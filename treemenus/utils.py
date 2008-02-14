from django.conf import settings
from django.db.models.base import ModelBase
from django.newforms.models import ModelFormMetaclass
from config import APP_LABEL

class MenuItemExtensionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_class(class_path):
    i = class_path.rfind('.')
    module_path, class_name = class_path[:i], class_path[i+1:]
    module = __import__(module_path, globals(), locals(), [class_name])
    return getattr(module, class_name)

def get_extension_model_class():
    if not hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_MODEL'):
        raise MenuItemExtensionError, 'Could not find the setting TREE_MENU_ITEM_EXTENSION_MODEL.'
    else:
        extension_class_path = settings.TREE_MENU_ITEM_EXTENSION_MODEL
    
    try:
        extension_class = get_class(extension_class_path)
    except (ImportError, AttributeError):
        raise MenuItemExtensionError, 'Class path incorrect: "%s" for TREE_MENU_ITEM_EXTENSION_MODEL setting. Check that you typed it correctly and that it is visible through your PYTHON_PATH.' % extension_class_path
    
    if not isinstance(extension_class, ModelBase):
        raise MenuItemExtensionError, '"%s" should be a Django model class.' % extension_class_path
    
    forbidden_fields = ['caption', 'level', 'menu', 'named_url', 'parent', 'rank', 'url']
    menu_item_attr_found = False
    for field in extension_class._meta.fields:
        if field.name == 'menu_item':
            menu_item_attr_found = True
        if field.name in forbidden_fields:
            raise MenuItemExtensionError, '%s is not allowed to contain an attribute with a name from this list: %s' % (extension_class_path, forbidden_fields)
    
    if not menu_item_attr_found:
        raise MenuItemExtensionError, '"%s" must contain an attribute named "menu_item", which is a unique ForeignKey reference to the class "%s.model.MenuItem".' % (extension_class_path, APP_LABEL)
    
    return extension_class
    
def get_extension_form_class():
    if not hasattr(settings, 'TREE_MENU_ITEM_EXTENSION_FORM'):
        raise MenuItemExtensionError, 'Could not find the setting TREE_MENU_ITEM_EXTENSION_FORM.'
    else:
        extension_form_class_path = settings.TREE_MENU_ITEM_EXTENSION_FORM
    
    try:
        extension_form_class = get_class(extension_form_class_path)
    except (ImportError, AttributeError):
        raise MenuItemExtensionError, 'Class path incorrect: "%s" for TREE_MENU_ITEM_EXTENSION_FORM setting. Check that you typed it correctly and that it is visible through your PYTHON_PATH.' % extension_form_class_path
    if not isinstance(extension_form_class, ModelFormMetaclass):
        raise MenuItemExtensionError, '"%s" should extend ModelForm.' % extension_form_class_path
    return extension_form_class
    
    


def clean_ranks(menu_items):
    rank = 0
    for menu_item in menu_items:
        menu_item.rank = rank
        menu_item.save()
        rank += 1