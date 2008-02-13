from django import newforms as forms

from models import Menu, MenuItem



class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        exclude = ('root_item',)
        
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        exclude = ('level', 'rank', 'menu')