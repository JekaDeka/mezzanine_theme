from __future__ import unicode_literals
from future.builtins import str, int

from calendar import month_name
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (login as auth_login, authenticate,
                                 logout as auth_logout, get_user_model)
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.pages.models import Page
from cartridge.shop.models import Category, Product
from theme.models import OrderItem, OrderItemCategory
from mezzanine.blog.feeds import PostsRSS, PostsAtom
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.core.models import SitePermission
from mezzanine.utils.views import paginate
from mezzanine.accounts import get_profile_form
from theme.forms import СustomBlogForm, ContactForm, ShopForm
from theme.models import UserShop
from theme.utils import grouped
from mezzanine.utils.email import send_verification_mail, send_approve_mail
from mezzanine.utils.urls import login_redirect, next_url
from mezzanine.accounts.forms import LoginForm, PasswordResetForm
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from django.views.generic.detail import BaseDetailView
from django.contrib.auth.decorators import login_required
from django.contrib.messages import info, error
from mezzanine.utils.urls import login_redirect, next_url
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


def promote_user(request, template="accounts/account_signup.html",
                 extra_context=None):
    # user = request.user
    # if user.is_authenticated():
    #     if not user.is_staff:
    #         user.is_staff = True
    #         group = Group.objects.get(name='custom')
    #         siteperms = SitePermission.objects.create(user=user)
    #         siteperms.sites.add(settings.SITE_ID)
    #         user.groups.add(group)
    #         user.save()
    #         user.userprofile.save()

    return redirect('/')


def true_index(request):
    main_category = Page.objects.filter(slug='catalog')
    featured = Category.objects.filter(parent=main_category)[:4]

    # enddate = datetime.datetime.today()
    # startdate = enddate - datetime.timedelta(days=60)
    # new_arrivals = Product.objects.filter(
    # created__range=[startdate,
    # enddate]).filter(status=2).order_by('-created')[:7]

    new_arrivals = Product.objects.filter(status=2).order_by('-created')[:7]

    recent_posts = BlogPost.objects.order_by('-created')[:4]

    most_popular = new_arrivals[:3]
    user_shops = UserShop.objects.all()[:3]
    sale_product = new_arrivals[3:6]

    context = {'featured': featured,
               'new_arrivals': new_arrivals,
               'recent_posts': recent_posts,
               'most_popular': most_popular,
               'user_shops': user_shops,
               'sale_product': sale_product
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
    # lookup = {"slug__iexact": slug}
    # shop = get_object_or_404(UserShop, slug=slug)
    # user = get_object_or_404(User, usershop=shop)
    shop = UserShop.objects.get(slug=slug)
    user = User.objects.get(usershop=shop)
    context = {'shop': shop, 'user': user}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


@login_required
def shop_create(request, template="accounts/account_shop_create.html"):
    try:
        shop = UserShop.objects.get(user=request.user)
        form = ShopForm(request.POST or None, instance=shop)
    except:
        shop = None
        form = ShopForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        # form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.user = request.user
            if request.FILES.get('image', False):
                shop.image = request.FILES['image']

            if request.FILES.get('background', False):
                shop.background = request.FILES['background']
            shop.save()

            if not shop.user.is_staff:
                shop.user.is_staff = True
                group = Group.objects.get(name='custom')
                siteperms = SitePermission.objects.create(user=shop.user)
                siteperms.sites.add(settings.SITE_ID)
                shop.user.groups.add(group)
                shop.user.save()  # save staff status and permissions

            return redirect('shop_view', slug=shop.slug)

        return redirect('shop_create')

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
        return redirect('shop_create')

    # if request.method == "POST":
    #     form = SmallProfileForm(request.POST, instance=user)
    #     if form.is_valid():
    #         profile = form.save(commit=False)
    #         profile.user = auth_user
    #         profile.save()

    #         if not auth_user.is_staff:
    #             auth_user.is_staff = True
    #             group = Group.objects.get(name='custom')
    #             siteperms = SitePermission.objects.create(user=auth_user)
    #             siteperms.sites.add(settings.SITE_ID)
    #             auth_user.groups.add(group)
    #             auth_user.save()  # save staff status and permissions

    #     return TemplateResponse(request, template, {"form": form, "title":
    #                                                 _("Update Profile")})

    context = {"shop": shop, "user": user, "title": _("Мой профиль")}
    context.update(extra_context or {})
    return TemplateResponse(request, template, context)


def order_list(request, tag=None, year=None, month=None, username=None,
               category=None, template="order/order_list.html",
               extra_context=None):

    templates = []
    orders = OrderItem.objects.all()
    if category is not None:
        pass
    author = request.user
    order_categories = OrderItemCategory.objects.all()
    if category is not None:
        category = get_object_or_404(OrderItemCategory, slug=category)
        orders = orders.filter(categories=category)

    orders = paginate(orders, request.GET.get("page", 1),
                      settings.BLOG_POST_PER_PAGE,
                      settings.MAX_PAGING_LINKS)
    context = {"orders": orders, "year": year, "month": month,
               "tag": tag, "category": category, "author": author, "order_categories": order_categories}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def order_detail(request, pk, template="order/order_detail.html",
                 extra_context=None):
    templates = []
    order = get_object_or_404(OrderItem, pk=pk)
    context = {"order": order}

    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


# class SignUpView(CreateView):
#     template_name = 'accounts/account_shop_create.html'
#     form_class = ShopForm


def validate_shopname(request):
    shopname = request.GET.get('shopname', None)
    data = {
        'is_taken': UserShop.objects.filter(shopname__iexact=shopname).exists()
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
