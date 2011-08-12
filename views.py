# bookstore views
from django.http import HttpResponse
from django.utils.html import escape, linebreaks
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.template import RequestContext

from bookstore.models import Genre, Person, Book, BookPublication, Purchase
from bookstore.models import SiteNewsBanner, SitePage, StorefrontNewsCard, StorefrontAd
from django.contrib.auth.models import User
from datetime import datetime
from random import choice

# HG mail: http://lillibridgepress.com:2096

def get_migrated_object_or_404(model, migrate_values, **kwargs):
    """equivalent to get_object_or_404 with fallback checks per migrate_values mapping dict"""
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return get_object_or_404(model, **{k: migrate_values.get(v, v) for k, v in kwargs.items()})

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
    
def site_page(request, page_link, migrate_url=False):
    page = get_migrated_object_or_404(SitePage, migrate_pages, link__iexact=page_link, visible=True)
    if page.link != page_link or migrate_url:
        return redirect(page, permanent=True)
    return render_to_response("bookstore/site_page.html", locals())

migrate_pages = dict(
    about="about-us",
)
    
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
    author = get_migrated_object_or_404(Person, migrate_authors, link__iexact=author_link, visible=True)
    if author.link != author_link:
        return redirect(author, permanent=True)
    all_books = author.book_set.filter(visible=True, publish_date__lte=datetime.now)
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    link = request.build_absolute_uri()
    return render_to_response("bookstore/author_detail.html", locals())

migrate_authors = {
    "DCPetterson": "DC_Petterson",
    "George_O%26Gorman": "George_OGorman",
}

def book_list(request):
    all_books = Book.objects.filter(visible=True, publish_date__lte=datetime.now).order_by("title")
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    return render_to_response("bookstore/book_listing.html", locals())

def book_detail(request, book_link, migrate_url=False):
    book = get_migrated_object_or_404(Book, migrate_books, link__iexact=book_link, visible=True)
    if book.link != book_link or migrate_url:
        return redirect(book, permanent=True)

    link = request.build_absolute_uri()
    return render_to_response("bookstore/book_detail.html", locals())

migrate_books = dict(
    Body_Servant_of_Aleops="The_Body_Servant_of_Aleops",
    magic_occult="magick_occult",
    myth="Myths_Tales",
    superhero="Superheroes",
    violin_s_cry="A_Violin_s_Cry",
)

def genre_list(request):
    all_genres = Genre.objects.filter(visible=True).order_by("name")
    genrepager = Pager(request, all_genres.count(), pagesize=25)
    genres = all_genres[genrepager.slice]
    return render_to_response("bookstore/genre_listing.html", locals())

def genre_detail(request, genre_link):
    genre = get_migrated_object_or_404(Genre, migrate_genres, link__iexact=genre_link, visible=True)
    if genre.link != genre_link:
        return redirect(genre, permanent=True)
    all_books = genre.book_set.filter(visible=True, publish_date__lte=datetime.now)
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    link = request.build_absolute_uri()
    return render_to_response("bookstore/genre_detail.html", locals())

migrate_genres = dict(
    magic_occult="magick_occult",
)

def signin(request, next='bookstore.views.storefront'):
    next = request.GET.get("next", next)
    login(request)
    return render_to_response("bookstore/signout.html", locals())

def signout(request, next='bookstore.views.storefront'):
    next = request.GET.get("next", next)
    logout(request)
    return render_to_response("bookstore/signout.html", locals())

@login_required
def purchase_book(request, pub_id):
    pub = get_object_or_404(BookPublication, pk=pub_id)
    LBP = request.build_absolute_uri().replace(request.get_full_path(), "")
    if not LBP:
        raise Http404

    book = pub.book
    bookprice = book.price_set.get(currency='USD')
    purchase = Purchase.objects.create(transaction='P',
                        price=bookprice.price,
                        currency=bookprice.currency,
                        publication=pub,
                        status='P',
                        customer=request.user,
                        email=request.user.email,
                        address=request.META['REMOTE_ADDR'])
    PAYPAL = "https://www.sandbox.paypal.com/cgi-bin/webscr" # sandbox
    # PAYPAL = "https://www.paypal.com/cgi-bin/webscr" # real
    return render_to_response("bookstore/purchase_book.html", locals())

@login_required
def purchase_listing(request):
    purchases = Purchase.objects.filter(customer=request.user).order_by("-date")
    return render_to_response("bookstore/purchase_listing.html", locals())

@login_required
def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    setstatus = request.POST.get('setstatus')
    if request.user.is_staff and setstatus:
        purchase.status = setstatus
        purchase.save()
        return redirect(purchase, permanent=True)

    action = request.REQUEST.get('action')
    if action == "cancelled":
        purchase.status = 'C'
        purchase.save()
    elif action == "purchased":
        purchase.status = 'S'
        purchase.save()
    elif not action:
        pub = purchase.publication
        book = pub.book
        return render_to_response("bookstore/purchase_detail.html", locals(), context_instance=RequestContext(request))
    return redirect(purchase, permanent=True)
    
@login_required
def user_detail(request, user_id=None):
    user = request.user
    if request.user.is_staff:
        users = User.objects.all()
        if user_id:
            user = User.objects.get(pk=user_id)
            purchases = Purchase.objects.filter(customer=user).order_by("-date")
    bookshelf = BookPublication.objects.filter(purchase__customer=user, purchase__status='R').order_by("-purchase__date")
    return render_to_response("bookstore/user_detail.html", locals())