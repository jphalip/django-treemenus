import django
try:
    from django.conf.urls import *
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

if django.VERSION >= (1, 1):
    urlpatterns = patterns('',
        (r'^test_treemenus_admin/', include(admin.site.urls)),
    )
else:
    urlpatterns = patterns('',
        (r'^test_treemenus_admin/(.*)', admin.site.root),
    )