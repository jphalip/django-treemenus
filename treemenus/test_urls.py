from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^test_treemenus_admin/(.*)', admin.site.root),
)
