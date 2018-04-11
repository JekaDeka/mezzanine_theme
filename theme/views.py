from __future__ import unicode_literals
from future.builtins import str, int

from calendar import month_name
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.template.loader import get_template, render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (login as auth_login, authenticate,
                                 logout as auth_logout, get_user_model)
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.db import transaction

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.pages.models import Page
from cartridge.shop.models import Category, Product, ProductVariation
from cartridge.shop.utils import recalculate_cart, sign
from cartridge.shop.forms import AddProductForm

from profiles.models import UserProfile
# from ordertable.models import OrderTableItem, OrderTableItemCategory, OrderTableItemRequest
from shops.models import UserShop, UserShopDeliveryOption, ShopProduct, ShopProductImage

from theme.forms import ContactForm, MessageForm, OrderMessageForm, BlogPostForm

from mezzanine.blog.feeds import PostsRSS, PostsAtom
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword, AssignedKeyword
from mezzanine.utils.views import paginate
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.decorators import login_required


# from rest_framework import viewsets
# from .serializers import UserShopSerializer

import datetime
import re
import json
from itertools import chain
from PIL import Image


User = get_user_model()




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
    # main_category = Page.objects.get(slug='catalog')
    # categories = main_category.children.all()
    categories = Category.objects.filter(parent__slug='catalog')[:10]
    # enddate = datetime.datetime.today()
    # startdate = enddate - datetime.timedelta(days=60)
    # new_arrivals = Product.objects.filter(
    # created__range=[startdate,
    # enddate]).filter(status=2).order_by('-created')[:7]

    best_products = ShopProduct.objects.filter(
        shop__on_vacation=False).order_by('-date_added').prefetch_related('images')[:4]
    user_shops = UserShop.objects.filter(on_vacation=False)[:4]
    masters = UserProfile.objects.select_related('country', 'city')[:4] ### мастера

    blog_posts = BlogPost.objects.published(for_user=request.user).select_related('user')[:8]
    recent_posts = blog_posts[:4]
    popular_posts = blog_posts[4:]
    comments = None

    context = {
        'best_products': best_products,
        'user_shops': user_shops,
        'masters': masters,
        'blog_posts': blog_posts,
        'recent_posts': recent_posts,
        'popular_posts': popular_posts,
        'comments': comments,
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


# def shop_view(request, slug, template_name='accounts/shop_profile.html', extra_context=None):
#     try:
#         shop = UserShop.objects.get(slug=slug)
#     except Exception as e:
#         return HttpResponseRedirect(reverse('true_index'))
#     try:
#         profile = request.user.profile
#         data = {'first_name': profile.first_name,
#                 'email': request.user.email}
#     except Exception as e:
#         profile = None
#         data = None

#     form = MessageForm(data)
#     if request.method == 'POST':
#         form = MessageForm(data=request.POST)
#         if form.is_valid():
#             message = request.POST.get('message', '')
#             first_name = request.POST.get('first_name', '')
#             email = request.POST.get('email', '')
#             template = get_template('email/shop_message_send.html')
#             context = {
#                 'request': request,
#                 'shop': shop,
#                 'profile': profile,
#                 'first_name': first_name,
#                 'email': email,
#                 'message': message,
#             }
#             content = template.render(context)

#             email = EmailMessage(
#                 "Вашему магазину задали вопрос handmaker.top",
#                 content,
#                 settings.EMAIL_HOST_USER,
#                 [shop.user.email],
#                 headers={'Reply-To': email}
#             )
#             email.content_subtype = 'html'
#             email.send(fail_silently=True)
#             messages.success(request, "Ваше сообщение успешно отправлено")
#             return HttpResponseRedirect(reverse('shop_view', args=[shop.slug]))

#     context = {'shop': shop, "form": form}
#     if extra_context is not None:
#         context.update(extra_context)
#     return TemplateResponse(request, template_name, context)


# @login_required
# def shop_toggle_vacation(request):
#     try:
#         shop = request.user.shop
#         if shop.on_vacation:
#             shop.on_vacation = False
#             messages.success(
#                 request, "Ваш магазин успешно вернулся с каникул!")
#         else:
#             shop.on_vacation = True
#             messages.info(
#                 request, 'Ваш магазин теперь на каникулах и не принимает заказы.')
#         shop.save()
#     except Exception as e:
#         shop = None
#         messages.append('go')

#     if request.META['HTTP_REFERER']:
#         return HttpResponseRedirect(request.META['HTTP_REFERER'])
#     else:
#         return HttpResponseRedirect('/')


# @login_required
# def shop_create(request, template="accounts/account_shop_create.html"):
#     try:
#         shop = UserShop.objects.get(user=request.user)
#     except:
#         shop = None

#     if request.method == 'POST':
#         form = ShopForm(request.POST, request.FILES, instance=shop)
#         if form.is_valid():
#             if shop:
#                 messages.success(request, "Магазин успешно изменен.")
#             else:
#                 messages.success(request, "Магазин успешно создан.")

#             shop = form.save(commit=False)
#             shop.user = request.user
#             if request.FILES.get('image', False):
#                 shop.image = request.FILES['image']

#             if request.FILES.get('background', False):
#                 shop.background = request.FILES['background']
#             shop.save()

#             if not shop.user.groups.filter(name='custom').exists():
#                 shop.user.is_staff = True
#                 group = Group.objects.get(name='custom')
#                 shop.user.groups.add(group)
#                 shop.user.save()
#             return redirect('shop_view', slug=shop.slug)
#     else:
#         form = ShopForm(instance=shop)
#     templates = []
#     context = {"form": form, "shop": shop}
#     templates.append(template)
#     return TemplateResponse(request, templates, context)


# @login_required
# def profiles:profile-settings(request, template="accounts/account_profiles:profile-settings.html",
#                      extra_context=None):
#     """
#     Profile basic settings
#     """
#     user = request.user
#     try:
#         shop = UserShop.objects.get(user=user)
#     except:
#         shop = None
#     try:
#         profile = user.profile
#     except:
#         profile = None

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             profile = form.save(commit=False)
#             profile.user = user
#             first_time = False
#             if request.FILES.get('image', False):
#                 profile.image = request.FILES['image']

#             if not profile.user.groups.filter(name='blog_only').exists():
#                 profile.user.is_staff = True
#                 group = Group.objects.get(name='blog_only')
#                 profile.user.groups.add(group)
#                 profile.user.save()
#                 messages.success(request, "Профиль успешно обновлен.")
#                 first_time = True

#             profile.save()
#             html = render_to_string(
#                 'accounts/includes/card_profile.html', {'profile': profile, 'MEDIA_URL': settings.MEDIA_URL})
#             response_data = {}
#             response_data['first_time'] = first_time
#             response_data['result'] = 'success'
#             response_data['response'] = html
#             return HttpResponse(json.dumps(response_data), content_type="application/json")
#         else:
#             response_data = {}
#             response_data['errors'] = form.errors
#             response_data['result'] = 'error'
#             return HttpResponse(json.dumps(response_data), content_type="application/json")

#     else:
#         form = UserProfileForm(instance=profile)

#     context = {"shop": shop, "user": user,
#                "profile": profile, "form": form, "title": "Личный кабинет"}
#     context.update(extra_context or {})
#     return TemplateResponse(request, template, context)


# def validate_shopname(request):
#     shopname = request.GET.get('shopname', None)
#     data = {
#         'is_taken': UserShop.objects.filter(shopname__iexact=shopname).exclude(user=request.user).exists()
#     }
#     if data['is_taken']:
#         data['error_message'] = 'Магазин с таким именем уже существует.'

#     return JsonResponse(data)


def get_categories(request):
    def get_tree_data(node):
        level = 0
        data = list()

        def allChildren(self, l=None, level=0):
            if(l is None):
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
    return JsonResponse(tree, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def product(request, slug, template="shop/product.html",
            form_class=AddProductForm, extra_context=None):
    """
    Display a product - convert the product variations to JSON as well as
    handling adding the product to either the cart or the wishlist.
    """
    # published_products = Product.objects.published(for_user=request.user)
    product = Product.objects.select_related('shop').get(slug=slug)
    profile = UserProfile.objects.select_related('country', 'city').get(user=product.shop.user_id)
    # fields = [f.name for f in ProductVariation.option_fields()]
    # variations = product.variations.all()
    # variations_json = dumps([dict([(f, getattr(v, f))
    #                                for f in fields + ["sku", "image_id"]]) for v in variations])
    to_cart = (request.method == "POST" and
               request.POST.get("add_wishlist") is None)
    initial_data = {}
    # if variations:
    #     initial_data = dict([(f, getattr(variations[0], f)) for f in fields])
    initial_data["quantity"] = 1
    # add_product_form = form_class(request.POST or None, product=product,
    # initial=initial_data, to_cart=to_cart)
    # if request.method == "POST":
    #     if add_product_form.is_valid():
    #         if to_cart:
    #             quantity = add_product_form.cleaned_data["quantity"]
    #             request.cart.add_item(add_product_form.variation, quantity)
    #             recalculate_cart(request)
    #             info(request, _("Item added to cart"))
    #             return redirect("shop_cart")
    #         else:
    #             skus = request.wishlist
    #             sku = add_product_form.variation.sku
    #             if sku not in skus:
    #                 skus.append(sku)
    #             info(request, _("Item added to wishlist"))
    #             response = redirect("shop_wishlist")
    #             set_cookie(response, "wishlist", ",".join(skus))
    #             return response
    # related = []
    # if settings.SHOP_USE_RELATED_PRODUCTS:
    #     related = product.related_products.published(for_user=request.user)
    context = {
        "product": product,
        "profile": profile,
        # "editable_obj": product,
        # "images": product.images.all(),
        # "variations": variations,
        # "variations_json": variations_json,
        # "has_available_variations": any([v.has_price() for v in variations]),
        # "related_products": related,
        # "add_product_form": add_product_form
    }
    context.update(extra_context or {})
    return TemplateResponse(request, template, context)


@method_decorator(login_required, name='dispatch')
class BlogPostList(ListView):
    model = BlogPost
    template_name = "blog/blogpost_user_list.html"
    context_object_name = "blogpost_list"

    def get_queryset(self):
        return BlogPost.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        remain = self.request.user.profile.allow_blogpost_count - len(context['object_list'])
        context['remain'] = remain
        return context


@method_decorator(login_required, name='dispatch')
class BlogPostCreate(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    # fields = ['title', 'featured_image', 'preview_content', 'content', 'categories', 'allow_comments', 'keywords']
    success_url = reverse_lazy('blogpost-list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.blogposts.count() >= 10:
            messages.warning(self.request, "Исчерпан лимит")
            return redirect(self.success_url)
        return super(BlogPostCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        messages.success(self.request, "Статья успешно добавлена в Блог.")
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class BlogPostUpdate(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy('blogpost-list')
    # fields = ['title', 'featured_image', 'preview_content', 'content', 'categories', 'allow_comments', 'keywords']

    def form_valid(self, form):
        instance = form.save(commit=True)
        messages.success(self.request, "Запись успешно изменена")
        return redirect(self.success_url)

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(BlogPostUpdate, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj


@method_decorator(login_required, name='dispatch')
class BlogPostDelete(DeleteView):
    model = BlogPost
    success_url = reverse_lazy('blogpost-list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(BlogPostDelete, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj


# @method_decorator(login_required, name='dispatch')
# class ProductList(ListView):
#     model = ShopProduct
#     template_name = "product/product_user_list.html"
#     context_object_name = "product_list"

#     def get_queryset(self):
#         return ShopProduct.objects.filter(shop=self.request.user.shop).prefetch_related('images')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         remain = self.request.user.profile.allow_blogpost_count - len(context['object_list'])
#         context['remain'] = remain
#         return context


# @method_decorator(login_required, name='dispatch')
# class ProductCreate(CreateView):
#     model = ShopProduct
#     form_class = ProductForm
#     success_url = reverse_lazy('product-list')


# @method_decorator(login_required, name='dispatch')
# class ProductUpdate(UpdateView):
#     model = ShopProduct
#     form_class = ProductForm
#     success_url = reverse_lazy('product-list')
#     template_name = "product/product_form.html"
#     # fields = '__all__'


# @method_decorator(login_required, name='dispatch')
# class ProductDelete(DeleteView):
#     model = ShopProduct
#     success_url = reverse_lazy('product-list')
#     template_name = "product/product_confirm_delete.html"

#     def get_object(self, queryset=None):
#         obj = super(ProductDelete, self).get_object()
#         if not obj.shop == self.request.user.shop:
#             raise Http404
#         return obj


# @method_decorator(login_required, name='dispatch')
# class ProductImageCreate(CreateView):
#     """docstring for ProductImageCreate"""
#     model = ShopProduct
#     form_class = ProductForm
#     success_url = reverse_lazy('product-list')
#     template_name = "product/product_form.html"

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.shop.products.count() >= 10:
#             messages.warning(self.request, "Исчерпан лимит")
#             return redirect(self.success_url)
#         return super(ProductImageCreate, self).dispatch(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         data = super(ProductImageCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['productimage'] = ProductImageFormSet(self.request.POST)
#         else:
#             data['productimage'] = ProductImageFormSet()
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         productimage = context['productimage']
#         with transaction.atomic():
#             self.object = form.save(commit=False)
#             self.object.shop = self.request.user.shop
#             self.object.save()

#             if productimage.is_valid():
#                 productimage.instance = self.object
#                 productimage.save()
#         return super(ProductImageCreate, self).form_valid(form)


# @method_decorator(login_required, name='dispatch')
# class ProductImageUpdate(UpdateView):
#     model = ShopProduct
#     form_class = ProductForm
#     success_url = reverse_lazy('product-list')
#     template_name = "product/product_form.html"
#     queryset = ShopProduct.objects.select_related()

#     def get_context_data(self, **kwargs):
#         data = super(ProductImageUpdate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['productimage'] = ProductImageFormSet(self.request.POST, instance=self.object)
#         else:
#             data['productimage'] = ProductImageFormSet(instance=self.object)
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         productimage = context['productimage']
#         with transaction.atomic():
#             self.object = form.save(commit=False)
#             self.object.shop = self.request.user.shop
#             self.object.save()

#             if productimage.is_valid():
#                 productimage.instance = self.object
#                 productimage.save()
#         return super(ProductImageUpdate, self).form_valid(form)

#     def get_object(self, queryset=None):
#         """ Hook to ensure object is owned by request.user. """
#         obj = super(ProductImageUpdate, self).get_object()
#         if not obj.shop == self.request.user.shop:
#             raise Http404
#         return obj


# class ProductDetailView(DetailView):
#     model = ShopProduct
#     template_name = "shop/product.html"
#     context_object_name = 'product'
#     queryset = ShopProduct.objects.prefetch_related(
#         'keywords__keyword', 'images').select_related("shop__user__profile", "shop__user__profile__country", "shop__user__profile__city")


class SearchAll(ListView):
    template_name = "search_results.html"
    context_object_name = 'results'

    def get_queryset(self):
        query = Q()
        search = self.request.GET.get('q')
        words = search.split(" ")
        for word in words:
            query |= Q(keywords_string__icontains=word)
            query |= Q(title__icontains=word)
        products = ShopProduct.objects.filter(query).all()
        blog_post = BlogPost.objects.filter(query).all()
        shops = UserShop.objects.filter(shopname__in=words)

        result_list = list(chain(products, blog_post, shops))
        return result_list


# class ShopList(ListView):
#     model = UserShop
#     template_name = "shop/shop_list.html"


# class ShopCreate(CreateView):
#     model = UserShop
#     # form = ShopForm
#     fields = ["background", "image", "shopname", "bio", "rules",
#               "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other"]


# class ShopDeliveryOptionCreate(CreateView):
#     model = UserShop
#     fields = ["background", "image", "shopname", "bio", "rules",
#               "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other"]
#     success_url = reverse_lazy('profile-list')
#     template_name = "shop/shop_form.html"

#     def get_context_data(self, **kwargs):
#         data = super(ShopDeliveryOptionCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['deliveryoption'] = UserShopDeliveryOptionFormSet(self.request.POST)
#         else:
#             data['deliveryoption'] = UserShopDeliveryOptionFormSet()
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         deliveryoption = context['deliveryoption']
#         with transaction.atomic():
#             self.object = form.save()

#             if deliveryoption.is_valid():
#                 deliveryoption.instance = self.object
#                 deliveryoption.save()
#         return super(ShopDeliveryOptionCreate, self).form_valid(form)


# class ShopUpdate(UpdateView):
#     model = UserShop
#     success_url = '/'
#     fields = ["background", "image", "shopname", "bio", "rules",
#               "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other"]
#     template_name = "shop/shop_form.html"


# class ShopDeliveryOptionUpdate(UpdateView):
#     model = UserShop
#     fields = ["background", "image", "shopname", "bio", "rules",
#               "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other"]
#     success_url = reverse_lazy('shop-list')
#     template_name = "shop/shop_form.html"

#     def get_context_data(self, **kwargs):
#         data = super(ShopDeliveryOptionUpdate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['deliveryoption'] = UserShopDeliveryOptionFormSet(self.request.POST, instance=self.object)
#         else:
#             data['deliveryoption'] = UserShopDeliveryOptionFormSet(instance=self.object)
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         deliveryoption = context['deliveryoption']
#         with transaction.atomic():
#             self.object = form.save()

#             if deliveryoption.is_valid():
#                 deliveryoption.instance = self.object
#                 deliveryoption.save()
#         return super(ShopDeliveryOptionUpdate, self).form_valid(form)


# class ShopDelete(DeleteView):
#     model = UserShop
#     success_url = reverse_lazy('shop-list')


# class ShopDetailView(DetailView):
#     model = UserShop
#     template_name = "accounts/shop_profile.html"
#     context_object_name = 'shop'
#     queryset = UserShop.objects.prefetch_related('products', 'products__images')

#     def post(self, request, *args, **kwargs):
#         form = MessageForm(data=request.POST)
#         if form.is_valid():
#             message = request.POST.get('message', '')
#             first_name = request.POST.get('first_name', '')
#             email = request.POST.get('email', '')
#             template = get_template('email/shop_message_send.html')
#             context = {
#                 'request': request,
#                 'shop': self.get_object(),
#                 'profile': self.get_object().user.profile,
#                 'first_name': first_name,
#                 'email': email,
#                 'message': message,
#             }
#             content = template.render(context)

#             email = EmailMessage(
#                 "Вашему магазину задали вопрос handmaker.top",
#                 content,
#                 settings.EMAIL_HOST_USER,
#                 [self.get_object().user.email],
#                 headers={'Reply-To': email}
#             )
#             email.content_subtype = 'html'
#             email.send(fail_silently=True)
#             messages.success(request, "Ваше сообщение успешно отправлено")
#         else:
#             messages.error(request, "Проверьте правильность введенных данных")
#         return HttpResponseRedirect(self.get_object().get_absolute_url())

#     def get_context_data(self, **kwargs):
#         data = super(ShopDetailView, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['form'] = MessageForm(self.request.POST)
#         else:
#             data['form'] = MessageForm()
#         return data
#     # def get_queryset(self):
#     # return UserShop.objects.prefetch_related('products')
#     # queryset = UserShop.objects.prefetch_related(
#     # 'keywords__keyword').select_related("shop__user__profile", "shop__user__profile__country", "shop__user__profile__city")
