from itertools import chain

from django.db import models
from django import newforms as forms
from django.newforms import IntegerField, Widget, HiddenInput
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from utils import clean_ranks, get_extension_model_class, MenuItemExtensionError





class MenuItem(models.Model):
    parent = models.ForeignKey('self', verbose_name=_('Parent'), null=True, blank=True)
    caption = models.CharField(_('Caption'), max_length=50)
    url = models.CharField(_('URL'), max_length=200, blank=True)
    named_url = models.CharField(_('Named URL'), max_length=200, blank=True)
    level = models.IntegerField(_('Level'), default=0, editable=False)
    rank = models.IntegerField(_('Rank'), default=0, editable=False)
    menu = models.ForeignKey('Menu', related_name='contained_items', verbose_name=_('Menu'), null=True, blank=True, editable=False)
    
    def __unicode__(self):
        return self.caption
    
    def save(self):
        if self.parent:
            if self.level != self.parent.level + 1:
                self.level = self.calcLevel() # The item has probably changed parent, so recalculate its level.

        if self.pk:
            new_parent = self.parent
            old_parent = MenuItem.objects.get(pk=self.pk).parent
            if old_parent != new_parent:
                #If so, we need to recalculate the new ranks for the item and its siblings (both old and new ones).
                if new_parent:
                    clean_ranks(new_parent.children()) # Clean ranks for new siblings
                    self.rank = new_parent.children().count()
                super(MenuItem, self).save() # Save menu item in DB. It has now officially changed parent.
                if old_parent:
                    clean_ranks(old_parent.children()) # Clean ranks for old siblings
            else:
                super(MenuItem, self).save() # Save menu item in DB
        
        else: # Saving the menu item for the first time (i.e creating the object)
            super(MenuItem, self).save()
    
    def delete(self):
        old_parent = self.parent
        super(MenuItem, self).delete()
        if old_parent:
            clean_ranks(old_parent.children())
    
    def clean_siblings_ranks(self):
        rank = 0
        for child in self.siblings():
            child.rank = rank
            child.save()
            rank += 1
        
    def caption_with_spacer(self):
        spacer = ''
        for i in range(0, self.level):
            spacer += u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        if self.level > 0:
            spacer += u'|-&nbsp;'
        return spacer + self.caption
    
    def calcLevel(self):
        if self.parent:
            return self.parent.level+1
        else:
            return 0
    
    def get_flattened(self):
        flat_structure = [self]
        for child in self.children():
            flat_structure = chain(flat_structure, child.get_flattened())
        return flat_structure
    
    def siblings(self):
        if not self.parent:
            return MenuItem.objects.none()
        else:
            if not self.pk: # If menu item not yet been saved in DB (i.e does not have a pk yet)
                return self.parent.children()
            else:
                return self.parent.children().exclude(pk=self.pk)
    
    def hasSiblings(self):
        return self.siblings().count() > 0
    
    def children(self):
        return MenuItem.objects.filter(parent=self).order_by('rank',)
    
    def hasChildren(self):
        return self.children().count() > 0
    
    def index(self):
        siblings = self.parent.children()
        i = -1
        for obj in siblings:
            if obj == self:
                return i+1
            else:
                i = i +1
        return -1

    def get_extension(self):
        """
        Returns an extension object for this menu item, that is, an object containing
        customized behaviour created by a developer using treemenus.
        The extension module class must be declared in the settings file with AUTH_PROFILE_MODULE.
        """
        if not hasattr(self, '_extension_cache'):
            extension_model_class = get_extension_model_class()
            self._extension_cache = extension_model_class._default_manager.get(menu_item__id__exact=self.id)
        return self._extension_cache


class Menu(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    root_item = models.ForeignKey(MenuItem, related_name='is_root_item_of', verbose_name=_('Root Item'), null=True, blank=True, editable=False)
    def save(self):
        if not self.root_item:
            root_item = MenuItem()
            root_item.caption = _('Root')
            root_item.level = 0
            if not self.pk: # If creating a new object (i.e does not have a pk yet)
                super(Menu, self).save() # Save, so that it gets a pk
            root_item.menu = self
            root_item.save() # Save, so that it gets a pk
            self.root_item = root_item
        super(Menu, self).save()

    def delete(self):
        if self.root_item is not None:
            self.root_item.delete()
        super(Menu, self).delete()
        
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Menu')
        verbose_name_plural = _('Menus')
        
    class Admin:
        pass
