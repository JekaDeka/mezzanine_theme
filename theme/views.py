from __future__ import unicode_literals
from future.builtins import str, int

from calendar import month_name
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (login as auth_login, authenticate,
                                 logout as auth_logout, get_user_model)
from django.contrib.auth.decorators import login_required

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.blog.feeds import PostsRSS, PostsAtom
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.core.models import SitePermission
from mezzanine.utils.views import paginate
from mezzanine.accounts import get_profile_form
from theme.forms import СustomBlogForm, ContactForm, MyProfileForm
from theme.models import MyProfile
from mezzanine.utils.email import send_verification_mail, send_approve_mail
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

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
    user = request.user
    if user.is_authenticated():
        if not user.is_staff:
            user.is_staff = True
            group = Group.objects.get(name='custom')
            siteperms = SitePermission.objects.create(user=user)
            siteperms.sites.add(2)
            user.groups.add(group)
            user.save()

    return redirect('/')

def true_index(request):
    return render(request, '_index.html')

def index(request):
    form = ContactForm
    # new logic!
    if request.method == 'POST':
        form = form(data=request.POST)
        if form.is_valid():
            return redirect('/')
        else:
            return redirect('/')
    context = {'form': form }
    return render(request, 'index.html', context)

@csrf_protect
@login_required
def profile_view(request, username,
                    template_name='admin/index.html',
                    form = MyProfileForm,
                    extra_context=None):
    try:
        u = User.objects.get(username=username)
        user = MyProfile.objects.get(user=u)
    except:
        user = None
    
    if not user:
        return TemplateResponse(request, template_name, {})
    if request.method == "POST":
        form = MyProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return TemplateResponse(request, template_name, {})
    else:
        form = MyProfileForm(instance=user)
    context = {
        'form': form,
        'profile_tab': True,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
