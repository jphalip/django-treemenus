from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^test_treemenus_admin/(.*)', admin.site.root), # For older versions of Django (see deprecated MenuAdmin.__call__() method)
    (r'^test_treemenus_admin/', include(admin.site.urls)),
)
