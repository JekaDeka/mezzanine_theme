from copy import deepcopy
from django.contrib import admin
from mezzanine.blog.models import BlogPost
from cartridge.shop.models import Product
from cartridge.shop.admin import ProductAdmin
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from theme.models import Slider, SliderItem

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
product_fieldsets = deepcopy(ProductAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(-2, "preview_content")


class MyBlogPostAdmin(BlogPostAdmin):
    fieldsets = blog_fieldsets

    def get_queryset(self, request):
        qs = super(MyBlogPostAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user)


class MyProductAdmin(ProductAdmin):
    fieldsets = product_fieldsets

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
