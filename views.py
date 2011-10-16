# bookstore views
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.html import escape, linebreaks
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition, require_POST
from django.db.models import Count

from bookstore.models import Genre, Person, Book, BookPublication
from bookstore.models import Purchase, MergedUser, PaypalIpn, Download
from bookstore.models import SiteNewsBanner, SitePage, StorefrontNewsCard, StorefrontAd
from django.contrib.auth.models import User

from datetime import datetime, timedelta
import logging
from random import choice
import urllib2

# HG mail: http://lillibridgepress.com:2096

PAYPAL = "https://www.sandbox.paypal.com/cgi-bin/webscr" # sandbox
# PAYPAL = "https://www.paypal.com/cgi-bin/webscr" # real

def get_migrated_object_or_404(model, migrate_values, **kwargs):
    """equivalent to get_object_or_404 with fallback checks per migrate_values mapping dict"""
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return get_object_or_404(model, **{k: migrate_values.get(v, v) for k, v in kwargs.items()})

def get_merged_purchases(user, **kwargs):
    for merged in MergedUser.objects.filter(accounts=user):
        return Purchase.objects.filter(customer__in=merged.accounts.all(), **kwargs)
    return Purchase.objects.filter(customer=user, **kwargs)

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

def _serve_purchase(request, purchase):
    # return the content of the download - serve the file
    from os import path
    pub = purchase.publication
    book = pub.book
    data = pub.data
    format = pub.format
    response = HttpResponse(data, content_type=format.mime)
    response["Content-Length"] = data.size
    response['Content-Disposition'] = 'attachment; filename=%s [%s].%s' % (book.title, book.publish_date.year, format.extension)
    Download.objects.create(purchase=purchase, ipaddress=request.META.get("REMOTE_ADDR"))
    return response

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
    root = request.build_absolute_uri("/").rstrip("/")
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
    feature = Book.objects.filter(visible=True, feature=True)
    if bestseller: feature = feature.exclude(link__exact=bestseller.link)
    feature = choose(feature)
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

def coming_soon(request):
    upcoming_books = Book.objects.filter(visible=True, upcoming=True, publish_date__gte=datetime.now).order_by("publish_date")
    bookpager = Pager(request, upcoming_books.count())
    if not bookpager.count:
        return redirect("bookstore.views.storefront", permanent=False)
    books = upcoming_books[bookpager.slice]
    return render_to_response("bookstore/coming_soon.html", locals())

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
    upcoming_books = genre.book_set.filter(visible=True, upcoming=True, publish_date__gte=datetime.now).order_by("publish_date")
    bookpager = Pager(request, all_books.count())
    books = all_books[bookpager.slice]
    link = request.build_absolute_uri()
    return render_to_response("bookstore/genre_detail.html", locals())

migrate_genres = dict(
    magic_occult="magick_occult",
)

try:
    import django_openid_auth.views as openid_views
except ImportError:
    openid_views = None
    
def openid_login(request):
    if not openid_views:
        raise Http404
    return openid_views.login_begin(request, template_name='bookstore/openid_login.html')

def openid_failure(request, message, status=403):
    return openid_views.default_render_failure(request, message, status, template_name='bookstore/openid_failure.html')

def openid_complete(request):
    if not openid_views:
        raise Http404
    return openid_views.login_complete(request, render_failure=openid_failure)

def signin(request, next='bookstore.views.storefront'):
    next = request.GET.get("next", next)
    login(request)
    return render_to_response("bookstore/signout.html", locals())

def signout(request, next='bookstore.views.storefront'):
    next = request.GET.get("next", next)
    logout(request)
    return redirect(next)
    return render_to_response("bookstore/signout.html", locals())

@login_required
def purchase_book(request, pub_id):
    pub = get_object_or_404(BookPublication, pk=pub_id)
    purchases = get_merged_purchases(request.user, publication=pub)
    try: purchased = purchases.filter(status='R').latest('date')
    except Purchase.DoesNotExist: pass
    try: submitted = purchases.filter(status='S').latest('date')
    except Purchase.DoesNotExist: pass
    del purchases
    
    LBP = request.build_absolute_uri().replace(request.get_full_path(), "")
    if not LBP:
        raise Http404

    book = pub.book
    status = 'P'
    transaction = 'P'
    free_purchase = book.is_free
    if free_purchase:
        transaction = 'F'
        status = 'R'
    bookprice = book.price_set.get(currency='USD')
    purchase = Purchase.objects.create(transaction=transaction,
                        price=bookprice.price,
                        currency=bookprice.currency,
                        publication=pub,
                        status=status,
                        customer=request.user,
                        email=request.user.email,
                        address=request.META['REMOTE_ADDR'],
                        email_sent=free_purchase)
    if free_purchase:
        return redirect(purchase.get_download_url())
    return render_to_response("bookstore/purchase_book.html", locals())

