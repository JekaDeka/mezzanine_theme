from copy import deepcopy
from django.contrib import admin
from django.db import models
# from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from mezzanine.forms.admin import FormAdmin
from mezzanine.blog.models import BlogPost
from cartridge.shop.models import Product
from cartridge.shop.admin import ProductAdmin
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from theme.models import Slider, SliderItem

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
# blog_fieldsets[0][1]["fields"].insert(-2, "preview_content")

product_fieldsets = deepcopy(ProductAdmin.fieldsets)
# product_fieldsets[0][1]["fields"] += ("material",)
# product_fieldsets[0][1]["fields"] += ("condition",)
# product_fieldsets[0][1]["fields"] += ("pre_order",)

class MyBlogPostAdmin(BlogPostAdmin):
    fieldsets = blog_fieldsets
    fieldsets.remove(fieldsets[1])
    list_per_page = 30
    fieldsets[0][1]['fields'] = ['title', 'status', 
                            # ('publish_date', 'expiry_date'), 
    'featured_image', 
    'preview_content', 'content', 'categories', 'allow_comments']

    fieldsets[1][1]['fields'].pop()
    def get_queryset(self, request):
        qs = super(MyBlogPostAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user)
    # def __init__(self, *args, **kwargs):
    #     super(MyBlogPostAdmin, self).__init__(*args, **kwargs)


class MyProductAdmin(ProductAdmin):
    fieldsets = product_fieldsets
    list_per_page = 30
    fieldsets[0][1]['fields'] = ['title', 'pre_order',  
    'status',
    # ('publish_date', 'expiry_date'), 
    'material', 'condition',
    'categories', 'content']

    def get_queryset(self, request):
        qs = super(MyProductAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user_id = request.user
        super(MyProductAdmin, self).save_model(request, obj, form, change)


class ItemInline(admin.StackedInline):
    model = SliderItem
    # fieldsets = (
    #     (None, {'fields': (('image', 'alt', 'sort'),
    #                        ('url', 'video_url'), ('title', 'credit'), 'content', 'price')}),
    # )


class SliderAdmin(admin.ModelAdmin):
    inlines = [
        ItemInline,
    ]
    list_display = ('title', )
    search_fields = ['title', ]

    # fieldsets = (
    #     (None, {'fields': (('title'), 'is_baget', 'parent', 'content', 'height', 'width', 'random', 'resize',
    #                        'quality', 'image')}),
    # )

admin.site.unregister(BlogPost)
admin.site.unregister(Product)
admin.site.register(BlogPost, MyBlogPostAdmin)
admin.site.register(Product, MyProductAdmin)

admin.site.register(Slider, SliderAdmin)


# form_fieldsets = deepcopy(FormAdmin.fieldsets)
# form_fieldsets[0][1]["fields"] += ("featured_image",)
# FormAdmin.fieldsets = form_fieldsets

# admin.site.unregister(Form)
# admin.site.register(Form, FormAdmin)