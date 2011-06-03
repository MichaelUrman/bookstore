from django.conf.urls.defaults import *

urlpatterns = patterns('bookstore.views',
    (r'^$', 'storefront'),
    (r'^readme$', 'readme'),
    (r'^genre/(?P<genre_name>\w+)$', 'genre_detail')
)
