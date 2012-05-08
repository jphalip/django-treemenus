from django.utils.safestring import mark_safe
from django.forms import ChoiceField

from treemenus.models import MenuItem


class MenuItemChoiceField(ChoiceField):
    ''' Custom field to display the list of items in a tree manner '''
    def clean(self, value):
        return MenuItem.objects.get(pk=value)


def move_item(menu_item, vector):
    ''' Helper function to move and item up or down in the database '''
    old_rank = menu_item.rank
    swapping_sibling = MenuItem.objects.get(parent=menu_item.parent, rank=old_rank + vector)
    new_rank = swapping_sibling.rank
    swapping_sibling.rank = old_rank
    menu_item.rank = new_rank
    menu_item.save()
    swapping_sibling.save()


def move_item_or_clean_ranks(menu_item, vector):
    ''' Helper function to move and item up or down in the database.
        If the moving fails, we assume that the ranks were corrupted,
        so we clean them and try the moving again.
    '''
    try:
        move_item(menu_item, vector)
    except MenuItem.DoesNotExist:
        if menu_item.parent:
            clean_ranks(menu_item.parent.children())
            fresh_menu_item = MenuItem.objects.get(pk=menu_item.pk)
            move_item(fresh_menu_item, vector)


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
            if menu_item.has_children():
                for child in menu_item.children():
                    choices += get_flat_tuples(child, excepted_item)
            return choices

    return get_flat_tuples(menu.root_item, menu_item)


def clean_ranks(menu_items):
    """
    Resets ranks from 0 to n, n being the number of items.
    """
    rank = 0
    for menu_item in menu_items:
        menu_item.rank = rank
        menu_item.save()
        rank += 1
