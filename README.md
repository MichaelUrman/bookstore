Bookstore
=========

A web bookstore implemention built for django.

Setup
-----

* Clone the latest copy from github into your django project. Don't do this yet unless you are masochistic, because it's not usable.
* Add the bookstore to your `INSTALLED_APPS` in `settings.py`:

        'bookstore',
    
* Add a url mapping to your project's `urls.py` file (an empty prefix will work, but put it last):

        (r'^bookstore/$', include('bookstore.urls')),

* Sync the database:

        % manage.py syncdb

Administration
--------------

Administration is easiest through the django admin interface. Start by adding an `Author`, a `Genre`, and a `Title`.