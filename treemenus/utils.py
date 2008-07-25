from django.utils.safestring import mark_safe    

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
                    choices += get_flat_tuples(child, excepted_item)
            return choices
    
    return get_flat_tuples(menu.root_item, menu_item)



def clean_ranks(menu_items):
    rank = 0
    for menu_item in menu_items:
        menu_item.rank = rank
        menu_item.save()
        rank += 1