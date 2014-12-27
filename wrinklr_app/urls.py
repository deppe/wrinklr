from django.conf.urls import patterns, url

from wrinklr_app import views

urlpatterns = patterns('',
    url(r'^$', views.input_celebs, name='input_celebs'),
    url(r'^age$', views.age, name='age')
)