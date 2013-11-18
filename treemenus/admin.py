import re

import django
try:
    from django.conf.urls import patterns, url
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.utils.html import escape
from django.utils.translation import ugettext as _
try:
    from django.utils.encoding import force_text
except ImportError:  # Django < 1.5
    from django.utils.encoding import force_unicode as force_text

from treemenus.models import Menu, MenuItem
from treemenus.utils import get_parent_choices, MenuItemChoiceField, move_item_or_clean_ranks


class MenuItemAdmin(admin.ModelAdmin):
    ''' This class is used as a proxy by MenuAdmin to manipulate menu items. It should never be registered. '''
    def __init__(self, model, admin_site, menu):
        super(MenuItemAdmin, self).__init__(model, admin_site)
        self._menu = menu

    def delete_view(self, request, object_id, extra_context=None):
        if request.method == 'POST':  # The user has already confirmed the deletion.
            # Delete and return to menu page
            super(MenuItemAdmin, self).delete_view(request, object_id, extra_context)
            return HttpResponseRedirect("../../../")
        else:
            # Show confirmation page
            return super(MenuItemAdmin, self).delete_view(request, object_id, extra_context)

    def save_model(self, request, obj, form, change):
        obj.menu = self._menu
        obj.save()

    def response_add(self, request, obj, post_url_continue=None):
        if django.VERSION < (1, 5):
            post_url_continue = '../%s/'
        else:
            pk_value = obj._get_pk_val()
            post_url_continue = '../%s/' % pk_value
        response = super(MenuItemAdmin, self).response_add(request, obj, post_url_continue)
        if "_continue" in request.POST:
            return response
        elif "_addanother" in request.POST:
            return HttpResponseRedirect(request.path)
        elif "_popup" in request.POST:
            return response
        else:
            return HttpResponseRedirect("../../")

    def response_change(self, request, obj):
        super(MenuItemAdmin, self).response_change(request, obj)
        if "_continue" in request.POST:
            return HttpResponseRedirect(request.path)
        elif "_addanother" in request.POST:
            return HttpResponseRedirect("../add/")
        elif "_saveasnew" in request.POST:
            return HttpResponseRedirect("../%s/" % obj._get_pk_val())
        else:
            return HttpResponseRedirect("../../")

    def get_form(self, request, obj=None, **kwargs):
        form = super(MenuItemAdmin, self).get_form(request, obj, **kwargs)
        choices = get_parent_choices(self._menu, obj)
        form.base_fields['parent'] = MenuItemChoiceField(choices=choices)
        return form


class MenuAdmin(admin.ModelAdmin):
    menu_item_admin_class = MenuItemAdmin

    def __call__(self, request, url):
        ''' DEPRECATED!! More recent versions of Django use the get_urls method instead.
            Overriden to route extra URLs.
        '''
        if url:
            if url.endswith('items/add'):
                return self.add_menu_item(request, unquote(url[:-10]))
            if url.endswith('items'):
                return HttpResponseRedirect('../')
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)$', url)
            if match:
                return self.edit_menu_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/delete$', url)
            if match:
                return self.delete_menu_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/history$', url)
            if match:
                return self.history_menu_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/move_up$', url)
            if match:
                return self.move_up_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/move_down$', url)
            if match:
                return self.move_down_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
        return super(MenuAdmin, self).__call__(request, url)

    def get_urls(self):
        urls = super(MenuAdmin, self).get_urls()
        my_urls = patterns('',
                           (r'^(?P<menu_pk>[-\w]+)/items/add/$',
                            self.admin_site.admin_view(self.add_menu_item)),
                           (r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/$',
                            self.admin_site.admin_view(self.edit_menu_item)),
                           (r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/delete/$',
                            self.admin_site.admin_view(self.delete_menu_item)),
                           (r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/history/$',
                            self.admin_site.admin_view(self.history_menu_item)),
                           (r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/move_up/$',
                            self.admin_site.admin_view(self.move_up_item)),
                           (r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/move_down/$',
                            self.admin_site.admin_view(self.move_down_item)),
                           )

        if django.VERSION >= (1, 4):
            # Dummy named URLs to satisfy reversing the reversing requirements
            # of the menuitem add/change views. It shouldn't ever be used; it
            # just needs to exist so that it get resolved internally by the
            # django admin.
            from django.views.generic import RedirectView
            my_urls += patterns('',
                                url(r'^item_changelist/$',
                                    RedirectView.as_view(url='/'),
                                    name='treemenus_menuitem_changelist'),
                                url(r'^item_add/$',
                                    RedirectView.as_view(url='/'),
                                    name='treemenus_menuitem_add'),
                                url(r'^item_history/(?P<pk>[-\w]+)/$',
                                    RedirectView.as_view(url='/'),
                                    name='treemenus_menuitem_history'),
                                url(r'^item_delete/(?P<pk>[-\w]+)/$',
                                    RedirectView.as_view(url='/'),
                                    name='treemenus_menuitem_delete'),
                                )
        return my_urls + urls

    def get_object_with_change_permissions(self, request, model, obj_pk):
        ''' Helper function that returns a menu/menuitem if it exists and if the user has the change permissions '''
        try:
            obj = model._default_manager.get(pk=obj_pk)
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        if obj is None:
            raise Http404('%s object with primary key %r does not exist.' % (model.__name__, escape(obj_pk)))
        return obj

    def add_menu_item(self, request, menu_pk):
        ''' Custom view '''
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menuitem_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menuitem_admin.add_view(request, extra_context={'menu': menu})

    def edit_menu_item(self, request, menu_pk, menu_item_pk):
        ''' Custom view '''
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.change_view(request, menu_item_pk, extra_context={'menu': menu})

    def delete_menu_item(self, request, menu_pk, menu_item_pk):
        ''' Custom view '''
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.delete_view(request, menu_item_pk, extra_context={'menu': menu})

    def history_menu_item(self, request, menu_pk, menu_item_pk):
        ''' Custom view '''
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.history_view(request, menu_item_pk, extra_context={'menu': menu})

    def move_down_item(self, request, menu_pk, menu_item_pk):
        self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item = self.get_object_with_change_permissions(request, MenuItem, menu_item_pk)

        if menu_item.rank < menu_item.siblings().count():
            move_item_or_clean_ranks(menu_item, 1)
            msg = _('The menu item "%s" was moved successfully.') % force_text(menu_item)
        else:
            msg = _('The menu item "%s" is not allowed to move down.') % force_text(menu_item)

        if django.VERSION >= (1, 4):
            self.message_user(request, message=msg)
        else:
            request.user.message_set.create(message=msg)

        return HttpResponseRedirect('../../../')

    def move_up_item(self, request, menu_pk, menu_item_pk):
        self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item = self.get_object_with_change_permissions(request, MenuItem, menu_item_pk)

        if menu_item.rank > 0:
            move_item_or_clean_ranks(menu_item, -1)
            msg = _('The menu item "%s" was moved successfully.') % force_text(menu_item)
        else:
            msg = _('The menu item "%s" is not allowed to move up.') % force_text(menu_item)

        if django.VERSION >= (1, 4):
            self.message_user(request, message=msg)
        else:
            request.user.message_set.create(message=msg)

        return HttpResponseRedirect('../../../')


admin.site.register(Menu, MenuAdmin)
