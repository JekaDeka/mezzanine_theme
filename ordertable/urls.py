from django.conf.urls import include, url
from ordertable import views


urlpatterns = [
    url(r"^ordertable/$", views.order_list, name='order_list'),
    url(r"^ordertable/(?P<pk>[0-9]+)/$",
        views.OrderTableItemDetail.as_view(), name="order_detail"),
    url(r"^ordertable/(?P<pk>[0-9]+)/$",
        views.OrderTableItemDetail.as_view(), name="ordertableitem-detail"),

    url("^ordertable/category/(?P<category>[\w\-]+)/$",
        views.order_list, name='order_list_category'),
    url(r'^ordertable/(?P<order_pk>[0-9]+)-(?P<performer_pk>[0-9]+)/assign/$',
        views.order_request_assign, name="order_request_assign"),
    url(r'^ordertable/(?P<order_pk>[0-9]+)-(?P<performer_pk>[0-9]+)/refuse/$',
        views.order_request_refuse, name="order_request_refuse"),
    url(r'^settings/ordertable/$', views.OrderTableItemList.as_view(), name='ordertableitem-list'),
    url(r'settings/ordertable/add/$', views.OrderTableItemImageCreate.as_view(), name='ordertableitem-add'),
    url(r'settings/ordertable/(?P<pk>[0-9]+)/edit/$', views.OrderTableItemImageUpdate.as_view(), name='ordertableitem-update'),
    url(r'settings/ordertable/(?P<pk>[0-9]+)/delete/$', views.OrderTableItemDelete.as_view(), name='ordertableitem-delete'),

    url(r'settings/ordertable/(?P<pk>[0-9]+)/request/assign/$', views.OrderTableRequestAssignList.as_view(), name='ordertableitemrequest-list'),

    url(r'settings/ordertable/requests/outcome/$', views.OrderTableRequestOutList.as_view(), name='ordertableitemrequestout-list'),
    # url(r'^settings/ordertable/requests/in/$', views.OrderTableIncomeRequestList.as_view(), name='ordertableitemrequest-list'),
    # url(r'^settings/ordertable/requests/out/$', views.OrderTableOutcomeRequestList.as_view(), name='ordertableitemoutrequest-list'),
]

# urlpatterns += router.urls
