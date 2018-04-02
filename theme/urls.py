from django.conf.urls import include, url
from theme import views
# from theme.forms import NoQuantityAddProductForm  # , NoQCartItemFormSet
# from cartridge.shop.forms import CartItemFormSet
# from cartridge.shop import views as cart_views
# from imagefit import urls
# from orders import urls
# from shops import urls
# from profiles import urls

# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'notes', views.NoteViewSet)

# prefix in main HelloDjango project
urlpatterns = [
    # url(r"^shop/product/(?P<slug>.*)/$", views.product, name="shop_product"),
    # url(r"^shop/cart/$", cart_views.cart, name="shop_cart"),
    # url(r"^shop/checkout/$", cart_views.checkout_steps, name="shop_checkout"),
    url(r"^shop/", include("cartridge.shop.urls")),


    # url(r"^ordertable/(?P<pk>[0-9]+)/$",
    #     views.ordertableitemDetail.as_view(), name="order_detail"),
    # url("^ordertable/category/(?P<category>[\w\-]+)/$",
    #     views.order_list, name='order_list_category'),


    # # url(r'^ordertable/add/(?P<order_pk>[0-9]+)/$',
    # #     views.order_request_add, name="order_request_add"),
    # url(r'^ordertable/(?P<order_pk>[0-9]+)-(?P<performer_pk>[0-9]+)/assign/$',
    #     views.order_request_assign, name="order_request_assign"),
    # url(r'^ordertable/(?P<order_pk>[0-9]+)-(?P<performer_pk>[0-9]+)/delete/$',
    #     views.order_request_delete, name="order_request_delete"),


    # url(r'^profile_view/$',
    #     views.profile_view, name='profile_view'),

    # url(r'^shop/create/$',
    #     views.shop_create, name="shop_create"),
    # url(r'^shop/edit/$',
    #     views.shop_create, name="shop_edit"),

    # url(r'^vacation/$',
    #     views.shop_toggle_vacation, name="shop_toggle_vacation"),

    # url(r'^ajax/validate_shopname/$',
    #     views.validate_shopname, name='validate_shopname'),
    url(r'^ajax/get_categories/$',
        views.get_categories, name='get_categories'),

    # url(r'^settings/$',
    #     views.profiles:profile-settings, name="profile-settings"),

    url(r'^settings/blog/$', views.BlogPostList.as_view(), name='blogpost-list'),
    url(r'settings/blog/add/$', views.BlogPostCreate.as_view(), name='blogpost-add'),
    url(r'settings/blog/(?P<pk>[0-9]+)/edit/$', views.BlogPostUpdate.as_view(), name='blogpost-update'),
    url(r'settings/blog/(?P<pk>[0-9]+)/delete/$', views.BlogPostDelete.as_view(), name='blogpost-delete'),

    # url(r'^settings/products/$', views.ProductList.as_view(), name='product-list'),
    # url(r'settings/products/add/$', views.ProductImageCreate.as_view(), name='product-add'),
    # url(r'settings/products/(?P<pk>[0-9]+)/edit/$', views.ProductImageUpdate.as_view(), name='product-update'),
    # url(r'settings/products/(?P<pk>[0-9]+)/delete/$', views.ProductDelete.as_view(), name='product-delete'),

    # url(r'^product/(?P<slug>.*)/$', views.ProductDetailView.as_view(), name='product-detail'),

    url(r'^$', views.true_index, name="true_index"),
    url(r'^imagefit/', include('imagefit.urls')),
    url(r'^chaining/', include('smart_selects.urls')),
    # url("^product/(?P<slug>[\w\-]+)/$", views.product,
    #     name="shop_product"),

    # url(r'^profile/$', views.ShopList.as_view(), name='shop-list'),
    # url(r'^profile/add/$', views.ShopDeliveryOptionCreate.as_view(), name='shop-add'),
    # url(r'^profile/(?P<pk>[0-9]+)/$', views.ShopDeliveryOptionUpdate.as_view(), name='shop-update'),
    # url(r'^profile/(?P<pk>[0-9]+)/delete/$', views.ShopDelete.as_view(), name='shop-delete'),

    url(r'^search/all/$', views.SearchAll.as_view(), name='search-all'),


    # url('^shop/(?P<slug>[\w\-]+)/$',
    #     views.ShopDetailView.as_view(), name='shop-view'),
    # url('^shop/(?P<slug>[\w\-]+)/$',
    #     views.shop_view, name='shop_view'),

]