@login_required
def download_book(request, pub_id):
    pub = get_object_or_404(BookPublication, pk=pub_id)
    purchases = get_merged_purchases(request.user, publication=pub)
    book = pub.book
    
    # see if there's a ready purchase under this user's merged account
    try:
        purchase = purchases.filter(status='R').latest('date')
    except Purchase.DoesNotExist:
        # see if there's something pending or submitted; if so jump to purchase detail
        try:
            unready = purchases.filter(status='S').latest('date')
        except Purchase.DoesNotExist:
            # if nothing available, jump to opportunity to purchase the book
            book = pub.book
            return render_to_response("bookstore/download_unpurchased.html", locals())
        else:
            return redirect(unready, permanent=False)
    
    if purchase.is_available_to(request.user):
        return render_to_response("bookstore/download_ready.html", locals())
    return render_to_response("bookstore/download_limit.html", locals())
    
def download_review(request, purchase_id, key):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    pub = purchase.publication
    book = pub.book
    if purchase.transaction != 'V' or key != purchase.get_key():
        return HttpResponseNotFound()

    if purchase.is_available_to(request.user):
        return render_to_response("bookstore/download_ready.html", locals())
    return render_to_response("bookstore/download_limit.html", locals())
    

@require_POST
@csrf_exempt
@condition(etag_func=lambda req: get_object_or_404(BookPublication, pk=req.POST.get('pub')).get_etag())
def download_pub(request):
    purchase = get_object_or_404(Purchase, pk=request.POST.get('id'))
    if request.POST.get('key') == purchase.get_key() and purchase.status == 'R' \
        and purchase.is_available_to(request.user):
        return _serve_purchase(request, purchase)
    return HttpResponseForbidden()

@login_required
def purchase_listing(request):
    purchases = get_merged_purchases(request.user).order_by("-date")
    if not request.user.is_staff:
        purchases = purchases.filter(status__in="RS")
    return render_to_response("bookstore/purchase_listing.html", locals())

@login_required
def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    format = purchase.publication.format
    book = purchase.publication.book

    setstatus = request.POST.get('setstatus')
    if request.user.is_staff and setstatus:
        purchase.status = setstatus
        purchase.admin = request.user
        purchase.save()
        messages.add_message(request, messages.SUCCESS, 
            "Set purchase %(pid)s (%(title)s in %(format)s for %(customer)s) to %(status)s" % dict(
                pid=purchase_id, title=book.title, format=format.name,
                customer=purchase.customer.email, status=purchase.get_status_display()))
        return redirect(purchase, permanent=True)

    action = request.REQUEST.get('action')
    if not action:
        return render_to_response("bookstore/purchase_detail.html", locals(), context_instance=RequestContext(request))

    if purchase.status in 'PCS':
        if action == "cancelled":
            purchase.status = 'C'
            purchase.save()
            messages.add_message(request, messages.ERROR, "You have cancelled your purchase of %s in %s." % (purchase.publication.book.title, purchase.publication.format.name))
        elif action == "purchased":
            purchase.status = 'S'
            purchase.save()
            messages.add_message(request, messages.SUCCESS,
                "Thank you for purchasing %s in %s. We'll email you when your payment goes through." % (purchase.publication.book.title, purchase.publication.format.name))
        else:
            messages.add_message(request, messages.DEBUG, "Someone made an unexpected action request: %s" % action)
    return redirect(purchase, permanent=True)
    
@login_required
def user_detail(request, user_id=None):
    user = request.user
    if request.user.is_staff:
        users = User.objects.all()
        if user_id:
            user = User.objects.get(pk=user_id)
    purchases = get_merged_purchases(user).order_by("-date")
    bookshelf = (purchase.publication for purchase in purchases.filter(status='R'))
    return render_to_response("bookstore/user_detail.html", locals())

