from django.conf.urls import url

from wrinklr_app import views

urlpatterns = [
    url(r'^$', views.input_celebs, name='input_celebs'),
    url(r'^age$', views.age, name='age')
]
