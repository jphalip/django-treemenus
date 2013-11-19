try:
    from django.conf.urls import patterns, include
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
        (r'^test_treemenus_admin/', include(admin.site.urls)),
    )

handler500 = 'django.views.defaults.server_error'