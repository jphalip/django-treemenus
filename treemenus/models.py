from itertools import chain

from django.db import models
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _


class MenuItem(models.Model):
    parent = models.ForeignKey('self', verbose_name=ugettext_lazy('parent'), null=True, blank=True)
    caption = models.CharField(ugettext_lazy('caption'), max_length=50)
    url = models.CharField(ugettext_lazy('URL'), max_length=200, blank=True)
    named_url = models.CharField(ugettext_lazy('named URL'), max_length=200, blank=True)
    level = models.IntegerField(ugettext_lazy('level'), default=0, editable=False)
    rank = models.IntegerField(ugettext_lazy('rank'), default=0, editable=False)
    menu = models.ForeignKey('Menu', related_name='contained_items', verbose_name=ugettext_lazy('menu'), null=True, blank=True, editable=False)

    def __str__(self):
        return self.caption

    def __unicode__(self):
        return self.caption

    def save(self, force_insert=False, **kwargs):
        from treemenus.utils import clean_ranks

        # Calculate level
        old_level = self.level
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0

        if self.pk:
            new_parent = self.parent
            old_parent = MenuItem.objects.get(pk=self.pk).parent
            if old_parent != new_parent:
                #If so, we need to recalculate the new ranks for the item and its siblings (both old and new ones).
                if new_parent:
                    clean_ranks(new_parent.children())  # Clean ranks for new siblings
                    self.rank = new_parent.children().count()
                super(MenuItem, self).save(force_insert, **kwargs)  # Save menu item in DB. It has now officially changed parent.
                if old_parent:
                    clean_ranks(old_parent.children())  # Clean ranks for old siblings
            else:
                super(MenuItem, self).save(force_insert, **kwargs)  # Save menu item in DB

        else:  # Saving the menu item for the first time (i.e creating the object)
            if not self.has_siblings():
                # No siblings - initial rank is 0.
                self.rank = 0
            else:
                # Has siblings - initial rank is highest sibling rank plus 1.
                siblings = self.siblings().order_by('-rank')
                self.rank = siblings[0].rank + 1
            super(MenuItem, self).save(force_insert, **kwargs)

        # If level has changed, force children to refresh their own level
        if old_level != self.level:
            for child in self.children():
                child.save()  # Just saving is enough, it'll refresh its level correctly.

    def delete(self, using=None):
        from treemenus.utils import clean_ranks
        old_parent = self.parent
        super(MenuItem, self).delete()
        if old_parent:
            clean_ranks(old_parent.children())

    def caption_with_spacer(self):
        spacer = ''
        for i in range(0, self.level):
            spacer += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        if self.level > 0:
            spacer += '|-&nbsp;'
        return '%s%s' % (spacer, self.caption)

    def get_flattened(self):
        flat_structure = [self]
        for child in self.children():
            flat_structure = chain(flat_structure, child.get_flattened())
        return flat_structure

    def siblings(self):
        if not self.parent:
            return MenuItem.objects.none()
        else:
            if not self.pk:  # If menu item not yet been saved in DB (i.e does not have a pk yet)
                return self.parent.children()
            else:
                return self.parent.children().exclude(pk=self.pk)

    def has_siblings(self):
        return self.siblings().count() > 0

    def children(self):
        _children = MenuItem.objects.filter(parent=self).order_by('rank',)
        for child in _children:
            child.parent = self  # Hack to avoid unnecessary DB queries further down the track.
        return _children

    def has_children(self):
        return self.children().count() > 0


class Menu(models.Model):
    name = models.CharField(ugettext_lazy('name'), max_length=50)
    root_item = models.ForeignKey(MenuItem, related_name='is_root_item_of', verbose_name=ugettext_lazy('root item'), null=True, blank=True, editable=False)

    def save(self, force_insert=False, **kwargs):
        if not self.root_item:
            root_item = MenuItem()
            root_item.caption = _('root')
            if not self.pk:  # If creating a new object (i.e does not have a pk yet)
                super(Menu, self).save(force_insert, **kwargs)  # Save, so that it gets a pk
                force_insert = False
            root_item.menu = self
            root_item.save()  # Save, so that it gets a pk
            self.root_item = root_item
        super(Menu, self).save(force_insert, **kwargs)

    def delete(self, using=None):
        if self.root_item is not None:
            self.root_item.delete()
        super(Menu, self).delete()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
