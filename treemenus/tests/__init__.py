import django

if django.VERSION < (1, 6):
    from treemenus.tests.test_treemenus import *