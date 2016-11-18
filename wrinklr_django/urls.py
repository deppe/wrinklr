from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [ 
    # Examples:
    # url(r'^$', 'wrinklr_django.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^wrinklr/', include('wrinklr_app.urls', namespace='wrinklr_app')),
    url(r'^admin/', include(admin.site.urls)),
]
