from django.test import TestCase

from treemenus.models import Menu, MenuItem
from treemenus.utils import move_item, clean_ranks

class TreemenusTestCase(TestCase):

    def test_change_parents(self):
        menu = Menu(name='menu_change_parents')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu_item1)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu_item1)
        menu_item5 = MenuItem.objects.create(caption='menu_item5', parent=menu_item1)
        
        # menu
        #     ri
        #         mi1
        #             mi3
        #             mi4
        #             mi5
        #         mi2
        
        # Check initial ranks
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 1)
        self.assertEquals(menu_item3.rank, 0)
        self.assertEquals(menu_item4.rank, 1)
        self.assertEquals(menu_item5.rank, 2)
        
        # Check initial levels
        self.assertEquals(menu_item1.level, 1)
        self.assertEquals(menu_item2.level, 1)
        self.assertEquals(menu_item3.level, 2)
        self.assertEquals(menu_item4.level, 2)
        self.assertEquals(menu_item5.level, 2)

        # Change parent for some items
        menu_item4.parent = menu.root_item
        menu_item4.save()
        menu_item5.parent = menu_item2
        menu_item5.save()
        
        # menu
        #     ri
        #         mi1
        #             mi3
        #         mi2
        #             mi5
        #         mi4
        
        # Refetch items from db
        menu_item1 = MenuItem.objects.get(pk=menu_item1.pk)
        menu_item2 = MenuItem.objects.get(pk=menu_item2.pk)
        menu_item3 = MenuItem.objects.get(pk=menu_item3.pk)
        menu_item4 = MenuItem.objects.get(pk=menu_item4.pk)
        menu_item5 = MenuItem.objects.get(pk=menu_item5.pk)
        
        # Check ranks
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 1)
        self.assertEquals(menu_item3.rank, 0)
        self.assertEquals(menu_item4.rank, 2)
        self.assertEquals(menu_item5.rank, 0)
        
        # Check levels
        self.assertEquals(menu_item1.level, 1)
        self.assertEquals(menu_item2.level, 1)
        self.assertEquals(menu_item3.level, 2)
        self.assertEquals(menu_item4.level, 1)
        self.assertEquals(menu_item5.level, 2)

        # Change parent for some items
        menu_item2.parent = menu_item1
        menu_item2.save()
        menu_item5.parent = menu_item1
        menu_item5.save()
        menu_item3.parent = menu.root_item
        menu_item3.save()
        menu_item1.parent = menu_item4
        menu_item1.save()
        
        # menu
        #     ri
        #         mi4
        #             mi1
        #                 mi2
        #                 mi5
        #         mi3

        # Refetch items from db
        menu_item1 = MenuItem.objects.get(pk=menu_item1.pk)
        menu_item2 = MenuItem.objects.get(pk=menu_item2.pk)
        menu_item3 = MenuItem.objects.get(pk=menu_item3.pk)
        menu_item4 = MenuItem.objects.get(pk=menu_item4.pk)
        menu_item5 = MenuItem.objects.get(pk=menu_item5.pk)
        
        # Check ranks
        self.assertEquals(menu_item1.rank, 0)
        self.assertEquals(menu_item2.rank, 0)
        self.assertEquals(menu_item3.rank, 1)
        self.assertEquals(menu_item4.rank, 0)
        self.assertEquals(menu_item5.rank, 1)
        
        # Check levels
        self.assertEquals(menu_item1.level, 2)
        self.assertEquals(menu_item2.level, 3)
        self.assertEquals(menu_item3.level, 1)
        self.assertEquals(menu_item4.level, 1)
        self.assertEquals(menu_item5.level, 3)

        # Change parent for some items
        menu_item2.parent = menu_item4
        menu_item2.save()
        menu_item4.parent = menu_item3
        menu_item4.save()
        menu_item1.parent = menu.root_item
        menu_item1.save()
        menu_item5.parent = menu_item4
        menu_item5.save()
        
        # menu
        #     ri
        #         mi3
        #             mi4
        #                 mi2
        #                 mi5
        #         mi1

        # Refetch items from db
        menu_item1 = MenuItem.objects.get(pk=menu_item1.pk)
        menu_item2 = MenuItem.objects.get(pk=menu_item2.pk)
        menu_item3 = MenuItem.objects.get(pk=menu_item3.pk)
        menu_item4 = MenuItem.objects.get(pk=menu_item4.pk)
        menu_item5 = MenuItem.objects.get(pk=menu_item5.pk)
        
        # Check ranks
        self.assertEquals(menu_item1.rank, 1)
        self.assertEquals(menu_item2.rank, 0)
        self.assertEquals(menu_item3.rank, 0)
        self.assertEquals(menu_item4.rank, 0)
        self.assertEquals(menu_item5.rank, 1)
        
        # Check levels
        self.assertEquals(menu_item1.level, 1)
        self.assertEquals(menu_item2.level, 3)
        self.assertEquals(menu_item3.level, 1)
        self.assertEquals(menu_item4.level, 2)
        self.assertEquals(menu_item5.level, 3)


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
        
        # Test forbidden move up
        self.assertRaises(MenuItem.DoesNotExist, lambda: move_item(menu_item1, -1))

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
        
        # Test forbidden move up
        self.assertRaises(MenuItem.DoesNotExist, lambda: move_item(menu_item3, 1))
        
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
        