from django.conf.urls import include, url
from theme import views
# from theme.forms import NoQuantityAddProductForm  # , NoQCartItemFormSet
from cartridge.shop.forms import CartItemFormSet
from cartridge.shop import views as cart_views
from imagefit import urls

# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'notes', views.NoteViewSet)

# prefix in main HelloDjango project
urlpatterns = [
    # url(r"^shop/product/(?P<slug>.*)/$", views.product, name="shop_product"),
    # url(r"^shop/cart/$", cart_views.cart, name="shop_cart"),
    # url(r"^shop/checkout/$", cart_views.checkout_steps, name="shop_checkout"),
    url(r"^shop/", include("cartridge.shop.urls")),


    url(r"^ordertable/(?P<pk>[0-9]+)/$",
        views.order_detail, name="order_detail"),
    url("^ordertable/category/(?P<category>[\w\-]+)/$",
        views.order_list, name='order_list_category'),


    # url(r'^ordertable/add/(?P<order_pk>[0-9]+)/$',
    #     views.order_request_add, name="order_request_add"),
    url(r'^ordertable/(?P<order_pk>[0-9]+)-(?P<performer_pk>[0-9]+)/assign/$',
        views.order_request_assign, name="order_request_assign"),
    url(r'^ordertable/(?P<order_pk>[0-9]+)-(?P<performer_pk>[0-9]+)/delete/$',
        views.order_request_delete, name="order_request_delete"),


    url(r'^profile_view/$',
        views.profile_view, name='profile_view'),

    url(r'^shop/create/$',
        views.shop_create, name="shop_create"),
    url(r'^shop/edit/$',
        views.shop_create, name="shop_edit"),

    url(r'^vacation/$',
        views.shop_toggle_vacation, name="shop_toggle_vacation"),

    url(r'^ajax/validate_shopname/$',
        views.validate_shopname, name='validate_shopname'),
    url(r'^ajax/get_categories/$',
        views.get_categories, name='get_categories'),


    url('^shop/(?P<slug>[\w\-]+)/$',
        views.shop_view, name='shop_view'),

    url(r'^settings/$',
        views.profile_settings, name="profile_settings"),

    url(r'^$', views.true_index, name="true_index"),
    url(r'^imagefit/', include('imagefit.urls')),
    url(r'^chaining/', include('smart_selects.urls')),
    # url(r'^api/', include(router.urls, namespace='api')),
]

# urlpatterns += router.urls
