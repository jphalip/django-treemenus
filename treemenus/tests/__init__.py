import django

if django.VERSION < (1, 6):
    from test_treemenus import *