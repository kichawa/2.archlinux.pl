from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



admin.autodiscover()


urlpatterns = patterns('',
    url(r'^',
        include('forum.urls')),
    url(r'^_admin/',
        include(admin.site.urls)),
    url(r'^account/',
        include('django.contrib.auth.urls')),
)


urlpatterns += staticfiles_urlpatterns()
