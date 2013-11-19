try:
    from imp import reload  # Python 3
except ImportError:
    pass
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.db.models.loading import load_app
from django import template
from django.template.loaders import app_directories
from django.contrib.auth.models import User

try:
    from django.utils.encoding import smart_bytes
except ImportError:  # Django < 1.5
    smart_bytes = str

from treemenus.models import Menu, MenuItem
from treemenus.utils import move_item, clean_ranks, move_item_or_clean_ranks


class TreemenusTestCase(TestCase):
    urls = 'treemenus.tests.urls'

    def setUp(self):
        # Install testapp
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS += ['treemenus.tests.fake_menu_extension']
        load_app('treemenus.tests.fake_menu_extension')
        call_command('syncdb', verbosity=0, interactive=False)

        # since django's r11862 templatags_modules and app_template_dirs are cached
        # the cache is not emptied between tests
        # clear out the cache of modules to load templatetags from so it gets refreshed
        template.templatetags_modules = []

        # clear out the cache of app_directories to load templates from so it gets refreshed
        app_directories.app_template_dirs = []
        # reload the module to refresh the cache
        reload(app_directories)
        # Log in as admin
        User.objects.create_superuser('super', 'super@test.com', 'secret')
        login = self.client.login(username='super', password='secret')
        self.assertEqual(login, True)

    def tearDown(self):
        # Restore settings
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS

    def test_view_add_item(self):
        menu_data = {
            "name": "menu12387640",
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/add/', menu_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/')

        menu = Menu.objects.order_by('-pk')[0]

        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "blah",
            "url": "http://www.example.com"
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk, menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        # Make sure the 'menu' attribute has been set correctly
        menu_item = menu.root_item.children()[0]
        self.assertEqual(menu_item.menu, menu)

        # Save and continue editing
        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "something0987456987546",
            "url": "http://www.example.com",
            "_continue": ''
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk, menu_item_data)
        new_menu_item = MenuItem.objects.order_by('-pk')[0]
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/items/%s/' % (menu.pk, new_menu_item.pk))

        # Save and add another
        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "something",
            "url": "http://www.example.com",
            "_addanother": ''
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk, menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk)

    def test_view_history_item(self):
        menu_data = {
            "name": "menu4578756856",
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/add/', menu_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/')

        menu = Menu.objects.order_by('-pk')[0]

        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "blah",
            "url": "http://www.example.com"
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk, menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        menu_item = menu.root_item.children()[0]

        # Delete item confirmation
        response = self.client.get('/test_treemenus_admin/treemenus/menu/%s/items/%s/history/' % (menu.pk, menu_item.pk))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(smart_bytes('Change history') in response.content)

    def test_view_delete_item(self):
        menu_data = {
            "name": "menu545468763498",
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/add/', menu_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/')

        menu = Menu.objects.order_by('-pk')[0]

        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "blah",
            "url": "http://www.example.com"
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk, menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        menu_item = menu.root_item.children()[0]

        # Delete item confirmation
        response = self.client.get('/test_treemenus_admin/treemenus/menu/%s/items/%s/delete/' % (menu.pk, menu_item.pk))
        self.assertEqual(response.request['PATH_INFO'], '/test_treemenus_admin/treemenus/menu/%s/items/%s/delete/' % (menu.pk, menu_item.pk))

        # Delete item for good
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/%s/delete/' % (menu.pk, menu_item.pk), {'post': 'yes'})
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item.pk))

    def test_view_change_item(self):
        # Add the menu
        menu_data = {
            "name": "menu87623598762345",
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/add/', menu_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/')

        menu = Menu.objects.order_by('-pk')[0]

        # Add the item
        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "blah",
            "url": "http://www.example.com"
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk, menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        menu_item = menu.root_item.children()[0]
        menu_item.menu = None  # Corrupt it!

        # Change the item
        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "something else",
            "url": "http://www.example.com"
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/%s/' % (menu.pk, menu_item.pk), menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        # Make sure the 'menu' attribute has been restored correctly
        menu_item = menu.root_item.children()[0]
        self.assertEqual(menu_item.menu, menu)

        # Save and continue editing
        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "something else",
            "url": "http://www.example.com",
            "_continue": ''
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/%s/' % (menu.pk, menu_item.pk), menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/items/%s/' % (menu.pk, menu_item.pk))

        # Save and add another
        menu_item_data = {
            "parent": menu.root_item.pk,
            "caption": "something else",
            "url": "http://www.example.com",
            "_addanother": ''
        }
        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/%s/' % (menu.pk, menu_item.pk), menu_item_data)
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/items/add/' % menu.pk)

    def test_delete(self):
        menu = Menu(name='menu_delete')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu_item1)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu_item1)
        menu_item5 = MenuItem.objects.create(caption='menu_item5', parent=menu_item1)
        menu_item6 = MenuItem.objects.create(caption='menu_item6', parent=menu_item2)
        menu_item7 = MenuItem.objects.create(caption='menu_item7', parent=menu_item4)
        menu_item8 = MenuItem.objects.create(caption='menu_item8', parent=menu_item4)
        menu_item9 = MenuItem.objects.create(caption='menu_item9', parent=menu_item1)
        menu_item10 = MenuItem.objects.create(caption='menu_item10', parent=menu_item4)

        # menu
        #     ri
        #         mi1
        #             mi3
        #             mi4
        #                 mi7
        #                 mi8
        #                 mi10
        #             mi5
        #             mi9
        #         mi2
        #             mi6

        # Check initial ranks
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 0)
        self.assertEqual(menu_item4.rank, 1)
        self.assertEqual(menu_item5.rank, 2)
        self.assertEqual(menu_item6.rank, 0)
        self.assertEqual(menu_item7.rank, 0)
        self.assertEqual(menu_item8.rank, 1)
        self.assertEqual(menu_item9.rank, 3)
        self.assertEqual(menu_item10.rank, 2)

        # Check initial levels
        self.assertEqual(menu_item1.level, 1)
        self.assertEqual(menu_item2.level, 1)
        self.assertEqual(menu_item3.level, 2)
        self.assertEqual(menu_item4.level, 2)
        self.assertEqual(menu_item5.level, 2)
        self.assertEqual(menu_item6.level, 2)
        self.assertEqual(menu_item7.level, 3)
        self.assertEqual(menu_item8.level, 3)
        self.assertEqual(menu_item9.level, 2)
        self.assertEqual(menu_item10.level, 3)

        # Delete some items
        menu_item8.delete()
        menu_item3.delete()

        # menu
        #     ri
        #         mi1
        #             mi4
        #                 mi7
        #                 mi10
        #             mi5
        #             mi9
        #         mi2
        #             mi6

        # Refetch items from db
        menu_item1 = MenuItem.objects.get(pk=menu_item1.pk)
        menu_item2 = MenuItem.objects.get(pk=menu_item2.pk)
        menu_item4 = MenuItem.objects.get(pk=menu_item4.pk)
        menu_item5 = MenuItem.objects.get(pk=menu_item5.pk)
        menu_item6 = MenuItem.objects.get(pk=menu_item6.pk)
        menu_item7 = MenuItem.objects.get(pk=menu_item7.pk)
        menu_item9 = MenuItem.objects.get(pk=menu_item9.pk)
        menu_item10 = MenuItem.objects.get(pk=menu_item10.pk)

        # Check ranks
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item4.rank, 0)
        self.assertEqual(menu_item5.rank, 1)
        self.assertEqual(menu_item6.rank, 0)
        self.assertEqual(menu_item7.rank, 0)
        self.assertEqual(menu_item9.rank, 2)
        self.assertEqual(menu_item10.rank, 1)

        # Check levels
        self.assertEqual(menu_item1.level, 1)
        self.assertEqual(menu_item2.level, 1)
        self.assertEqual(menu_item4.level, 2)
        self.assertEqual(menu_item5.level, 2)
        self.assertEqual(menu_item6.level, 2)
        self.assertEqual(menu_item7.level, 3)
        self.assertEqual(menu_item9.level, 2)
        self.assertEqual(menu_item10.level, 3)

        # Delete some items
        menu_item4.delete()
        menu_item5.delete()

        # menu
        #     ri
        #         mi1
        #             mi9
        #         mi2
        #             mi6

        # Refetch items from db
        menu_item1 = MenuItem.objects.get(pk=menu_item1.pk)
        menu_item2 = MenuItem.objects.get(pk=menu_item2.pk)
        menu_item6 = MenuItem.objects.get(pk=menu_item6.pk)
        menu_item9 = MenuItem.objects.get(pk=menu_item9.pk)

        # Check ranks
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item6.rank, 0)
        self.assertEqual(menu_item9.rank, 0)

        # Check levels
        self.assertEqual(menu_item1.level, 1)
        self.assertEqual(menu_item2.level, 1)
        self.assertEqual(menu_item6.level, 2)
        self.assertEqual(menu_item9.level, 2)

        # Check that deleted items are in fact, gone.
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item3.pk))
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item4.pk))
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item5.pk))
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item7.pk))
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item8.pk))
        self.assertRaises(MenuItem.DoesNotExist, lambda: MenuItem.objects.get(pk=menu_item10.pk))

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
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 0)
        self.assertEqual(menu_item4.rank, 1)
        self.assertEqual(menu_item5.rank, 2)

        # Check initial levels
        self.assertEqual(menu_item1.level, 1)
        self.assertEqual(menu_item2.level, 1)
        self.assertEqual(menu_item3.level, 2)
        self.assertEqual(menu_item4.level, 2)
        self.assertEqual(menu_item5.level, 2)

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
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 0)
        self.assertEqual(menu_item4.rank, 2)
        self.assertEqual(menu_item5.rank, 0)

        # Check levels
        self.assertEqual(menu_item1.level, 1)
        self.assertEqual(menu_item2.level, 1)
        self.assertEqual(menu_item3.level, 2)
        self.assertEqual(menu_item4.level, 1)
        self.assertEqual(menu_item5.level, 2)

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
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 0)
        self.assertEqual(menu_item3.rank, 1)
        self.assertEqual(menu_item4.rank, 0)
        self.assertEqual(menu_item5.rank, 1)

        # Check levels
        self.assertEqual(menu_item1.level, 2)
        self.assertEqual(menu_item2.level, 3)
        self.assertEqual(menu_item3.level, 1)
        self.assertEqual(menu_item4.level, 1)
        self.assertEqual(menu_item5.level, 3)

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
        self.assertEqual(menu_item1.rank, 1)
        self.assertEqual(menu_item2.rank, 0)
        self.assertEqual(menu_item3.rank, 0)
        self.assertEqual(menu_item4.rank, 0)
        self.assertEqual(menu_item5.rank, 1)

        # Check levels
        self.assertEqual(menu_item1.level, 1)
        self.assertEqual(menu_item2.level, 3)
        self.assertEqual(menu_item3.level, 1)
        self.assertEqual(menu_item4.level, 2)
        self.assertEqual(menu_item5.level, 3)

    def test_move_up(self):
        menu = Menu(name='menu_move_up')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 2)
        self.assertEqual(menu_item4.rank, 3)

        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/%s/move_up/' % (menu.pk, menu_item3.pk))
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 2)
        self.assertEqual(menu_item3.rank, 1)
        self.assertEqual(menu_item4.rank, 3)

        # Test forbidden move up
        self.assertRaises(MenuItem.DoesNotExist, lambda: move_item(menu_item1, -1))

    def test_move_down(self):
        menu = Menu(name='menu_move_down')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 2)
        self.assertEqual(menu_item4.rank, 3)

        response = self.client.post('/test_treemenus_admin/treemenus/menu/%s/items/%s/move_down/' % (menu.pk, menu_item3.pk))
        self.assertRedirects(response, '/test_treemenus_admin/treemenus/menu/%s/' % menu.pk)

        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 3)
        self.assertEqual(menu_item4.rank, 2)

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
        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 2)
        self.assertEqual(menu_item4.rank, 3)

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

        self.assertEqual(menu_item1.rank, 3)
        self.assertEqual(menu_item2.rank, 0)
        self.assertEqual(menu_item3.rank, 1)
        self.assertEqual(menu_item4.rank, 2)

    def test_move_item_or_clean_ranks(self):
        menu = Menu(name='menu_move_item_or_clean_ranks')
        menu.save()
        menu_item1 = MenuItem.objects.create(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.create(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.create(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.create(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 1)
        self.assertEqual(menu_item3.rank, 2)
        self.assertEqual(menu_item4.rank, 3)

        # Corrupt ranks
        menu_item1.rank = 0
        menu_item1.save()
        menu_item2.rank = 0
        menu_item2.save()
        menu_item3.rank = 0
        menu_item3.save()
        menu_item4.rank = 0
        menu_item4.save()

        move_item_or_clean_ranks(menu_item3, -1)  # Move up

        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 0)
        self.assertEqual(menu_item2.rank, 2)
        self.assertEqual(menu_item3.rank, 1)
        self.assertEqual(menu_item4.rank, 3)

        # Corrupt ranks
        menu_item1.rank = 18
        menu_item1.save()
        menu_item2.rank = -1
        menu_item2.save()
        menu_item3.rank = 6
        menu_item3.save()
        menu_item4.rank = 99
        menu_item4.save()

        move_item_or_clean_ranks(menu_item1, 1)  # Try to move down

        # Retrieve objects from db
        menu_item1 = MenuItem.objects.get(caption='menu_item1', parent=menu.root_item)
        menu_item2 = MenuItem.objects.get(caption='menu_item2', parent=menu.root_item)
        menu_item3 = MenuItem.objects.get(caption='menu_item3', parent=menu.root_item)
        menu_item4 = MenuItem.objects.get(caption='menu_item4', parent=menu.root_item)

        self.assertEqual(menu_item1.rank, 3)
        self.assertEqual(menu_item2.rank, 0)
        self.assertEqual(menu_item3.rank, 1)
        self.assertEqual(menu_item4.rank, 2)

    def test_menu_create(self):
        # Regression test for issue #18
        # http://code.google.com/p/django-treemenus/issues/detail?id=18
        menu = Menu.objects.create(name="menu_created_with_force_insert_True")
