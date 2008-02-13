
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings



class MenuItemExtensionNotAvailable(Exception):
    pass

class MenuItemExtensionFormNotAvailable(Exception):
    pass

def get_class(class_path):
    i = class_path.rfind('.')
    module_path, class_name = class_path[:i], class_path[i+1:]
    module = __import__(module_path, globals(), locals(), [class_name])
    return getattr(module, class_name)

def get_extension_model_class():
    #Todo: Test if the retrieved class is actually a Model class
    try:
        return get_class(settings.TREE_MENU_ITEM_EXTENSION_MODEL)
    except (ImportError, ImproperlyConfigured):
        raise MenuItemExtensionNotAvailable
    
def get_extension_form_class():
    #Todo: Test if the retrieved class is actually a Form (or ModelForm) class
    try:
        return get_class(settings.TREE_MENU_ITEM_EXTENSION_FORM)
    except (ImportError, ImproperlyConfigured):
        raise MenuItemExtensionFormNotAvailable


def clean_ranks(menu_items):
    rank = 0
    for menu_item in menu_items:
        menu_item.rank = rank
        menu_item.save()
        rank += 1