import re
from django.utils.functional import wraps
from django.contrib import admin
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.forms import ChoiceField
from django.http import HttpResponseRedirect
from django.contrib.admin.util import unquote
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

from treemenus.models import Menu, MenuItem
from treemenus.utils import get_parent_choices



class MenuItemChoiceField(ChoiceField):
    ''' Custom field to display the list of items in a tree manner '''
    def clean(self, value):
        return MenuItem.objects.get(pk=value)


def move_item(menu_item, vector):
    ''' Helper function to move and item up or down in the database '''
    old_rank = menu_item.rank
    swapping_sibling = MenuItem.objects.get(parent=menu_item.parent, rank=old_rank+vector)
    new_rank = swapping_sibling.rank
    swapping_sibling.rank = old_rank
    menu_item.rank = new_rank
    menu_item.save()
    swapping_sibling.save()







class MenuItemAdmin(admin.ModelAdmin):
    ''' This class is used as a proxy by MenuAdmin to manipulate menu items. It should never be registered. '''
    def __init__(self, model, admin_site, menu):
        #TODO: Try to get rid of _menu attribute...
        super(MenuItemAdmin, self).__init__(model, admin_site)
        self._menu = menu
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        ''' Overriden to change the choices of the ``parent`` attribute's form field '''
        if db_field.name == 'parent':
            kwargs['choices'] = get_parent_choices(self._menu)
            return MenuItemChoiceField(**kwargs)
        return super(MenuItemAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def delete_view(self, request, object_id, extra_context=None):
        if request.method == 'POST':
            # Delete and return to menu page
            ignored_response = super(MenuItemAdmin, self).delete_view(request, object_id, extra_context)
            return HttpResponseRedirect("../../../")
        else:
            # Show confirmation page
            return super(MenuItemAdmin, self).delete_view(request, object_id, extra_context)

    def save_add(self, request, form, formsets, post_url_continue):
        response = super(MenuItemAdmin, self).save_add(request, form, formsets, post_url_continue)
        if request.POST.has_key("_continue"):
            return response
        elif request.POST.has_key("_addanother"):
            return HttpResponseRedirect(request.path)
        elif request.POST.has_key("_popup"):
            return response
        else:
            return HttpResponseRedirect("../../")

    def save_change(self, request, form, formsets=None):
        response =  super(MenuItemAdmin, self).save_change(request, form, formsets)
        if request.POST.has_key("_continue"):
            return HttpResponseRedirect(request.path)
        elif request.POST.has_key("_addanother"):
            return HttpResponseRedirect("../add/")
        elif request.POST.has_key("_saveasnew"):
            #TODO: Know issue: how to redirect to the newly created object's edit page?
            return HttpResponseRedirect("../../")
        else:
            return HttpResponseRedirect("../../")


class MenuAdmin(admin.ModelAdmin):
    menu_item_admin_class = MenuItemAdmin
    
    def __call__(self, request, url):
        ''' Overriden to route extra URLs.
        
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
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/move_up$', url)
            if match:
                return self.move_up_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
            match = re.match('^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/move_down$', url)
            if match:
                return self.move_down_item(request, match.group('menu_pk'), match.group('menu_item_pk'))
        
        return super(MenuAdmin, self).__call__(request, url)
    
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
        return menuitem_admin.add_view(request, extra_context={ 'menu': menu })

    def edit_menu_item(self, request, menu_pk, menu_item_pk):
        ''' Custom view '''
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.change_view(request, menu_item_pk, extra_context={ 'menu': menu })

    def delete_menu_item(self, request, menu_pk, menu_item_pk):
        ''' Custom view '''
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.delete_view(request, menu_item_pk, extra_context={ 'menu': menu })

    def move_down_item(self, request, menu_pk, menu_item_pk):
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item = self.get_object_with_change_permissions(request, MenuItem, menu_item_pk)
        
        if menu_item.rank < menu_item.siblings().count():
            move_item(menu_item, 1)
            msg = _('The menu item "%s" was moved successfully.') % force_unicode(menu_item)
        else:
            msg = _('The menu item "%s" is not allowed to move down.') % force_unicode(menu_item)
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect('../../../')
    
    def move_up_item(self, request, menu_pk, menu_item_pk):
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item = self.get_object_with_change_permissions(request, MenuItem, menu_item_pk)
        
        if menu_item.rank > 0:
            move_item(menu_item, -1)
            msg = _('The menu item "%s" was moved successfully.') % force_unicode(menu_item)
        else:
            msg = _('The menu item "%s" is not allowed to move up.') % force_unicode(menu_item)
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect('../../../')


admin.site.register(Menu, MenuAdmin)