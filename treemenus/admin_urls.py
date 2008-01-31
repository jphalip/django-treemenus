from django.conf.urls.defaults import *

from config import APP_LABEL

urlpatterns = patterns('%s.admin_views' % APP_LABEL,
    url(r'^menu/(?P<menu_pk>\d+)/add_item/$', 'add_item', name='add_item'),
    url(r'^menu/(?P<menu_pk>\d+)/$', 'edit_menu', name='edit_menu'),
    url(r'^menu/(?P<menu_pk>\d+)/items/(?P<menu_item_pk>\d+)/$', 'edit_item', name='edit_item'),
    url(r'^menu/(?P<menu_pk>\d+)/items/(?P<menu_item_pk>\d+)/move_up/$', 'move_up_item', name='move_up_item'),
    url(r'^menu/(?P<menu_pk>\d+)/items/(?P<menu_item_pk>\d+)/move_down/$', 'move_down_item', name='move_down_item'),
    url(r'^menu/(?P<menu_pk>\d+)/items/(?P<menu_item_pk>\d+)/delete/$', 'delete_item', name='delete_item'),
)