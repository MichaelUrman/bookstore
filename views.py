# bookstore views
from django.http import HttpResponse
from django.utils.html import escape, linebreaks
from django.shortcuts import render_to_response, get_object_or_404, redirect

from bookstore.models import Genre, Person, Book, SiteNewsBanner, SitePage, StorefrontNewsCard, StorefrontAd
from datetime import datetime
from random import choice

# HG mail: http://lillibridgepress.com:2096

class Pager:
    def __init__(self, request, count, pagesize=12):
        try: page = int(request.REQUEST.get("p", 0))
        except ValueError: page = 0
        try: size = int(request.REQUEST.get("c", pagesize))
        except ValueError: size = pagesize
        self.page = page
        self.size = size
        self.offset = size * page
        self.count = count
        self.pagecount = (count + size - 1) // size
        self.sizer = sizer = size != pagesize and "&c=%s" % size or ""
        self.slice = slice(self.offset, self.offset + size)

        self.next = (page * size + size < count) and ("?p=%s" % (page + 1) + sizer) or ""
        self.prev = (page > 0) and ("?p=%s" % (page - 1) + sizer) or ""

def storefront(request):
    cards = StorefrontNewsCard.objects.filter(visible=True).order_by("display_order")
    all_ads = StorefrontAd.objects.filter(visible=True).order_by("display_order")
    left_ads = all_ads.filter(column="L")
    center_ads = all_ads.filter(column="C")
    right_ads = all_ads.filter(column="R")
    try:
        site = SitePage.objects.get(frontpage=True)
    except SitePage.DoesNotExist:
        pass
    return render_to_response("bookstore/storefront.html", locals())

def sitemap(request):
    published_books = Book.objects.filter(visible=True, publish_date__lte=datetime.now).order_by("-publish_date")
    upcoming_books = Book.objects.filter(visible=True, publish_date__gt=datetime.now).order_by("publish_date")
    authors = Person.objects.filter(visible=True, author=True).order_by("lastname", "firstname")
    genres = Genre.objects.filter(visible=True).order_by("name")
    site_pages = SitePage.objects.filter(visible=True).order_by("display_order")
    return render_to_response("bookstore/sitemap.xml", locals())
    
def site_page(request, page_link):
    page = get_object_or_404(SitePage, link__iexact=page_link, visible=True)
    if page.link != page_link:
        return redirect(page, permanent=True)
    return render_to_response("bookstore/site_page.html", locals())
    
def readme(request):
    from os import path
    with open(path.join(path.dirname(path.realpath(__file__)), "README.md"), "rU") as f:
        text = f.read().decode("utf-8")

    try: import markdown
    except ImportError: html = linebreaks(escape(text))
    else: html = markdown.markdown(text)

    return render_to_response("bookstore/markdown.html", dict(content=html))

def site_news(request):
    newsbanners = SiteNewsBanner.objects.filter(visible=True).order_by("display_order")
    return render_to_response("bookstore/site_newsbanner.html", locals())

def choose(qs, choice=choice):
    if not qs: return None
    return choice(qs)

def site_picks(request):
    bestseller = choose(Book.objects.filter(visible=True, bestseller=True))
    feature = choose(Book.objects.filter(visible=True, feature=True).exclude(link__exact=bestseller.link))
    return render_to_response("bookstore/site_picks.html", locals())

def author_list(request):
    all_authors = Person.objects.filter(visible=True, author=True).order_by("lastname", "firstname")
    authorpager = Pager(request, all_authors.count(), pagesize=25)
    authors = all_authors[authorpager.slice]
    return render_to_response("bookstore/author_listing.html", locals())

def author_detail(request, author_link):
    author = get_object_or_404(Person, link__iexact=author_link, visible=True)
    if author.link != author_link:
        return redirect(author, permanent=True)
    all_books = author.book_set.filter(visible=True, publish_date__lte=datetime.now)
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    link = request.build_absolute_uri()
    return render_to_response("bookstore/author_detail.html", locals())

def book_list(request):
    all_books = Book.objects.filter(visible=True, publish_date__lte=datetime.now).order_by("title")
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    return render_to_response("bookstore/book_listing.html", locals())

def book_detail(request, book_link, migrate_url=False):
    book = get_object_or_404(Book, link__iexact=book_link, visible=True)
    if book.link != book_link or migrate_url:
        return redirect(book, permanent=True)
    return render_to_response("bookstore/book_detail.html", dict(book=book, link=request.build_absolute_uri()))

def genre_list(request):
    all_genres = Genre.objects.filter(visible=True).order_by("name")
    genrepager = Pager(request, all_genres.count(), pagesize=25)
    genres = all_genres[genrepager.slice]
    return render_to_response("bookstore/genre_listing.html", locals())

def genre_detail(request, genre_link):
    genre = get_object_or_404(Genre, link__iexact=genre_link, visible=True)
    if genre.link != genre_link:
        return redirect(genre, permanent=True)
    all_books = genre.book_set.filter(visible=True, publish_date__lte=datetime.now)
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    link = request.build_absolute_uri()
    return render_to_response("bookstore/genre_detail.html", locals())
