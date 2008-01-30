=================
Django Tree-Menus
=================


This is a simple and generic tree-like menuing system for Django_ with an easy-to-use admin interface.

.. _Django: http://www.djangoproject.com/


Installation
============

Installing an official release
------------------------------

Official releases are made available from
http://code.google.com/p/django-tree-menus/

Download the .zip distribution file and unpack it. Inside is a script
named ``setup.py``. Enter this command::

   python setup.py install

...and the package will install automatically.

Installing the development version
----------------------------------

Alternatively, if you'd like to update Django Tree-Menus occasionally to pick
up the latest bug fixes and enhancements before they make it into an
official release, perform a Subversion checkout instead::

   svn checkout http://django-tree-menus.googlecode.com/svn/trunk/treemenus

Add the resulting folder to your PYTHONPATH or symlink (junction,
if you're on Windows) the ``treemenus`` directory inside it into a
directory which is on your PYTHONPATH, such as your Python
installation's ``site-packages`` directory.

Hooking Tree-Menus to your project
----------------------------------

1. Add ``treemenus`` to the ``INSTALLED_APPS`` setting of your
   Django project.

2. Add the treememus admin templates to the ``TEMPLATE_DIRS``::
    TEMPLATE_DIRS = (
        ...
        'treemenus/templates/',
    )

3. Modify your URLConf. Because the treemenus application contains some
   custom admin views, you need to declare its URL configuration before
   the admin's::

    (r'^admin/treemenus/', include('treemenus.admin_urls')),
    ...
    (r'^admin/', include('django.contrib.admin.urls')),

4. Add your custom templates to display the menus. See below.

Basic use
=========

To build a menu, log into the admin interface, and click "Menus" under
the Treemenus application section, then click "Add menu". Give your new
menu a name and then save.

To items into your new menu, click on it in the menu list. You will then see
a table in the bottom part of the page with only one item: the menu's root.
Click "Add an item", select its parent (obviously, since this is the first
item you're creating you can only select the root). Fill out the item's
details and click "Save". The new item now shows up in the table. You can
now create all the structure of your menu.

When you've finished building your menu from the admin interface, you will
have to write the appropriate templates to display the menu on your site.

Templates used by django-treemenus
==================================

The views included in django-treemenus make use of two templates. You need
to create your own templates into your template folder or any folder referenced
in the ``TEMPLATE_DIRS`` setting of your project.

``treemenus/menu.html``
-----------------------
To specify how to display a menu.

**Context:**

``menu``
    Pointer to the menu to display. You can access its root item with
    ``menu.root_item``.
    
``menu_type`` (optional)
    This variable will only be present if it has been specified when
    calling the ``show_menu`` template tag.

**Example of use**::

	{% ifequal menu_type "unordered-list" %}
	<ul>
		{% for menu_item in menu.root_item.children %}
			{% load tree_menu_tags %}
			{% show_menu_item menu_item %}
		{% endfor %}
	</ul>
	{% ifequal menu_type "ordered-list" %}
	<ol>
		{% for menu_item in menu.root_item.children %}
			{% load tree_menu_tags %}
			{% show_menu_item menu_item %}
		{% endfor %}
	</ol>
	{% endifequal %}


``treemenus/menu_item.html``
----------------------------
To specify how to display a menu item.

**Context:**

``menu_item``
    Pointer to the menu_item to display. You can directly access all
    its methods and variables.

``menu_type`` (optional)
    This variable will only be present if it has been specified when
    calling the ``show_menu`` template tag.

**Example of use**::


Template tags
=============

There a 3 template tags to let you display your menus. To be able to use them
you will first have to load the library they are contained in, with:

{% load tree_menu_tags %}

``show_menu``
-------------

This is the starting point. Call it whereever you want to display your menu
(most of the time it will be in your site's base template).

There are two parameters:

    * ``menu_name``: name of the menu to display
    * ``menu_type``: This parameter is optional. If it is given it is simply
                     passed to the ``treemenus/menu.html`` template. It does
                     not have any particular pre-defined function but can be
                     tested with (% ifequal menu_type "sometype" %} to
                     determine how to display the menu.

**Examples of use**::

    {% show_menu "TopMenu" %)
    {% show_menu "LeftMenu" "vertical" %)
    {% show_menu "RightMenu" "horizontal" %)

``show_menu_item``
------------------

This tag allows you to display a menu item, which is the only parameter.

**Example of use**::

    {% show_menu_item menu_item %}

``reverse_named_url``
---------------------

This tag allows you to reverse the named URL of a menu item, which is passed as a
single string. To know more about named URLs, refer to `the Django template documentation`_.
For example, the passed value could be 'latest_news' or 'show_profile user.id', and that
would be reversed to the corresponding URLs (as defined in your URLConf).

.. _the Django template documentation: http://www.djangoproject.com/documentation/templates/#url

**Example of use**::

	<li><a href="{% reverse_named_url menu_item.named_url %}">{{ menu_item.caption }}</a></li>

Fields and methods
==================

As you've guessed it you can manipulate two types of objects: menus and menu
items. In this section we present their fields and methods, which you can use
in your templates.

Menu
----

There is only one field that is available: ``root_item``, which points to...
you got it, the menu's root item.

Menu item
---------

``url``

Returns the item's url.

**Example of use**::
	<li><a href="{{ menu_item.url }}">{{ menu_item.caption }}</a></li>

``parent``

Returns the menu item's parent (that is, another menu item).

``login_required``

Returns True or False.

**Example of use**::

	{% if user.is_authenticated %}
	    {% if menu_item.login_required %}
	    	<li><a href="{{ menu_item.url }}">{{ menu_item.caption }}</a></li>
	    {% endif %}
	{% endif %}

``rank``

Returns the item's rank amongst its siblings. To change an item's ranking you can
move it up or down through the admin interface.

**Example of use**::

	<li><a class="menuitem-{{ menu_item.rank }}" href="{{ menu_item.url }}">{{ menu_item.caption }}</a></li>

``level``

Returns the item's level in the hierarchy. This is automatically calculated by
the system. For example, the root item has a level 0, and its children have a 
level one.

**Example of use**::

	{% ifequal menu_item.level 1 %}
	    <li><a class="top" href="{{ menu_item.url }}">{{ menu_item.caption }}</a></li>
	{% else %}
		<li><a href="{{ menu_item.url }}">{{ menu_item.caption }}</a></li>
	{% endifequal %}

``caption``

Returns the item's caption, which should be displayed on the page.

``named_url``

Use this parameter if you want to use named URLs instead of raw URLs.

**Example of use**::

    <li><a href="{% reverse_named_url menu_item.named_url %}">{{ menu_item.caption }}</a></li>

``hasChildren``

Returns True if the item has some children, False otherwise.

``children``

Returns the list of children.

**Example of use**::

	{% if menu_item.hasChildren %}
	    <li><a class="daddy" href="{{ menu_item.url }}">{{ menu_item.caption }}</a>
			<ul>
			    {% for child in menu_item.children %}
			        {% show_menu_item child %}
				{% endfor %}
			</ul>
		</li>
	{% else %}
		<li><a href="{{ menu_item.url }}">{{ menu_item.caption }}</a></li>
	{% endif %}
