from __future__ import unicode_literals
from future.builtins import str, int

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (login as auth_login, authenticate,
                                 logout as auth_logout, get_user_model)
from django.contrib.auth.decorators import login_required
from django.db import transaction

from mezzanine.blog.models import BlogPost, BlogCategory
from cartridge.shop.models import Category

from profiles.models import UserProfile
from shops.models import UserShop, ShopProduct, ShopProductImage

from theme.forms import ContactForm, MessageForm, OrderMessageForm, BlogPostForm
from theme.models import SliderItem

from mezzanine.conf import settings
from mezzanine.generic.models import Keyword, AssignedKeyword
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView


from itertools import chain


User = get_user_model()


def get_keywords(request):
    data = list(Keyword.objects.values('title'))
    return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})



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
        shop__on_vacation=False, available=True).order_by('-date_added').prefetch_related('images')[:4]
    user_shops = UserShop.objects.filter(on_vacation=False)[:4]
    masters = UserProfile.objects.select_related('country', 'city', 'user')[:4]  # мастера

    blog_posts = BlogPost.objects.published(
        for_user=request.user).select_related(
            'user__profile',
            'user__profile',
            )[:8]
    recent_posts = blog_posts[:4]
    popular_posts = blog_posts[4:]
    comments = None
    slideshow = SliderItem.objects.all().only('href__id','href__slug', 'featured_image', 'short_description').select_related('href')

    context = {
        'slideshow':  slideshow,
        'best_products': best_products,
        'user_shops': user_shops,
        'masters': masters,
        'blog_posts': recent_posts,
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



@method_decorator(login_required, name='dispatch')
class BlogPostList(ListView):
    model = BlogPost
    template_name = "blog/blogpost_user_list.html"
    context_object_name = "blogpost_list"

    def get_queryset(self):
        return BlogPost.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        remain = self.request.user.profile.allow_blogpost_count - \
            len(context['object_list'])
        context['remain'] = remain
        return context


class BlogPostGlobalList(ListView):
    model = BlogPost
    template_name = "blog/blog_post_list.html"
    context_object_name = "blogpost_list"
    paginate_by = 10

    def get_queryset(self):
        qs = super(BlogPostGlobalList, self).get_queryset()
        qs = qs.filter(status=2).only(
            'id',
            'slug',
            'title',
            'status',
            'preview_content',
            'content',
            'allow_comments',
            'comments_count',
            'featured_image',
            'publish_date',
            'user__id',
            'user__username',
            'user__profile__id',
            'user__profile__first_name',
            'user__profile__last_name',
            ).select_related(
            "user__profile",
            ).prefetch_related(
                "keywords__keyword",
            )
        tag = self.kwargs.get('tag')
        if tag is not None:
            qs = qs.filter(keywords__keyword__slug=tag)

        category = self.kwargs.get('category')
        if category is not None:
            qs = qs.filter(categories__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super(BlogPostGlobalList, self).get_context_data(**kwargs)
        qs = BlogPost.objects.filter(status=2).only('id', 'slug', 'featured_image', 'comments_count', 'title', 'publish_date')
        context['recent_posts'] = qs.order_by('-publish_date')[:5]
        context['popular_posts'] = qs.order_by('-comments_count')[:5]


        tag = self.kwargs.get('tag')
        if tag:
            context['tag'] = Keyword.objects.values('title').get(slug=tag)

        category = self.kwargs.get('category')
        if category:
            context['category'] = BlogCategory.objects.values('title').get(slug=category)

        return context

class BlogPostGlobalDetailView(DetailView):
    model = BlogPost
    template_name = "blog/blog_post_detail.html"
    context_object_name = 'blog_post'

    def get_queryset(self):
        qs = super(BlogPostGlobalDetailView, self).get_queryset()
        qs = qs.only(
            'id',
            'slug',
            'title',
            'status',
            'description',
            '_meta_title',
            'content',
            'allow_comments',
            'comments_count',
            'featured_image',
            'publish_date',
            'user__id',
            'user__username',
            'user__profile__id',
            'user__profile__first_name',
            'user__profile__last_name',
            ).select_related(
            "user__profile",
            ).prefetch_related(
                "keywords__keyword",
            )
        tag = self.kwargs.get('tag')
        if tag is not None:
            qs = qs.filter(keywords__keyword__slug=tag)

        category = self.kwargs.get('category')
        if category is not None:
            qs = qs.filter(categories__slug=category)
        return qs

    def get_object(self, queryset=None):
        obj = super(BlogPostGlobalDetailView, self).get_object(queryset=queryset)
        if not self.request.user.is_superuser:
            if obj.status == 1 and obj.user != self.request.user:
                raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        context = super(BlogPostGlobalDetailView, self).get_context_data(**kwargs)
        qs = BlogPost.objects.filter(status=2).only('id', 'slug', 'featured_image', 'comments_count', 'title', 'publish_date')
        context['recent_posts'] = qs.order_by('-publish_date')[:5]
        context['popular_posts'] = qs.order_by('-comments_count')[:5]


        tag = self.kwargs.get('tag')
        if tag:
            context['tag'] = Keyword.objects.values('title').get(slug=tag)

        category = self.kwargs.get('category')
        if category:
            context['category'] = BlogCategory.objects.values('title').get(slug=category)

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
        instance.status = 1
        instance.save()
        messages.success(self.request, "Статья успешно добавлена в Блог.")
        return super(BlogPostCreate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class BlogPostUpdate(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy('blogpost-list')
    # fields = ['title', 'featured_image', 'preview_content', 'content', 'categories', 'allow_comments', 'keywords']

    def form_valid(self, form):
        # instance = form.save(commit=True)
        messages.success(self.request, "Запись успешно изменена")
        # return redirect(self.success_url)
        return super(BlogPostUpdate, self).form_valid(form)

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
