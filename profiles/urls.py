from django.conf.urls import include, url
from profiles import views

urlpatterns = [
    url(r'^profile/change_password/$', views.change_password, name="change_fck_password"),
    url(r'^profile/settings/$', views.ProfileSettings.as_view(), name="profile-settings"),
    url(r'^profile/$', views.ProfileCreate.as_view(), name="profile-add"),
    url(r'^profile/edit/$', views.ProfileUpdate.as_view(), name="profile-update"),
    url(r'^profile/update/status/$', views.profile_status_toggle, name="profile-status-toggle"),
    url(r'^profile/(?P<slug>.*)/$', views.ProfileDetailView.as_view(), name='profile-detail'),
    url(r'^profile-list/$', views.ProfileList.as_view(), name="profile-list"),



]
