from django.contrib import admin
from copy import deepcopy

from shops.models import UserShop, ShopProduct, ShopProductImage, \
                        Cart, CartItem, Order, OrderItem,  \
                        UserShopDelivery, UserShopPayment, UserShopDeliveryOption,  ProductReview



class CartItemInline(admin.StackedInline):
    model = CartItem



class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartItemInline,
    ]
    list_display = ('id', 'user', 'created_at', 'last_updated', )


class OrderItemInline(admin.StackedInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]


class ProductImageInline(admin.StackedInline):
    model = ShopProductImage


class UserShopAdmin(admin.ModelAdmin):
    model = UserShop
    search_fields = ('shopname', )
    list_display = ('shopname', 'user', 'on_vacation', 'show_link')
    list_filter = ('on_vacation',)

    def show_link(self, obj):
        return '<a href="%s">Посмотреть на сайте</a>' % obj.get_absolute_url()
    show_link.allow_tags = True
    show_link.short_description = "Посмотреть на сайте"


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
    ]
    list_display = ('title', 'shop', 'available', 'price', 'show_link')
    list_editable = ('available',)
    search_fields = ('title', 'shop', )
    list_filter = ('available', 'condition')
    def show_link(self, obj):
        return '<a href="%s">Посмотреть на сайте</a>' % obj.get_absolute_url()
    show_link.allow_tags = True
    show_link.short_description = "Посмотреть на сайте"


class ProductReviewAdmin(admin.ModelAdmin):
    model = ProductReview
    list_display = ('content', 'author', 'product', 'approved')
    list_editable = ('approved',)
    list_filter = ('approved',)

    # def show_link(self, obj):
    #     return '<a href="%s">Посмотреть на сайте</a>' % obj.get_absolute_url()
    # show_link.allow_tags = True
    # show_link.short_description = "Посмотреть на сайте"

admin.site.register(ShopProduct, ProductAdmin)
admin.site.register(UserShopDelivery)
admin.site.register(UserShopPayment)
admin.site.register(UserShop, UserShopAdmin)
# admin.site.register(UserShopDeliveryOption)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
