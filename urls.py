from django.conf.urls.defaults import *

urlpatterns = patterns('bookstore.views',
    (r'^$', 'storefront'),
    (r'^readme$', 'readme'),    # use to preview readme.md
    (r'^site/news/', 'site_news'),
    (r'^site/picks/', 'site_picks'),
    (r'^author/$', 'author_list'),
    (r'^author/(?P<author_link>[\w-]+)$', 'author_detail'),
    (r'^book/$', 'book_list'),
    (r'^book/(?P<book_link>[\w-]+)$', 'book_detail'),
    (r'^genre/$', 'genre_list'),
    (r'^genre/(?P<genre_link>[\w-]+)$', 'genre_detail'),
    (r'^sitemap.xml$', 'sitemap'),
    (r'^(?P<page_link>[\w-]+)$', 'site_page'),
)
