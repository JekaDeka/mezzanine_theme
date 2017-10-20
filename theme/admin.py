from copy import deepcopy
from django.contrib import admin
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.conf.urls import url
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline
from django.core.urlresolvers import reverse
from mezzanine.forms.admin import FormAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.pages.models import Page
from cartridge.shop.models import Category, Product, ProductImage, ProductVariation
from cartridge.shop.admin import ProductAdmin, ProductImageAdmin, ProductVariationAdmin
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from theme.models import Slider, SliderItem, OrderItem, OrderItemCategory, OrderItemRequest, OrderItemImage
from theme.forms import SelectForm, OrderItemAdminForm


# Lists of field names.
option_fields = []


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

    def save_model(self, request, obj, form, change):
        try:
            tmp = BlogPost.objects.get(pk=obj.pk)
        except Exception as e:
            obj.status = 1
            tmp = None

        if tmp and not 'status' in form.changed_data and not request.user.is_superuser:
            obj.status = tmp.status
        super(MyBlogPostAdmin, self).save_model(request, obj, form, change)


class MyProductAdmin(ProductAdmin):
    # formfield_overrides = {
    #     models.ManyToManyField: {
    #         'widget': ToolBoxEditForm},
    # }
    form = SelectForm
    inlines = (ProductImageAdmin, ProductVariationAdmin)
    # ProductVariationAdmin.form = ThemeProductVariationAdminForm
    ProductVariationAdmin.extra = 0
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
        if not obj.unit_price:
            obj.unit_price = 1
        if obj.unit_price < 0:
            obj.unit_price = - obj.unit_price
        super(MyProductAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Here be dragons. We want to perform these steps sequentially:
        - Save variations formset
        - Run the required variation manager methods:
          (create_from_options, manage_empty, etc)
        - Save the images formset
        The variations formset needs to be saved first for the manager
        methods to have access to the correct variations. The images
        formset needs to be run last, because if images are deleted
        that are selected for variations, the variations formset will
        raise errors when saving due to invalid image selections. This
        gets addressed in the set_default_images method.
        An additional problem is the actual ordering of the inlines,
        which are in the reverse order for achieving the above. To
        address this, we store the images formset as an attribute, and
        then call save on it after the other required steps have
        occurred.
        """

        product = self.model.objects.get(id=self._product_id)

        # Store the images formset for later saving, otherwise save the
        # formset.
        if formset.model == ProductImage:
            self._images_formset = formset
        else:
            super(ProductAdmin, self).save_formset(request, form, formset,
                                                   change)

        # Run each of the variation manager methods if we're saving
        # the variations formset.
        if formset.model == ProductVariation:

            # Build up selected options for new variations.
            options = dict([(f, request.POST.getlist(f)) for f in option_fields
                            if request.POST.getlist(f)])
            # Create a list of image IDs that have been marked to delete.
            deleted_images = [request.POST.get(f.replace("-DELETE", "-id"))
                              for f in request.POST
                              if f.startswith("images-") and f.endswith("-DELETE")]

            # Create new variations for selected options.
            product.variations.create_from_options(options)
            # Create a default variation if there are none.
            product.variations.manage_empty()

            # Remove any images deleted just now from variations they're
            # assigned to, and set an image for any variations without one.
            product.variations.set_default_images(deleted_images)

            # Save the images formset stored previously.
            super(ProductAdmin, self).save_formset(request, form,
                                                   self._images_formset, change)

            # Run again to allow for no images existing previously, with
            # new images added which can be used as defaults for variations.
            product.variations.set_default_images(deleted_images)

            # Copy duplicate fields (``Priced`` fields) from the default
            # variation to the product.
            product.copy_default_variation()

            # Save every translated fields from ``ProductOption`` into
            # the required ``ProductVariation``
            # if settings.USE_MODELTRANSLATION:
            #     from collections import OrderedDict
            #     from modeltranslation.utils import (build_localized_fieldname
            #                                         as _loc)
            #     for opt_name in options:
            #         for opt_value in options[opt_name]:
            #             opt_obj = ProductOption.objects.get(type=opt_name[6:],
            #                                                 name=opt_value)
            #             params = {opt_name: opt_value}
            #             for var in product.variations.filter(**params):
            #                 for code in OrderedDict(settings.LANGUAGES):
            #                     setattr(var, _loc(opt_name, code),
            #                             getattr(opt_obj, _loc('name', code)))
            #                 var.save()


class SliderItemInline(admin.StackedInline):
    model = SliderItem


class SliderAdmin(admin.ModelAdmin):
    inlines = [
        SliderItemInline,
    ]
    list_display = ('title', )
    search_fields = ['title', ]

    # fieldsets = (
    #     (None, {'fields': (('title'), 'is_baget', 'parent', 'content', 'height', 'width', 'random', 'resize',
    #                        'quality', 'image')}),
    # )


class OrderItemImageInline(admin.TabularInline):
    model = OrderItemImage
    extra = 2


class OrderItemAdmin(admin.ModelAdmin):
    view_on_site = True
    list_display = ('title', 'created', 'price', 'ended',
                    'get_performer', 'view_on_site')
    form = OrderItemAdminForm
    inlines = [OrderItemImageInline, ]

    def view_on_site(self, obj):
        return format_html("<a href={}>Посмотреть на сайте</a>", obj.get_absolute_url())
    view_on_site.short_description = ""

    def get_performer(self, obj):
        if obj.performer:
            return obj.performer.get_full_name()
        return obj.performer
    get_performer.short_description = 'Исполнитель'

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(OrderItemAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    # def format_date(self, obj):
    #     return obj.ended.strftime('%d %b %Y %H:%M')

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     field = super(OrderItemAdmin, self).formfield_for_dbfield(
    #         db_field, **kwargs)

    #     if isinstance(db_field, models.DateField):
    #         return forms.DateField(input_formats=('%d/%m/%Y',))
    #     return field


@admin.register(OrderItemRequest)
class OrderItemRequestAdmin(admin.ModelAdmin):
    model = OrderItemRequest
    list_display = ('order', 'get_performers', 'view_on_site')
    list_display_links = None

    def view_on_site(self, obj):
        return format_html("<a href={}>Посмотреть на сайте</a>", obj.get_absolute_url())
    view_on_site.short_description = ""

    def get_queryset(self, request):
        qs = super(OrderItemRequestAdmin, self).get_queryset(request)
        orders = OrderItem.objects.filter(
            performer=None).filter(order__in=qs).distinct()
        if not request.user.is_superuser:
            orders.filter(author=request.user)

        if orders:
            return orders
        else:
            return OrderItem.objects.none()
        # if OrderItemRequest.objects.filter(order__in=qs):
        #     if request.user.is_superuser:
        #         return qs.filter()
        #     return qs.filter(author=request.user)
        # else:
        #     return OrderItem.objects.none()

    def order(self, obj):
        return obj.title

    def buttons(self, order):
        return format_html(
            '<div class="btn-group dropdown">'
            '<a href="{}" class="btn btn-sm btn-default btn-raised" target="_blank">{}<div class="ripple-container"></div></a>'
            '<button class="btn btn-sm btn-info btn-raised dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>'
            '<ul class="dropdown-menu" role="menu">'
            '<li><a href="{}">Одобрить</a></li>'
            '<li><a href="{}" target="_blank">Посмотреть профиль</a></li>'
            '<li class="divider"></li>'
            '<li><a href="{}">Отказать</a></li>'
            '</ul>'
            '</div><br>',
            reverse('profile', args=[order.performer]),
            order.performer.profile.get_full_name(),
            reverse('order_request_assign', args=[
                    order.order.id, order.performer.id]),
            reverse('profile', args=[order.performer]),
            reverse('order_request_delete', args=[
                    order.order.id, order.performer.id]),
        )

    def get_performers(self, obj):
        orderRequests = OrderItemRequest.objects.filter(order=obj)
        html = '<div class="parent">'
        html += "".join(self.buttons(order) for order in orderRequests)
        html += '</div>'
        return html

    get_performers.short_description = 'Исполнители'
    get_performers.allow_tags = True


admin.site.unregister(BlogPost)
admin.site.unregister(Product)
admin.site.register(BlogPost, MyBlogPostAdmin)
admin.site.register(Product, MyProductAdmin)

admin.site.register(Slider, SliderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderItemCategory)
# admin.site.register(OrderItemRequest, OrderItemRequestAdmin)

# form_fieldsets = deepcopy(FormAdmin.fieldsets)
# form_fieldsets[0][1]["fields"] += ("featured_image",)
# FormAdmin.fieldsets = form_fieldsets

# admin.site.unregister(Form)
# admin.site.register(Form, FormAdmin)
