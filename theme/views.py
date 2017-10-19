from __future__ import unicode_literals
from future.builtins import str, int

from calendar import month_name
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context
from django.template.response import TemplateResponse
from django.template.loader import get_template, render_to_string
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (login as auth_login, authenticate,
                                 logout as auth_logout, get_user_model)
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.db.models import Count
from django.db import IntegrityError

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.pages.models import Page
from cartridge.shop.models import Category, Product
from theme.models import OrderItem, OrderItemCategory, OrderItemRequest, UserShop, UserProfile
from theme.utils import AuthorIsRequested
from mezzanine.blog.feeds import PostsRSS, PostsAtom
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.core.models import SitePermission
from mezzanine.utils.views import paginate
from mezzanine.accounts import get_profile_form
from theme.forms import СustomBlogForm, ContactForm, ShopForm, MessageForm, OrderMessageForm, UserProfileForm
from mezzanine.utils.email import send_verification_mail, send_approve_mail
from mezzanine.utils.urls import login_redirect, next_url
from mezzanine.accounts.forms import LoginForm, PasswordResetForm
from django.contrib.auth.models import Group
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.views.generic.detail import BaseDetailView
from django.contrib.auth.decorators import login_required
# from django.contrib.messages import info, error
# from mezzanine.utils.urls import login_redirect, next_url
import datetime
import json
from PIL import Image


User = get_user_model()


def blog_post_list(request, tag=None, year=None, month=None, username=None,
                   category=None, template="blog/blog_post_list.html",
                   extra_context=None):
    """
    Display a list of blog posts that are filtered by tag, year, month,
    author or category. Custom templates are checked for using the name
    ``blog/blog_post_list_XXX.html`` where ``XXX`` is either the
    category slug or author's username if given.
    """
    templates = []
    blog_posts = BlogPost.objects.published(for_user=request.user)
    blog_categories = BlogCategory.objects.all()

    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        blog_posts = blog_posts.filter(keywords__keyword=tag)
    if year is not None:
        blog_posts = blog_posts.filter(publish_date__year=year)
        if month is not None:
            blog_posts = blog_posts.filter(publish_date__month=month)
            try:
                month = _(month_name[int(month)])
            except IndexError:
                raise Http404()
    if category is not None:
        category = get_object_or_404(BlogCategory, slug=category)
        blog_posts = blog_posts.filter(categories=category)
        templates.append(u"blog/blog_post_list_%s.html" %
                         str(category.slug))
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        blog_posts = blog_posts.filter(user=author)
        templates.append(u"blog/blog_post_list_%s.html" % username)

    prefetch = ("categories", "keywords__keyword")
    blog_posts = blog_posts.select_related("user").prefetch_related(*prefetch)
    blog_posts = paginate(blog_posts, request.GET.get("page", 1),
                          settings.BLOG_POST_PER_PAGE,
                          settings.MAX_PAGING_LINKS)
    context = {"blog_posts": blog_posts, "year": year, "month": month,
               "tag": tag, "category": category, "author": author, "blog_categories": blog_categories}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def blog_post_detail(request, slug, year=None, month=None, day=None,
                     template="blog/blog_post_detail.html",
                     extra_context=None):
    """. Custom templates are checked for using the name
    ``blog/blog_post_detail_XXX.html`` where ``XXX`` is the blog
    posts's slug.
    """
    blog_posts = BlogPost.objects.published(
        for_user=request.user).select_related()
    blog_post = get_object_or_404(blog_posts, slug=slug)
    related_posts = blog_post.related_posts.published(for_user=request.user)
    context = {"blog_post": blog_post, "editable_obj": blog_post,
               "related_posts": related_posts}
    context.update(extra_context or {})
    templates = [u"blog/blog_post_detail_%s.html" % str(slug), template]
    return TemplateResponse(request, templates, context)


def blog_post_feed(request, format, **kwargs):
    """
    Blog posts feeds - maps format to the correct feed view.
    """
    try:
        return {"rss": PostsRSS, "atom": PostsAtom}[format](**kwargs)(request)
    except KeyError:
        raise Http404()


