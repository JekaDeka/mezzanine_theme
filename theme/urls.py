from django.conf.urls import url
from theme import views

#prefix in main HelloDjango project
urlpatterns = [
    url(r'^promote/$', views.promote_user, name="promote_user"),
    url(r'^$', views.true_index, name="true_index"),
]
