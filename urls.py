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
    (r'^book/(?P<migrate_url>[^/]+)/(?P<book_link>[\w-]+)$', 'book_detail'), # migrate old urls
    (r'^signin/$', 'signin'),
    (r'^signout/$', 'signout'),
    (r'^purchase/book/(?P<pub_id>[^/]+)$', 'purchase_book'),
    (r'^user/(?P<user_id>[^/]*)$', 'user_detail'),
    (r'^user/purchases/$', 'purchase_listing'),
    (r'^user/purchases/(?P<purchase_id>[^/]+)/$', 'purchase_detail'),
    (r'^genre/$', 'genre_list'),
    (r'^genre/(?P<genre_link>[\w-]+)$', 'genre_detail'),
    (r'^sitemap.xml$', 'sitemap'),
    (r'^(?P<migrate_url>page/)(?P<page_link>[\w-]+)$', 'site_page'),
    (r'^(?P<page_link>[\w-]+)$', 'site_page'),
)
