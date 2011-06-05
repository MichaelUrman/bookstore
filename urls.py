from django.conf.urls.defaults import *

urlpatterns = patterns('bookstore.views',
    (r'^$', 'storefront'),
    (r'^readme$', 'readme'),    # use to preview readme.md
    (r'^author/$', 'author_list'),
    (r'^author/(?P<author_link>\w+)$', 'author_detail'),
    (r'^genre/$', 'genre_list'),
    (r'^genre/(?P<genre_link>\w+)$', 'genre_detail'),
)
