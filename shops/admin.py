from django.contrib import admin

from shops.models import UserShop, ShopProduct, Cart, CartItem, Order, OrderItem, UserShopDelivery, UserShopPayment, UserShopDeliveryOption

class CartItemInline(admin.StackedInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartItemInline,
    ]


class OrderItemInline(admin.StackedInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]


admin.site.register(ShopProduct)
admin.site.register(UserShopDelivery)
admin.site.register(UserShopPayment)
admin.site.register(UserShop)
admin.site.register(UserShopDeliveryOption)

admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
