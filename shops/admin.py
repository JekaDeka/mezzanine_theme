from django.contrib import admin

from shops.models import ShopProduct, Cart, CartItem, Order, OrderItem

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

admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
