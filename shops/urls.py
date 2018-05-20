from django.conf.urls import include, url
from shops import views

urlpatterns = [
    url(r'^settings/products/$', views.ProductList.as_view(), name='product-list'),
    url(r'^settings/products/add/$', views.ProductImageCreate.as_view(), name='product-add'),
    url(r'^settings/products/(?P<pk>[0-9]+)/edit/$', views.ProductImageUpdate.as_view(), name='product-update'),
    url(r'^settings/products/(?P<pk>[0-9]+)/delete/$', views.ProductDelete.as_view(), name='product-delete'),

    url(r'^product/(?P<slug>.*)/$', views.ProductDetailView.as_view(), name='product-detail'),


    # url(r'^shop/create/$', views.ShopDeliveryOptionCreate.as_view(), name="shop_create"),
    # url(r'^shop/edit/$', views.ShopDeliveryOptionCreate.as_view(), name="shop_edit"),
    # view cart
    # cart itself + items_formset
    # add item to cart via ajax
    # cart delete item
    # cart update
    url(r'^ajax/cart/get/$', views.get_cart, name='get_cart'),
    url(r'^ajax/cart/update/$', views.cart_update, name='cart_update'),
    url(r'^cart/$', views.CartView.as_view(), name='shop-cart'),
    url(r'^checkout/(?P<slug>[\w\-]+)/(?P<pk>[0-9]+)/$', views.CheckoutProcess.as_view(), name='shop-checkout'),


    url(r'^shop/(?P<slug>[\w\-]+)/$', views.ShopDetailView.as_view(), name='shop-view'),
    url(r'^vacation/$', views.shop_toggle_vacation, name="shop_toggle_vacation"),
    url(r'^ajax/validate_shopname/$', views.validate_shopname, name='validate_shopname'),
    url(r'^settings/shop/$', views.ShopList.as_view(), name='shop-list'),
    url(r'^settings/shop/add/$', views.ShopDeliveryOptionCreate.as_view(), name='shop-add'),
    url(r'^settings/shop/(?P<slug>.*)/$', views.ShopDeliveryOptionUpdate.as_view(), name='shop-update'),
    url(r'^settings/shop/(?P<slug>.*)/delete/$', views.ShopDelete.as_view(), name='shop-delete'),

    url(r'^settings/orders/(?P<slug>[\w\-]+)/(?P<pk>[0-9]+)/$', views.OrderList.as_view(), name='shop-order-list'),
    url(r'^orders/$', views.OrderList.as_view(), name='user-order-list'),
    url(r'^settings/orders/(?P<pk>[0-9]+)/edit/$', views.OrderUpdate.as_view(), name='order-update'),
    url(r'^settings/orders/(?P<pk>[0-9]+)/detail/$', views.OrderDetail.as_view(), name='order-detail'),
]
