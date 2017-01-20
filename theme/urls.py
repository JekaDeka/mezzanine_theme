from django.conf.urls import url
from theme import views


urlpatterns = [
    url(r'^blog/$', views.create_user_blog),
    url(r'^item/$', views.create_user_shop_item),
]
