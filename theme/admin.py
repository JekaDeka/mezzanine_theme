from copy import deepcopy
from django.contrib import admin
from django.db import models
# from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from mezzanine.forms.admin import FormAdmin
from mezzanine.blog.models import BlogPost
from cartridge.shop.models import Product
from cartridge.shop.admin import ProductAdmin, ProductImageAdmin, ProductVariationAdmin
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from theme.models import Slider, SliderItem, OrderItem, OrderItemCategory

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
Product._meta.get_field('unit_price').verbose_name = 'Цена'

product_fieldsets = deepcopy(ProductAdmin.fieldsets)


class MyBlogPostAdmin(BlogPostAdmin):
    fieldsets = blog_fieldsets
    fieldsets.remove(fieldsets[1])
    list_per_page = 30
    fieldsets[0][1]['fields'] = ['title',
                                 # 'status',
                                 # ('publish_date', 'expiry_date'),
                                 'featured_image',
                                 'preview_content', 'content', 'categories', 'allow_comments']

    fieldsets[1][1]['fields'].pop()

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = ('title', 'user', 'status', 'admin_link',)
        else:
            list_display = ('title', 'publish_date', 'admin_link',)
        return list_display

    def get_queryset(self, request):
        qs = super(MyBlogPostAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user)


class MyProductAdmin(ProductAdmin):
    # inlines = (ProductImageAdmin,)
    fieldsets = product_fieldsets
    list_per_page = 30
    fieldsets[0][1]['fields'] = ['title', 'pre_order',
                                 'status', 'unit_price',
                                 # ('publish_date', 'expiry_date'),
                                 'material', 'condition',
                                 'categories', 'content']

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = ('title', 'status', 'pre_order', 'admin_link',)
        else:
            list_display = ('title', 'pre_order', 'admin_link',)
        return list_display

    def get_queryset(self, request):
        qs = super(MyProductAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user = request.user
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


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'price', 'ended')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(OrderItemAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)


admin.site.unregister(BlogPost)
admin.site.unregister(Product)
admin.site.register(BlogPost, MyBlogPostAdmin)
admin.site.register(Product, MyProductAdmin)

admin.site.register(Slider, SliderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderItemCategory)

# form_fieldsets = deepcopy(FormAdmin.fieldsets)
# form_fieldsets[0][1]["fields"] += ("featured_image",)
# FormAdmin.fieldsets = form_fieldsets

# admin.site.unregister(Form)
# admin.site.register(Form, FormAdmin)
