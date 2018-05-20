from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core import paginator
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import redirect

from profiles.models import UserProfile
from profiles.forms import UserProfileForm

from shops.models import Order

from mezzanine.utils.views import paginate
from mezzanine.conf import settings

###
import pymorphy2


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Пароль успешно изменен!')
            return redirect('change_fck_password')
        else:
            messages.error(request, 'Ошибка')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profiles/change_password.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileSettings(TemplateView):
    template_name = "profiles/profile_settings.html"
    # model = User
    #
    # def get_queryset(self):
    #     return User.objects.filter(pk=self.request.user.pk).values('shop__id', 'profile__first_name')

    def get_context_data(self, **kwargs):
        data = super(ProfileSettings, self).get_context_data(**kwargs)
        # user = User.objects.values('shop__id', 'shop__slug', 'profile__first_name', 'email').get(pk=self.request.user.pk)
        user = User.objects.defer(
            'password',
            'last_login',
            'first_name',
            'last_name',
            'date_joined',
            'shop__background',
            'shop__image',
            'profile__background',
            'profile__bio'
        ).select_related(
            "shop",
            "profile",
            "profile__country",
            "profile__city").get(pk=self.request.user.pk)
        data['user'] = user

        if user.profile.status == 1:
            ### if user is master ###
            pass
            # reviews = MasterReview.objects.filter(master=self.request.user).values_list(
            #     'mastery', 'punctuality', 'responsibility', 'avg_rating')
            # data['reviews'] = reviews.aggregate(mastery=Avg('mastery'), punctuality=Avg(
            #     'punctuality'), responsibility=Avg('responsibility'), avg_rating=Avg('avg_rating'))
            # data['reviews_count'] = reviews.count()

        ### get shop data
        try:
            shop = user.shop
            orders = Order.objects.filter(shop=shop).values('status')
            orders_status_count = orders.order_by(
                'status').annotate(total=Count('status'))
            orders_data = dict()

            morph = pymorphy2.MorphAnalyzer()
            for key, value in settings.SHOP_ORDER_STATUS_CHOICES:
                label = morph.parse(value)[0]
                if key != 2:
                    label = label.inflect({'gent', 'plur'})
                orders_data[key] = {'label': label.word, 'total': 0 }

            for order in orders_status_count:
                orders_data[order['status']]['total'] = order['total']
            data['orders'] = orders_data
            data['orders_count'] = orders.count()
        except Exception as e:
            pass


        ### get order table data
        try:
            ordertableitems = user.orders_as_author.values('pk', 'created', 'title')
            ordertablitems_count = ordertableitems.count()
            data['ordertablitems'] = ordertableitems[:5]
            data['ordertablitems_count'] = ordertablitems_count
            data['ordertablitems_remain'] = user.profile.allow_ordertable_count - ordertablitems_count
        except Exception as e:
            pass

        ### get blog_post data
        try:
            blogposts = user.blogposts.all()
            blogposts_count = blogposts.count()
            data['blogposts'] = blogposts[:5]
            data['blogposts_count'] = blogposts_count
            data['blogposts_remain'] = user.profile.allow_blogpost_count - blogposts_count

            pass
        except Exception as e:
            raise

        return data

    def dispatch(self, request, *args, **kwargs):
        try:
            profile = request.user.profile
        except Exception as e:
            return redirect(reverse_lazy('profile-add'))

        return super(ProfileSettings, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProfileList(ListView):
    model = UserProfile
    # template_name = "orders/ordertableitem_user_list.html"
    # context_object_name = "ordertableitem_list"

    # def get_queryset(self):
    #     return OrderTableItem.objects.filter(author=self.request.user).prefetch_related('images')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     remain = self.request.user.profile.allow_blogpost_count - len(context['object_list'])
    #     context['remain'] = remain
    #     return context


@method_decorator(login_required, name='dispatch')
class ProfileCreate(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    success_url = reverse_lazy('profile-settings')
    template_name = "profiles/userprofile_create.html"
    success_message = "Профиль успешно создан"

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            messages.success(self.request, self.success_message)
        return super(ProfileCreate, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        try:
            profile = request.user.profile
        except Exception as e:
            pass
        else:
            return redirect(reverse_lazy('profile-update'))

        return super(ProfileCreate, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    success_url = reverse_lazy('profile-settings')
    # template_name = "profiles/userprofile_create.html"
    success_message = "Профиль успешно обновлен"

    def get_object(self, queryset=None):
        return UserProfile.objects.get(user=self.request.user)
        # """ Hook to ensure object is owned by request.user. """
        # obj = super(ProfileUpdate, self).get_object(queryset=queryset)
        # if obj.user != self.request.user:
        #     raise Http404
        # return obj

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(ProfileUpdate, self).form_valid(form)


@login_required
def profile_status_toggle(request):
    try:
        profile = request.user.profile
        if profile.status == 0:
            profile.status = 1
            messages.success(
                request, 'Вы успешно стали мастером.')
        profile.save()
    except Exception as e:
        messages.error(
            request, e)

    if request.META['HTTP_REFERER']:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')


class ProfileDetailView(DetailView):
    model = User
    slug_field = 'username'
    template_name = "profiles/profile_detail.html"
    queryset = User.objects.select_related(
        "profile",
        "profile__country",
        "profile__city").prefetch_related('master_reviews', 'blogposts', 'blogposts__keywords')

    def get_object(self, queryset=None):
        obj = super(ProfileDetailView, self).get_object(queryset=queryset)
        try:
            profile = obj.profile
        except Exception as e:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        reviews = self.queryset.filter(pk=self.object.pk).values(
            'master_reviews__mastery',
            'master_reviews__punctuality',
            'master_reviews__responsibility',
            'master_reviews__avg_rating'
        ).aggregate(
            Avg('master_reviews__mastery'),
            Avg('master_reviews__punctuality'),
            Avg('master_reviews__responsibility'),
            Avg('master_reviews__avg_rating'),
            Count('master_reviews')
        )

        context["reviews"] = reviews
        return context

    # def get_queryset(self):
    #     return User.objects.filter(username=self.slug)

    # template_name = "shop/product.html"
    # context_object_name = 'product'
    # queryset = ShopProduct.objects.prefetch_related(
    #     'keywords__keyword', 'images').select_related("shop__user__profile", "shop__user__profile__country", "shop__user__profile__city")


# @login_required
# def profiles:profile-settings(request, template="accounts/account_profiles:profile-settings.html",
#                      extra_context=None):
    """
    Profile basic settings
    """
    # user = request.user
    # try:
    #     shop = UserShop.objects.get(user=user)
    # except:
    #     shop = None
    # try:
    #     profile = user.profile
    # except:
    #     profile = None

    # if request.method == 'POST':
    #     form = UserProfileForm(request.POST, request.FILES, instance=profile)
    #     if form.is_valid():
    #         profile = form.save(commit=False)
    #         profile.user = user
    #         first_time = False
    #         if request.FILES.get('image', False):
    #             profile.image = request.FILES['image']

    #         if not profile.user.groups.filter(name='blog_only').exists():
    #             profile.user.is_staff = True
    #             group = Group.objects.get(name='blog_only')
    #             profile.user.groups.add(group)
    #             profile.user.save()
    #             messages.success(request, "Профиль успешно обновлен.")
    #             first_time = True

    #         profile.save()
    #         html = render_to_string(
    #             'accounts/includes/card_profile.html', {'profile': profile, 'MEDIA_URL': settings.MEDIA_URL})
    #         response_data = {}
    #         response_data['first_time'] = first_time
    #         response_data['result'] = 'success'
    #         response_data['response'] = html
    #         return HttpResponse(json.dumps(response_data), content_type="application/json")
    #     else:
    #         response_data = {}
    #         response_data['errors'] = form.errors
    #         response_data['result'] = 'error'
    #         return HttpResponse(json.dumps(response_data), content_type="application/json")

    # else:
    #     form = UserProfileForm(instance=profile)

    # context = {"shop": shop, "user": user,
    #            "profile": profile, "form": form, "title": "Личный кабинет"}
    # context.update(extra_context or {})
    # return TemplateResponse(request, template, context)
