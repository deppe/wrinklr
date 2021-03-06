from django.conf.urls import include, url
from django.contrib import admin
from wrinklr_django import views

admin.autodiscover()

urlpatterns = [ 
    # Examples:
    # url(r'^$', 'wrinklr_django.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home),
    url(r'^wrinklr/', include('wrinklr_app.urls', namespace='wrinklr_app'), name='wrinklr'),
    url(r'^admin/', include(admin.site.urls)),
]
