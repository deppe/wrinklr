from django.conf.urls import url
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from wrinklr_app import views

urlpatterns = [
    url(r'^$', views.input_celebs, name='input_celebs'),
    url(r'^age$', views.age, name='age'),
    url(r'^vs/(?P<matchup_id>[0-9]+)$', views.matchup, name='matchup'),
    url(r'^vs/(?P<matchup_id>[0-9]+)/results$', views.matchup_results, name='matchup_results'),
    url(r'^login$', login, name='login', kwargs={'redirect_authenticated_user': True}),
    url(r'^logout$', logout, name='logout'),
    url(r'^register$', views.register, name='register')
]