# def promote_user(request, template="accounts/account_signup.html",
#                  extra_context=None):
#     # user = request.user
#     # if user.is_authenticated():
#         # if not user.is_staff:
#         #     user.is_staff = True
#         #     group = Group.objects.get(name='custom')
#         #     siteperms = SitePermission.objects.create(user=user)
#         #     siteperms.sites.add(settings.SITE_ID)
#         #     user.groups.add(group)
#         #     user.save()
#         #     user.userprofile.save()

#     return redirect('/')

def true_index(request):
    main_category = Page.objects.get(slug='catalog')
    # categories = main_category.children.all()
    categories = Category.objects.filter(parent=main_category)[:10]
    # enddate = datetime.datetime.today()
    # startdate = enddate - datetime.timedelta(days=60)
    # new_arrivals = Product.objects.filter(
    # created__range=[startdate,
    # enddate]).filter(status=2).order_by('-created')[:7]

    featured_products = Product.objects.filter(
        user__shop__on_vacation=False).order_by('-created')[:10]

    # recent_posts = BlogPost.objects.order_by('-created')[:4]
    tmp = User.objects.distinct().annotate(
        product_num=Count('product')).filter(product_num__gt=3)

    user_shops = UserShop.objects.filter(
        user__in=tmp).filter(on_vacation=False)
    context = {
        'featured_products': featured_products,
        'user_shops': user_shops,
        'categories': categories,
    }
    return render(request, '_index.html', context)


def index(request):
    form = ContactForm
    # new logic!
    if request.method == 'POST':
        form = form(data=request.POST)
        if form.is_valid():
            return redirect('/')
        else:
            return redirect('/')
    context = {'form': form}
    return render(request, 'index.html', context)


