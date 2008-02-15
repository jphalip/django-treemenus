from itertools import chain

from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from models import Menu, MenuItem
from forms import MenuForm, MenuItemForm
from config import APP_LABEL
from utils import clean_ranks, get_extension_model_class, get_extension_form_class, MenuItemExtensionError

def edit_menu(request, menu_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/%s/menu/' % APP_LABEL)
    else:
        form = MenuForm(instance = menu)
    
    return render_to_response('admin/%s/edit_menu.html' % APP_LABEL,
                              { 'form': form, 'menu': menu, 'flat_structure': menu.root_item.get_flattened() },
                              context_instance=RequestContext(request))
edit_menu = staff_member_required(never_cache(edit_menu))



def get_parent_choices(menu, menu_item=None):
    """
    Returns flat list of tuples (possible_parent.pk, possible_parent.caption_with_spacer).
    If 'menu_item' is not given or None, returns every item of the menu. If given, intentionally omit it and its descendant in the list.
    """
    def get_flat_tuples(menu_item, excepted_item=None):
        if menu_item == excepted_item:
            return []
        else:
            choices = [(menu_item.pk, mark_safe(menu_item.caption_with_spacer()))]
            if menu_item.hasChildren:
                for child in menu_item.children():
                    choices = chain(choices, get_flat_tuples(child, excepted_item))
            return choices
    
    return get_flat_tuples(menu.root_item, menu_item)




def add_item(request, menu_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    
    extension_form = None    
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        
        if hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL'):
            extension_form = get_extension_form_class()(request.POST)
        
        if form.is_valid() and (not hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL') or extension_form.is_valid()):
            menu_item = form.save(commit=False)
            clean_ranks(menu_item.siblings()) # Clean ranks for new siblings
            menu_item.rank = menu_item.siblings().count()
            menu_item.menu = menu
            menu_item.save()
            
            if extension_form:
                extension = extension_form.save(commit=False)
                extension.menu_item = menu_item
                extension.save()
            
            
            msg = _('The menu item "%s" was added successfully.') % force_unicode(menu_item)
            
            if "_continue" in request.POST:
                request.user.message_set.create(message=msg + ' ' + _("You may edit it again below."))
                return HttpResponseRedirect("../items/%s/" % menu_item.pk)
            elif "_addanother" in request.POST:
                request.user.message_set.create(message=msg + ' ' + _("You may add another menu item below."))
                return HttpResponseRedirect(request.path)
                return HttpResponseRedirect("../../add_item/")
            else:
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('edit_menu', kwargs={ 'menu_pk': menu.pk }))
    else:
        form_class = MenuItemForm
        choices = get_parent_choices(menu)
        form_class.base_fields['parent'].choices = choices
        form = form_class()
        if hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL'):
            extension_form = get_extension_form_class()()
    
    return render_to_response('admin/%s/add_edit_item.html' % APP_LABEL,
                              { 'form': form, 'extension_form': extension_form, 'menu': menu, 'title': _('Add menu item'), 'add_or_edit': 'add' },
                              context_instance=RequestContext(request))
add_item = staff_member_required(never_cache(add_item))



def edit_item(request, menu_pk, menu_item_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    menu_item = get_object_or_404(MenuItem, pk=menu_item_pk)
    
    extension_form = None
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu_item)
        
        if hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL'):
            menu_item = get_object_or_404(MenuItem, pk=menu_item_pk)
            extension_form = get_extension_form_class()(request.POST, instance=menu_item.get_extension())
        
        if form.is_valid() and (not hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL') or extension_form.is_valid()):
            form.save()
            
            if extension_form:
                extension_form.save()
            
            msg = _('The menu item "%s" was changed successfully.') % force_unicode(menu_item)
            if "_continue" in request.POST:
                request.user.message_set.create(message=msg + ' ' + _("You may edit it again below."))
                return HttpResponseRedirect(request.path)
            elif "_addanother" in request.POST:
                request.user.message_set.create(message=msg + ' ' + (_("You may add another menu item below.")))
                return HttpResponseRedirect("../../add_item/")
            else:
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('edit_menu', kwargs={ 'menu_pk': menu.pk }))
    else:
        form_class = MenuItemForm
        choices = get_parent_choices(menu, menu_item)
        form_class.base_fields['parent'].choices = choices
        form = form_class(instance=menu_item)
        if hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL'):
            extension_form = get_extension_form_class()(instance=menu_item.get_extension())
    
    return render_to_response('admin/%s/add_edit_item.html' % APP_LABEL,
                              { 'form': form, 'extension_form': extension_form, 'menu': menu, 'menu_item': menu_item, 'title': _('Change menu item'), 'add_or_edit': 'edit' },
                              context_instance=RequestContext(request))
edit_item = staff_member_required(never_cache(edit_item))


def delete_item(request, menu_pk, menu_item_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    menu_item = get_object_or_404(MenuItem, pk=menu_item_pk)
    
    opts = MenuItem._meta
    if not request.user.has_perm(APP_LABEL + '.' + opts.get_delete_permission()):
        raise PermissionDenied

    if request.POST: # The user has already confirmed the deletion.
        obj_display = force_unicode(menu_item)
        menu_item.delete()
        request.user.message_set.create(message=_('The %(name)s "%(obj)s" was deleted successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': obj_display})
        return HttpResponseRedirect("../../../")
    extra_context = {
        "title": _("Are you sure?"),
        "menu_item": menu_item,
        "menu": menu,
        "opts": MenuItem._meta,
    }
    return render_to_response("admin/%s/delete_item_confirmation.html" % APP_LABEL, extra_context, context_instance=RequestContext(request))
delete_item = staff_member_required(never_cache(delete_item))


def move_item(menu_item, vector):
    old_rank = menu_item.rank
    swaping_sibling = MenuItem.objects.get(parent=menu_item.parent, rank=old_rank+vector)
    new_rank = swaping_sibling.rank
    swaping_sibling.rank = old_rank
    menu_item.rank = new_rank
    
    menu_item.save()
    swaping_sibling.save()


def move_down_item(request, menu_pk, menu_item_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    menu_item = get_object_or_404(MenuItem, pk=menu_item_pk)
    
    if menu_item.rank < menu_item.siblings().count():
        move_item(menu_item, 1)
        msg = _('The menu item "%s" was moved successfully.') % force_unicode(menu_item)
    else:
        msg = _('The menu item "%s" is not allowed to move down.') % force_unicode(menu_item)
    request.user.message_set.create(message=msg)
    return HttpResponseRedirect(reverse('edit_menu', kwargs={ 'menu_pk': menu.pk }))
move_down_item = staff_member_required(never_cache(move_down_item))



def move_up_item(request, menu_pk, menu_item_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    menu_item = get_object_or_404(MenuItem, pk=menu_item_pk)
    
    if menu_item.rank > 0:
        move_item(menu_item, -1)
        msg = _('The menu item "%s" was moved successfully.') % force_unicode(menu_item)
    else:
        msg = _('The menu item "%s" is not allowed to move up.') % force_unicode(menu_item)
    request.user.message_set.create(message=msg)
    return HttpResponseRedirect(reverse('edit_menu', kwargs={ 'menu_pk': menu.pk }))
move_up_item = staff_member_required(never_cache(move_up_item))

