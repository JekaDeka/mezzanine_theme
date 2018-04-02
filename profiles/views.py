from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404
from django.db import transaction
from django.shortcuts import redirect

from profiles.models import UserProfile
from profiles.forms import UserProfileForm


from mezzanine.utils.views import paginate
from mezzanine.conf import settings


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

    # def get_context_data(self, **kwargs):
    #     data = super(ProfileSettings, self).get_context_data(**kwargs)
    #     user = User.objects.values('shop__id', 'shop__slug', 'profile__first_name', 'email').get(pk=self.request.user.pk)
    #     data['user'] = user
    #     return data

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
            return redirect(reverse_lazy('profile-update', args=[request.user.pk]))

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


class ProfileDetailView(DetailView):
    model = User
    slug_field = 'username'
    template_name = "profiles/profile_detail.html"
    queryset = User.objects.select_related(
        "profile",
        "profile__country",
        "profile__city")

    def get_object(self, queryset=None):
        obj = super(ProfileDetailView, self).get_object(queryset=queryset)
        try:
            profile = obj.profile
        except Exception as e:
            raise Http404
        return obj


    # def get_context_data(self, **kwargs):
    #     context = super(ProfileDetailView, self).get_context_data(**kwargs)
    #     return context

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
