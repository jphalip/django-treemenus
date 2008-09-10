import unittest

from treemenus.models import Menu, MenuItem
from treemenus.utils import move_item, clean_ranks

class TreemenusTestCase(unittest.TestCase):

    def test_move_up(self):
        menu = Menu(name='menu_move_up')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu.root_item)
        
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 1)
        self.assertEquals(menu_item3.rank, 2)
        self.assertEquals(menu_item4.rank, 3)

        move_item(menu_item3, -1) # Move up
        
        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)
        
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 2)
        self.assertEquals(menu_item3.rank, 1)
        self.assertEquals(menu_item4.rank, 3)

    def test_move_down(self):
        menu = Menu(name='menu_move_down')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu.root_item)
        
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 1)
        self.assertEquals(menu_item3.rank, 2)
        self.assertEquals(menu_item4.rank, 3)

        move_item(menu_item3, 1) # Move down
        
        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)
        
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 1)
        self.assertEquals(menu_item3.rank, 3)
        self.assertEquals(menu_item4.rank, 2)
        
    def test_clean_children_ranks(self):
        menu = Menu(name='menu_clean_children_ranks')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu.root_item)
        
        # Initial check
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 1)
        self.assertEquals(menu_item3.rank, 2)
        self.assertEquals(menu_item4.rank, 3)
        
        # Mess up ranks
        menu_item1.rank = 99
        menu_item1.save()
        menu_item2.rank = -150
        menu_item2.save()
        menu_item3.rank = 3
        menu_item3.save()
        menu_item4.rank = 67
        menu_item4.save()

        clean_ranks(menu.root_item.children())
        
        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)
        
        self.assertEquals(menu_item1.rank, 3)
        self.assertEquals(menu_item2.rank, 0)
        self.assertEquals(menu_item3.rank, 1)
        self.assertEquals(menu_item4.rank, 2)
        