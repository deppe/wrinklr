from django.conf.urls import url
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from wrinklr_app import views

urlpatterns = [
    url(r'^$', views.input_celebs, name='input_celebs'),
    url(r'^age$', views.age, name='age'),
    url(r'^vs/(?P<matchup_id>[0-9]+)$', views.matchup, name='matchup'),
    url(r'^vs/(?P<matchup_id>[0-9]+)/results$', views.matchup_results, name='matchup_results'),
    url(r'^navbar_login$', views.navbar_login, name='navbar_login'),
    url(r'^login$', 
        login, 
        name='login', 
        kwargs={
            'redirect_authenticated_user': True,
            'template_name': 'wrinklr_app/login.html',
            'extra_context': {'navbar_text': 'Login'}
        }),
    url(r'^logout$', logout, name='logout', kwargs={'next_page': '/wrinklr/'}),
    url(r'^register$', views.register, name='register'),
    url(r'^slack/slash$', views.slack_slash, name='slack_slash'),
    url(r'^slack/action$', views.slack_action, name='slack_action'),
    url(r'^ping$', views.ping, name='ping')
]
