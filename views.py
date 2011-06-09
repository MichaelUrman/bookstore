# bookstore views
from django.http import HttpResponse
from django.utils.html import escape, linebreaks
from django.shortcuts import render_to_response, get_object_or_404, redirect

from bookstore.models import Genre, Person, Book, SiteNewsBanner
from datetime import datetime

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

        self.next = (page * size + size < count) and ("?p=%s" % (page + 1) + sizer) or ""
        self.prev = (page > 0) and ("?p=%s" % (page - 1) + sizer) or ""

def storefront(request):
    return render_to_response("bookstore/storefront.html")
    
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

def site_picks(request):
    return HttpResponse("<html><body><p>(site picks)</p></body></html>")

def author_list(request):
    return HttpResponse("TODO: not yet...")

def author_detail(request, author_link):
    author = get_object_or_404(Person, link__iexact=author_link)
    if author.link != author_link:
        return redirect(author, permanent=True)
    bookpager = Pager(request, 100)
    books = author.book_set.filter(visible=True).filter(publish_date__lte=datetime.now)
    link = request.build_absolute_uri()
    return render_to_response("bookstore/author_detail.html", locals())

def book_list(request):
    return HttpResponse("TODO: not yet...")

def book_detail(request, book_link):
    book = get_object_or_404(Book, link__iexact=book_link)
    if book.link != book_link:
        return redirect(book, permanent=True)
    return render_to_response("bookstore/book_detail.html", dict(book=book, link=request.build_absolute_uri()))

def genre_list(request):
    return HttpResponse("TODO: not yet...")

def genre_detail(request, genre_link):
    genre = get_object_or_404(Genre, link__iexact=genre_link)
    if genre.link != genre_link:
        return redirect(genre, permanent=True)
    bookpager = Pager(request, 100)
    books = genre.book_set.filter(visible=True).filter(publish_date__lte=datetime.now)
    link = request.build_absolute_uri()
    return render_to_response("bookstore/genre_detail.html", locals())
