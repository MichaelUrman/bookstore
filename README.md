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
        
* Make sure you have a `MEDIA_ROOT` and `MEDIA_URL` set up in your `settings.py`:

        MEDIA_ROOT = '/home/www/mydjango-project/media/'

* Sync the database:

        % manage.py syncdb
        
* Provide css and images at `{{MEDIA_URL}}bookstore/style`. The files include `site.css`, `site_ie6.css`, `banner.jpg`, and `texel.png`. There's gotta be a better way for me to provide base versions of these, though...

Administration
--------------

Administration is easiest through the django admin interface. Start by adding an `Author`, a `Genre`, and a `Title`.