@require_POST
@csrf_exempt
def paypal_ipn(request):
    try:
        # Verify we have a matching purchase. If not there's no point verifying the request.
        purchase_id = request.POST.get('invoice')
        if not purchase_id.startswith('rlbp_'):
            logging.error("IPN: Invoice %s not found" % purchase_id)
            return HttpResponseNotFound("Invoice Not Found")

        purchase = get_object_or_404(Purchase, pk=purchase_id.strip('rlbp_'))

        # Then verify the parameters from PayPal.
        #params = str(request.raw_post_data)
        params = request.POST.urlencode()
        if not params:
            logging.error("IPN: No parameters")
            return HttpResponseBadRequest()

        confirm_request = urllib2.Request(PAYPAL, params + '&cmd=_notify-validate')
        confirm_request.add_header("Content-type", "application/x-www-form-urlencoded")
        confirm_response = urllib2.urlopen(confirm_request)
        confirm_content = confirm_response.read()
        if confirm_content != 'VERIFIED':
            logging.error("IPN: Paypal claims: %s", str(confirm_content)[:40])
            return HttpResponseForbidden("Unverified")

        # Continue onward if everything is good; record IPN parameters and verify payment amounts.
        ipn = PaypalIpn.objects.create(purchase=purchase, params=params,
            payment=(request.POST.get('payment_gross') or request.POST.get('mc_gross') or request.POST.get('mc_gross_1') or '0').strip('$'),
            currency=request.POST.get('mc_currency', 'USD'),
            payment_status=request.POST.get('payment_status'),
        )

        if purchase.price > ipn.payment:
            logging.error("IPN: Payment %s smaller than Price %s" % (ipn.payment, purchase.price))
            return HttpResponseBadRequest("Bad Payment")

        if ipn.payment_status == "Completed":
            if purchase.status != 'R' and request.POST.get('txn_type') in ('cart', 'express_checkout', 'masspay', 'virtual_terminal', 'web_accept'):
                purchase.status = 'R'
                if not purchase.email_sent:
                    purchase.email_name = request.POST.get('first_name') or request.POST.get('last_name') or 'Lillibridge Press Customer'
                    purchase.email_address = request.POST.get('payer_email') or purchase.customer.email
                    purchase.email_link = request.build_absolute_uri(purchase.get_download_url())
                purchase.save()

    except Exception:
        logging.exception("IPN")
        raise
    
    return HttpResponse("Ok")

def require_staff(view):
    def surrogate_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseNotFound()
        return view(request, *args, **kwargs)
    surrogate_view.__doc__ = view.__doc__
    return surrogate_view

@require_staff
def staff_purchase(request):
    user = request.REQUEST.get('user')
    if user:
        purchases = get_merged_purchases(User.get(pk=user))
    else:
        purchases = Purchase.objects.all()

    book = request.REQUEST.get('book')
    if book:
        purchases = purchases.filter(publication__book=Book.get(pk=book))
        
    status = request.REQUEST.get('status') or 'RSX'
    purchases = purchases.filter(status__in=status)
    
    sort = request.REQUEST.get('sort')
    if sort:
        purchases = purchases.annotate(downloads=Count('download')).order_by(sort.strip("+"))
        
    purchasepager = Pager(request, purchases.count(), pagesize=50)
    purchases = purchases[purchasepager.slice]
    
    toggle_pending = request.GET.copy()
    toggle_pending["status"] = ['RSX', 'PRSCX'][status == 'RSX']
    toggle_pending = '?' + toggle_pending.urlencode()

    return render_to_response("bookstore/staff_purchases.html", locals())
    
@require_staff
def staff_purchase_detail(request, purchase_id):
    purchase = Purchase.objects.get(pk=purchase_id)
    downloads = purchase.download_set.all()

    sort = request.REQUEST.get('sort')
    if sort:
        downloads = downloads.order_by(sort.strip("+"))
        
    downloadpager = Pager(request, downloads.count(), pagesize=50)
    downloads = downloads[downloadpager.slice]
    
    return render_to_response("bookstore/staff_purchase_detail.html", locals())
    
@require_staff
def staff_review(request):
    if request.POST.get("op") == "review":
        email = request.POST.get("email")
        name = request.POST.get("name")
        pub_id = request.POST.get("publication")
        publication = pub_id and BookPublication.objects.get(pk=pub_id)
        if email and name and publication:
            book = publication.book
            bookprice = book.price_set.get(currency='USD')
            purchase = Purchase.objects.create(transaction='V',
                                price=bookprice.price,
                                currency=bookprice.currency,
                                publication=publication,
                                status='P',
                                admin=request.user,
                                customer=request.user,
                                email=email,
                                email_name=name,
                                email_address=email,
                                address=request.META['REMOTE_ADDR'],
                                email_sent=False)
            purchase.status = 'R'
            purchase.email_link = request.build_absolute_uri(purchase.get_download_url())
            purchase.save()
            messages.add_message(request, messages.SUCCESS,
                "Sent review copy of %s (%s) to %s (%s)" % (publication.book.title, publication.format.name, name, email))
            return redirect(staff_review)
        
        if not email:
            messages.add_message(request, messages.ERROR, "Must specify Email")
        if not name:
            messages.add_message(request, messages.ERROR, "Must specify Name")
        if not publication:
            messages.add_message(request, messages.ERROR, "Must specify Book")
        
    books = Book.objects.all()
    return render_to_response("bookstore/staff_review.html", locals(), context_instance=RequestContext(request))