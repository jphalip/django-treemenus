
from django.db import models
from treemenus.models import MenuItem

class MenuItemExtension(models.Model):
    menu_item = models.OneToOneField (MenuItem, related_name="extension")
    published = models.BooleanField(default=False)