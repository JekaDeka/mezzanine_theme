from django.conf.urls import include, url
from theme import views
from imagefit import urls

# prefix in main HelloDjango project
urlpatterns = [
    url("^ordertable/(?P<pk>\w+)/",
        views.order_detail, name="order_detail"),
    url(r'^profile_view/$',
        views.profile_view, name='profile_view'),

    url(r'^create/$',
        views.shop_create, name="shop_create"),
    url(r'^edit/$',
        views.shop_create, name="shop_edit"),

    url(r'^ajax/validate_shopname/$',
        views.validate_shopname, name='validate_shopname'),


    url('^shop/(?P<slug>[\w\-]+)/$',
        views.shop_view, name='shop_view'),
    url(r'^promote/$', views.promote_user, name="promote_user"),
    url(r'^settings/$',
        views.profile_settings, name="profile_settings"),
    url(r'^$', views.true_index, name="true_index"),
    url(r'^imagefit/', include('imagefit.urls')),

]
