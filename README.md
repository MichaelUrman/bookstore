Bookstore
=========

A web bookstore implemention built for django.

Setup
-----

* Clone the latest copy from github into your django project. Don't do this yet unless you are masochistic, because it's not usable.
* Add the bookstore to your `INSTALLED_APPS` in `settings.py`:

        'bookstore',
    
* Add a url mapping to your project's `urls.py` file (an empty prefix instead of `bookstore/` will work, but put it last):

        (r'^bookstore/$', include('bookstore.urls')),
        
* If you don't have them already, consider adding error handlers to your project's `urls.py` file as well:

        handler403 = 'bookstore.views.page_access_denied'
        handler404 = 'bookstore.views.page_not_found'
        handler500 = 'bookstore.views.page_server_error'

* Make sure you have a `MEDIA_ROOT` and `MEDIA_URL` set up in your `settings.py`:

        MEDIA_ROOT = '/home/www/mydjango-project/media/'
        
* Consider adding openid support. This requires [`python-openid`](https://github.com/openid/python-openid/downloads) and [`django_openid_auth`](https://launchpad.net/django-openid-auth/+download), with additional urls and settings. The quick and dirty options follow; see their installation instructions for full details.

        # in settings
        INSTALLED_APPS += 'django_openid_auth',
        
        AUTHENTICATION_BACKENDS = (
            'django_openid_auth.auth.OpenIDBackend',
            'django.contrib.auth.backends.ModelBackend',
        )
        
        OPENID_CREATE_USERS = True
        OPENID_UPDATE_DETAILS_FROM_SREG = True
        OPENID_UPDATE_DETAILS_FROM_AX = True
        LOGIN_URL = '/bookstore/signin/' # note, use the same prefix as for bookstore's url mapping
        LOGIN_REDIRECT_URL = '/'
        # OPENID_USE_AS_ADMIN_LOGIN = True # optional; use only once an openid has admin access
        
* Sync the database:

        % manage.py syncdb
        
* Provide css and images at `{{MEDIA_URL}}bookstore/style`. The files include `site.css`, `site_ie6.css`, `banner.jpg`, and `texel.png`. There's gotta be a better way for me to provide base versions of these, though...

Administration
--------------

Administration is easiest through the django admin interface. Start by adding an `Author`, a `Genre`, and a `Title`.