@csrf_protect
@login_required
def profile_view(request, template_name='admin/index.html',
                 extra_context=None):
    # user = UserProfile.objects.get(user=request.user)
    # if not user:
    #     return TemplateResponse(request, template_name, {})
    # if request.method == "POST":
    #     form = ShopForm(request.POST, instance=user)
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         user.save()
    #         return TemplateResponse(request, template_name, {})
    # else:
    #     form = ShopForm(instance=user)
    context = {
        # 'form': form,
        # 'profile_tab': True,
    }
    # if extra_context is not None:
    #     context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def shop_view(request, slug, template_name='accounts/shop_profile.html', extra_context=None):
    try:
        shop = UserShop.objects.get(slug=slug)
    except Exception as e:
        return HttpResponseRedirect(reverse('true_index'))
    try:
        profile = request.user.profile
        data = {'first_name': profile.first_name,
                'email': request.user.email}
    except Exception as e:
        profile = None
        data = None

    form = MessageForm(data)
    if request.method == 'POST':
        form = MessageForm(data=request.POST)
        if form.is_valid():
            message = request.POST.get('message', '')
            first_name = request.POST.get('first_name', '')
            email = request.POST.get('email', '')
            template = get_template('email/message_send.html')
            context = Context({
                'request': request,
                'shop': shop,
                'profile': profile,
                'first_name': first_name,
                'email': email,
                'message': message,
            })
            content = template.render(context)

            email = EmailMessage(
                "Вашему магазину задали вопрос handmaker.top",
                content,
                settings.EMAIL_HOST_USER,
                [shop.user.email],
                headers={'Reply-To': email}
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
            messages.success(request, "Ваше сообщение успешно отправлено")
            return HttpResponseRedirect(reverse('shop_view', args=[shop.slug]))

    context = {'shop': shop, "form": form}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


@login_required
def shop_toggle_vacation(request):
    try:
        shop = request.user.shop
        if shop.on_vacation:
            shop.on_vacation = False
            messages.success(
                request, "Ваш магазин успешно вернулся с каникул!")
        else:
            shop.on_vacation = True
            messages.info(
                request, 'Ваш магазин теперь на каникулах и не принимает заказы.')
        shop.save()
    except Exception as e:
        shop = None
        messages.append('go')

    if request.META['HTTP_REFERER']:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')


@login_required
def shop_create(request, template="accounts/account_shop_create.html"):
    try:
        shop = UserShop.objects.get(user=request.user)
    except:
        shop = None

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            if shop:
                messages.success(request, "Магазин успешно изменен.")
            else:
                messages.success(request, "Магазин успешно создан.")

            shop = form.save(commit=False)
            shop.user = request.user
            if request.FILES.get('image', False):
                shop.image = request.FILES['image']

            if request.FILES.get('background', False):
                shop.background = request.FILES['background']
            shop.save()

            if not shop.user.groups.filter(name='custom').exists():
                shop.user.is_staff = True
                group = Group.objects.get(name='custom')
                shop.user.groups.add(group)
                shop.user.save()
            return redirect('shop_view', slug=shop.slug)
    else:
        form = ShopForm(instance=shop)
    templates = []
    context = {"form": form, "shop": shop}
    templates.append(template)
    return TemplateResponse(request, templates, context)


@login_required
def profile_settings(request, template="accounts/account_profile_settings.html",
                     extra_context=None):
    """
    Profile basic settings
    """
    user = request.user
    try:
        shop = UserShop.objects.get(user=user)
    except:
        shop = None
    try:
        profile = user.profile
    except:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            first_time = False
            if request.FILES.get('image', False):
                profile.image = request.FILES['image']

            if not profile.user.groups.filter(name='blog_only').exists():
                profile.user.is_staff = True
                group = Group.objects.get(name='blog_only')
                profile.user.groups.add(group)
                profile.user.save()
                messages.success(request, "Профиль успешно обновлен.")
                first_time = True

            profile.save()
            html = render_to_string(
                'accounts/includes/card_profile.html', {'profile': profile, 'MEDIA_URL': settings.MEDIA_URL})
            response_data = {}
            response_data['first_time'] = first_time
            response_data['result'] = 'success'
            response_data['response'] = html
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data = {}
            response_data['errors'] = form.errors
            response_data['result'] = 'error'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    else:
        form = UserProfileForm(instance=profile)

    context = {"shop": shop, "user": user,
               "profile": profile, "form": form, "title": "Личный кабинет"}
    context.update(extra_context or {})
    return TemplateResponse(request, template, context)


def order_list(request, tag=None, year=None, month=None, username=None,
               category=None, template="order/order_list.html",
               extra_context=None):

    templates = []
    orders = OrderItem.objects.filter(performer=None)
    author = request.user
    order_categories = OrderItemCategory.objects.all()
    if category is not None:
        category = get_object_or_404(OrderItemCategory, slug=category)
        orders = orders.filter(categories=category)

    orders = paginate(orders, request.GET.get("page", 1),
                      15,
                      settings.MAX_PAGING_LINKS)
    context = {"orders": orders, "year": year, "month": month,
               "tag": tag, "category": category, "author": author, "order_categories": order_categories}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def order_detail(request, pk, template="order/order_detail.html",
                 extra_context=None):
    templates = []
    try:
        order = OrderItem.objects.get(pk=pk)
    except Exception as e:
        return redirect('order_list')

    form = OrderMessageForm()
    if request.method == 'POST':
        form = OrderMessageForm(data=request.POST)
        if form.is_valid():
            # message = request.POST.get('message', '')
            # template = get_template('order/order_email_request_approved.html')
            # context = Context({
            #     'request': request,
            #     'order': order,
            #     'performer': request.user,
            #     'message': message,
            # })
            # content = template.render(context)

            # email = EmailMessage(
            #     "Для вашего заказа нашелся исполнитель handmaker.top",
            #     content,
            #     settings.EMAIL_HOST_USER,
            #     [order.author.email],
            #     headers={'Reply-To': request.user.email}
            # )
            # email.content_subtype = 'html'
            # email.send(fail_silently=True)
            order_request_add(request, pk)
            return HttpResponseRedirect(reverse('order_detail', args=[pk]))

    context = {"order": order, "form": form}

    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def order_request_add(request, order_pk):
    try:
        order = OrderItem.objects.get(pk=order_pk, performer=None)
        if request.user == order.author:
            raise ValueError('Нельзя откликнуться на собственную заявку')
        orderRequest = OrderItemRequest(order=order, performer=request.user)
        orderRequest.save()
    except Exception as error:
        if 'UNIQUE constraint' in error.args[0]:
            messages.error(request, 'Вы уже откликнулись на данный заказ')
        elif 'matching query does not exist' in error.args[0]:
            order = OrderItem.objects.get(pk=order_pk)
            order.active = False
            order.save()
            messages.error(request, 'Данная заявка закрыта')
        else:
            messages.error(request, error.args[0])

    else:
        messages.success(
            request, "Ваше сообщение успешно отправлено. Автор данный заявки свяжется с вами по мере своих возможностей.")
    # return HttpResponseRedirect(reverse('order_detail', args=[order_pk]))
    # return render(request, 'order/order_request_approved.html', {'order':
    # order})


@login_required
def order_request_assign(request, order_pk, performer_pk, extra_context=None):
    if request.user.has_perm('theme.change_orderitemrequest'):
        try:
            order = OrderItem.objects.get(pk=order_pk)
            performer = User.objects.get(pk=performer_pk)
            order.performer = performer
            order.active = False
            order.save()
        except Exception as e:
            messages.success(
                request, e.args[0])
        else:
            template = get_template('order/order_email_request_assign.html')
            context = Context({
                'request': request,
                'order': order,
                'performer': performer,
            })
            content = template.render(context)

            email = EmailMessage(
                "Ваша заявка на исполнение заказа одобрена handmaker.top",
                content,
                settings.EMAIL_HOST_USER,
                [order.author.email],
                headers={'Reply-To': performer.email}
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
            messages.success(
                request, "Исполнитель успешно назначен. Ему отправлено уведомление.")

    return HttpResponseRedirect(reverse('admin:theme_orderitemrequest_changelist'))


@login_required
def order_request_delete(request, order_pk, performer_pk, extra_context=None):
    if request.user.has_perm('theme.change_orderitemrequest'):
        try:
            order = OrderItemRequest.objects.get(
                order=order_pk, performer=performer_pk)
            order.delete()
        except Exception as e:
            raise

    return HttpResponseRedirect(reverse('admin:theme_orderitemrequest_changelist'))


def validate_shopname(request):
    shopname = request.GET.get('shopname', None)
    data = {
        'is_taken': UserShop.objects.filter(shopname__iexact=shopname).exclude(user=request.user).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Магазин с таким именем уже существует.'

    return JsonResponse(data)


def get_categories(request):
    def get_tree_data(node):
        level = 0
        data = list()

        def allChildren(self, l=None, level=0):
            if(l == None):
                l = list()
            # if level != 0:
            l.append(
                tuple((self.parent.id if self.parent else None, self.title, self.id)))
            level += 1
            for child in self.children.all():
                l = allChildren(child, l, level)
            return l
        data = allChildren(node, data)
        return data

    data = get_tree_data(Category.objects.filter(parent=None)[0])
    # print(data)
    links = data
    # parents, children, ids = zip(*links)
    # print(parents)
    # print("------")
    # print(children)
    # root_nodes = {x for x in parents if x not in children}
    # for node in root_nodes:
    #     links.append(('Root', node))

    def get_nodes(node):
        d = {}
        d['parent'] = node[0]
        d['title'] = node[1]
        d['id'] = node[2]
        children = get_children(node)
        if children:
            d['children'] = [get_nodes(child) for child in children]
        return d

    def get_children(node):
        # print("node:__", node)
        # for x in links:
        #     print(x)
        return [x for x in links if x[0] == node[2]]

    tree = get_nodes(data[0])
    # return HttpResponse(json.dumps(tree, ensure_ascii=False, indent=4),
    # content_type="application/json")
    return JsonResponse(tree, safe=False,  json_dumps_params={'ensure_ascii': False, 'indent': 4})


# class UserList(generic.ListView):
#     model = UserProfile
#     template_name = 'accounts/account_profile_settings.html'


# class UserEdit(generic.UpdateView):
#     model = UserProfile
#     fields = '__all__'

#     def get_context_data(self, **context):
#         if 'edit' in self.request.GET:
#             context['edit'] = True
#         return super(UserEdit, self).get_context_data(**context)

#     def get_template_names(self):
#         if self.request.is_ajax():
#             return 'accounts/includes/form.html'
#         return 'accounts/account_profile_settings.html'

#     def get_object(self, queryset=None):
#         return self.request.user.profile

#     def get_success_url(self):
#         return reverse('profile_settings')
