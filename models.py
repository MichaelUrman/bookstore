from django.db import models
from django.core.files import File
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decimal import Decimal, ROUND_UP

import cgi
from datetime import datetime, date
from os import path
import sha
import logging

# HACK: make it possible to identify openiduser records in the admin interface.
def user_unicode(self):
    return "%s (%s)" % (self.username, self.email)
User.__unicode__ = user_unicode

# TODO:
# consider dijit.Editor instead of minifmt: http://lazutkin.com/blog/2011/mar/13/using-dojo-rich-editor-djangos-admin/

CURRENCY = (
    ('USD', 'US Dollar'),
    ('GBP', 'British Pound'),
    ('EUR', 'Euro'),
    ('CAD', 'Canada Dollar'),
    ('AUD', 'Australian Dollar'),
)

CURRENCY_SYMBOLS = dict(USD='$', GBP=u'\u00a3', EUR=u'\u20ac', CAD='(CA) $', AUD='(AU) $')

# Base models
class Genre(models.Model):
    link = models.SlugField("Genre Link", max_length=200, unique=True, help_text="Address: /genre/[LINK]")
    name = models.CharField("Genre Name", max_length=200, unique=True, help_text="Name of genre")
    blurb = models.CharField("Genre Blurb", max_length=500, help_text="Short description shown in tooltip")
    visible = models.BooleanField("Visible", help_text="Show this genre in the store")
    display_order = models.IntegerField("Order", default=100, help_text="Show genres in this order")
    description = models.TextField("Description", help_text="Long description shown on genre's page")
    text_color = models.SlugField("Text Color", help_text="Color of text on genre's image")
    page_color = models.SlugField("Page Color", help_text="Color of background on genre's image")
    page_image = models.ImageField(upload_to='bookstore/img/genre')
    metakeywords = models.TextField("Page Keywords", blank=True)
    metadescription = models.TextField("Page Description", blank=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.link)

    @models.permalink
    def get_absolute_url(self):
        return ('bookstore.views.genre_detail', (), dict(genre_link=self.link))

class MergedUser(models.Model):
    name = models.CharField(max_length=200)
    accounts = models.ManyToManyField(User, related_name='+')

class Person(models.Model):
    link = models.SlugField("Author Link", max_length=200, unique=True, help_text="Address: /author/[LINK]")
    firstname = models.CharField("First Name", max_length=100)
    lastname = models.CharField("Last Name", max_length=100)
    email = models.EmailField("Email Address", max_length=255, unique=True)
    metakeywords = models.TextField("Page Keywords", blank=True, help_text="Useful only for Visible Authors")
    metadescription = models.TextField("Page Description", blank=True, help_text="Useful only for Visible Authors")
    biography = models.TextField("Biography", help_text="Useful only for Visible Authors")

    author = models.BooleanField("Is Author", help_text="Make this person available to be a Book Author")
    editor = models.BooleanField("Is Editor", help_text="Make this person available to be an Editor")
    visible = models.BooleanField("Visible", help_text="Show this author in the store")
    modified = models.DateTimeField(auto_now=True)
    rank = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ["lastname", "firstname"]
        verbose_name_plural = "People"

    def __unicode__(self):
        return "%s, %s <%s>" % (self.lastname, self.firstname, self.email)

    @models.permalink
    def get_absolute_url(self):
        return ('bookstore.views.author_detail', (), dict(author_link=self.link))

class Book(models.Model):
    link = models.SlugField("Book Link", max_length=200, unique=True, help_text="Book: /book/[LINK]")
    isbn = models.CharField("ISBN", max_length=50, blank=True, help_text="ISBN, if available")
    lbpn = models.CharField("LBPN", max_length=50, blank=True, help_text="LBPN, if available")
    size = models.CharField("Size", max_length=50, choices=(
        ('Free Read', 'Free Read'),
        ('Short Fiction', 'Short Fiction (2,500 to 7,500 words)'),
        ('Novelette', 'Novelette (7,500 to 17,500 words)'),
        ('Novella', 'Novella (17,500 to 40,000 words)'),
        ('Novel', 'Novel (40,000 to 100,000 words)'),
    ))
    title = models.CharField("Title", max_length=200)
    blurb = models.TextField("Blurb", help_text="Short description of the book shown in search results")
    description = models.TextField("Description", help_text="Description shown on the book's page")
    page_image = models.ImageField(upload_to='bookstore/img/book', help_text="Generally a 400x600 image of the book's cover")
    page_image_small = models.ImageField(upload_to='bookstore/img/book', help_text="Generally a 150x225 version of the book's cover")
    added_date = models.DateField("Date added")
    publish_date = models.DateField("Date published", help_text="Consider as an upcoming book until this date; an available book thereafter.")
    ero_rating = models.CharField("Heat Rating", max_length=20, choices=(
        ('Young Adult', 'Young Adult (safe for ages 14 to 21)'),
        ('Smolder', 'Smolder (non-consummated sex scenes)'),
        ('Smoke', 'Smoke (sensual and euphemistic sex scenes)'),
        ('Burn', 'Burn (sensual and explict, graphic, direct)'),
        ('Blaze', 'Blaze (frequent, explict, graphic, frank)'),
        ('Inferno', 'Inferno (quite frequent, explict, graphic, frank, or objectionable)'),
    ))
    authors = models.ManyToManyField(Person, limit_choices_to={"author": True})
    genres = models.ManyToManyField(Genre)
    visible = models.BooleanField("Visible", help_text="Show this book in the store")
    metakeywords = models.TextField("Page Keywords", blank=True, help_text="Useful only for Visible Authors")
    metadescription = models.TextField("Page Description", blank=True, help_text="Useful only for Visible Authors")
    upcoming = models.BooleanField(default=True, help_text="Include in upcoming lists if Publish Date is in the future")
    feature = models.BooleanField(default=False, help_text="Include this book as a potential featured item")
    bestseller = models.BooleanField(default=False, help_text="Include this book as a potential bestseller")
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-added_date"]

    def __unicode__(self):
        return "%s, a %s (%s)" % (self.title, self.size, self.link)

    @models.permalink
    def get_absolute_url(self):
        return ('bookstore.views.book_detail', (), dict(book_link=self.link))

    @property
    def is_published(self):
        return self.publish_date <= date.today()

    @property
    def price(self, quantum=Decimal('.01')):
        for price in self.price_set.filter(currency='USD'):
            return "%s%s" % (price.symbol, price.price.quantize(quantum, rounding=ROUND_UP))
        return 'ERROR'

    @property
    def is_free(self):
        return self.price == "$0.00" or self.price.upper() == "FREE"

    def publications_by_format(self):
        return self.bookpublication_set.filter(format__visible=True).order_by('format__display_order').all()

    def listings_by_reseller(self):
        return self.booklisting_set.filter(reseller__visible=True).order_by('reseller__display_order').all()

class BookPrice(models.Model):
    book = models.ForeignKey(Book, related_name="price_set")
    price = models.DecimalField(max_digits=10, decimal_places=3, help_text="Price to display on the book's page")
    currency = models.CharField(max_length=5, default='USD', choices=CURRENCY, help_text="Currency for book's price")
    @property
    def symbol(self, symbols=CURRENCY_SYMBOLS):
        return symbols[self.currency]

    class Meta:
        unique_together = ("book", "currency")
        
    def __unicode__(self):
        return "%s%s" % (self.symbol, self.price)

class BookReview(models.Model):
    book = models.ForeignKey(Book)
    quote = models.TextField()
    reviewer = models.TextField()
    date = models.DateField()

    class Meta:
        ordering = ["-date"]

    def __unicode__(self):
        return "%s by %s on %s" % (self.book.title, self.reviewer, self.date)

class BookMedia(models.Model):
    book = models.ForeignKey(Book)
    writeup = models.TextField()
    video_size = models.CharField("Video Size", max_length=20, choices=(
        ('500x405', "500 by 405"),
        ('480x385', "480 by 385"),
    ))
    youtube = models.CharField("Youtube Video Key", max_length=50, blank=True)

    def __unicode__(self):
        return "%s %s (%s)" % (self.book.title, self.video_size, self.youtube)
        
    def clean(self):
        youtube = self.youtube
        if youtube:
            if '/v/' in youtube:
                youtube = youtube[youtube.find('/v/') + 3:]
            elif 'v=' in youtube:
                youtube = youtube[youtube.find('v=') + 2:]
            for c in '/?&;':
                if c in youtube:
                    youtube = youtube[:youtube.find(c)]
            self.youtube = youtube
        return models.Model.clean(self)

class BookWallpaper(models.Model):
    book = models.ForeignKey(Book)
    wallpaper = models.ImageField(upload_to='bookstore/img/wall', width_field="wallwidth", height_field="wallheight", help_text="Try to include the largest of any of these size groups. There's no need to include more than one.\n16x10: 1920x1200, 1440x900, 1280x800\n4x3: 1600x1200, 1024x768\n16x9: 1920x1080\n5x4: 1280x1024")
    thumbnail = models.ImageField(upload_to='bookstore/img/wall', width_field="thumbwidth", height_field="thumbheight", help_text="Automatically generated if not provided")
    wallwidth = models.IntegerField()
    wallheight = models.IntegerField()
    thumbwidth = models.IntegerField(default=0)
    thumbheight = models.IntegerField(default=0)
    
    def __unicode__(self):
        return "%s at %dx%d" % (self.book.title, self.wallwidth, self.wallheight)

class BookFormat(models.Model):
    name = models.CharField(max_length=200, unique=True)
    blurb = models.CharField(max_length=500)
    extension = models.SlugField(max_length=10)
    mime = models.CharField(max_length=100)
    display_order = models.IntegerField()
    image = models.ImageField(upload_to='bookstore/img/fmt', width_field="width", height_field="height")
    width = models.IntegerField()
    height = models.IntegerField()
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s (*.%s), %s" % (self.name, self.extension, self.mime)

class BookPublication(models.Model):
    book = models.ForeignKey(Book)
    format = models.ForeignKey(BookFormat)
    data = models.FileField(upload_to='bookstore/ebook/%Y')

    @models.permalink
    def get_purchase_url(self):
        return ('bookstore.views.purchase_book', (), dict(pub_id=self.id))

    @models.permalink
    def get_download_url(self):
        return ('bookstore.views.download_book', (), dict(pub_id=self.id))

    class Meta:
        unique_together = ("book", "format")

    def __unicode__(self):
        return "%s in %s" % (self.book.title, self.format.name)
        
    def get_etag(self):
        return sha.new(str(self.book.title) + str(path.getmtime(self.data.path))).hexdigest()

class BookReseller(models.Model):
    name = models.CharField(max_length=200, unique=True)
    display_order = models.IntegerField()
    image = models.ImageField(upload_to='bookstore/img/sell', width_field="width", height_field="height")
    width = models.IntegerField()
    height = models.IntegerField()
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return self.name

class BookListing(models.Model):
    book = models.ForeignKey(Book)
    reseller = models.ForeignKey(BookReseller)
    url = models.URLField(verify_exists=False)
    
    class Meta:
        unique_together = ("book", "reseller")

    def __unicode__(self):
        return "%s at %s" % (self.book.title, self.reseller.name)

class SiteNewsBanner(models.Model):
    display_order = models.IntegerField("Order", default=100, help_text="Show Banners in this order")
    visible = models.BooleanField("Visible", default=True, help_text="Show this banner on the site")
    image = models.ImageField(upload_to='bookstore/img/news', width_field="width", height_field="height")
    width = models.IntegerField()
    height = models.IntegerField()
    title = models.CharField(max_length=500, help_text="Hover text for the image")
    text = models.TextField(help_text="Text accompanying the image")
    
    class Meta:
        ordering = ["display_order"]

class SitePage(models.Model):
    link = models.SlugField("Page Link", max_length=200, unique=True, help_text="Page: /[LINK]")
    title = models.CharField(max_length=50, unique=True, help_text="Page title, used for page title (except on front page) and tab")
    metakeywords = models.TextField("Page Keywords", blank=True, help_text="Leave empty to use defaults")
    metadescription = models.TextField("Page Description", blank=True, help_text="Leave empty to use defaults")
    content = models.TextField()
    visible = models.BooleanField(default=True, help_text="Allow page to be loaded")
    showinheader = models.BooleanField("List in Header", default=True, help_text="Show page in tabs at top")
    showinfooter = models.BooleanField("List in Footer", default=True, help_text="Show page in list at bottom")
    frontpage = models.BooleanField(default=False, help_text="Use as front page; select this for only one page")
    display_order = models.IntegerField("Order", default=100, help_text="Show page links in this order")
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.link)

    @models.permalink
    def get_absolute_url(self):
        if self.frontpage:
            return ('bookstore.views.storefront', (), {})
        else:
            return ('bookstore.views.site_page', (), dict(page_link=self.link))

class StorefrontNewsCard(models.Model):
    display_order = models.IntegerField("Order", default=100, help_text="Show news cards in this order")
    visible = models.BooleanField("Visible", default=True, help_text="Show this news card")
    image = models.ImageField(upload_to='bookstore/img/card', width_field="width", height_field="height")
    width = models.IntegerField()
    height = models.IntegerField()
    link = models.URLField(verify_exists=False, blank=True)
    description = models.TextField(help_text="Text for those who don't see the image")
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s (%s)" % (self.description, self.link)

class StorefrontAd(models.Model):
    display_order = models.IntegerField("Order", default=100, help_text="Show ads in this order")
    visible = models.BooleanField("Visible", default=True, help_text="Show this ad")
    image = models.ImageField(upload_to='bookstore/img/card', width_field="width", height_field="height")
    width = models.IntegerField()
    height = models.IntegerField()
    link = models.URLField(verify_exists=False, blank=True)
    column = models.CharField(max_length=5, choices=(
        ('L', 'Left (165 px wide)'),
        ('C', 'Center (600 px wide)'),
        ('R', 'Right (125 or 137 px wide)'),
    ))
    description = models.TextField(help_text="Text for those who don't see the image")
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s [%s] (%s)" % (self.description, self.column, self.link)

class Purchase(models.Model):
    transaction = models.CharField(max_length=10, default='P', choices=(
        ('P', 'Purchase'),
        ('F', 'Free Purchase'),
        ('R', 'Replace'),
        ('V', 'Review'),
    ))
    price = models.DecimalField(max_digits=10, decimal_places=3)
    currency = models.CharField(max_length=5, default='USD', choices=CURRENCY)
    publication = models.ForeignKey(BookPublication)
    status = models.CharField(max_length=10, default='P', choices=(
        ('P', 'Pending'),
        ('S', 'Submitted'),
        ('R', 'Ready'),
        ('C', 'Cancelled'),
        ('X', 'Expired'),
    ))
    admin = models.ForeignKey(User, null=True, related_name="purchase_admin_set")
    customer = models.ForeignKey(User, related_name="purchase_customer_set")
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=256)
    email_name = models.CharField(max_length=200, blank=True)
    email_address = models.EmailField(blank=True)
    email_link = models.CharField(max_length=256, blank=True)
    email_sent = models.BooleanField(default=False)
    email_sent_date = models.DateTimeField(null=True)
    
    @property
    def book(self):
        return self.publication.book
        
    @property
    def format(self):
        return self.publication.format

    class Meta:
        ordering = ["date"]
        
    def __unicode__(self):
        return '%s %s of %s at %s' % (self.get_status_display(), self.get_transaction_display(), self.publication, self.date)

    @models.permalink
    def get_absolute_url(self):
        return ('bookstore.views.purchase_detail', (), dict(purchase_id=self.id))
        
    @models.permalink
    def get_download_url(self):
        if self.transaction == 'V':
            return ('bookstore.views.download_review', (), dict(purchase_id=self.id, key=sha.new(self.email_address + str(self.id)).hexdigest()))
        else:
            return ('bookstore.views.download_book', (), dict(pub_id=self.publication.id))

class PaypalIpn(models.Model):
    purchase = models.ForeignKey(Purchase)
    params = models.TextField("PayPal IPN Parameters", help_text="guru only")
    payment = models.DecimalField(max_digits=10, decimal_places=3)
    currency = models.CharField(max_length=5, default='USD', choices=CURRENCY)
    payment_status = models.CharField(max_length=50)
    entered = models.DateTimeField(auto_now_add=True)
    
    def parse_params(self):
        return cgi.parse_qsl(self.params)

class Download(models.Model):
    purchase = models.ForeignKey(Purchase)
    timestamp = models.DateTimeField(auto_now_add=True)
    ipaddress = models.IPAddressField()

#
# Signal handling
#
from django.db.models.signals import post_save
#from django.dispatch import receiver
def receiver(signal, **kwargs):
    def connector(handler):
        signal.connect(handler, **kwargs)
        return handler
    return connector
        
@receiver(post_save, sender=Purchase, dispatch_uid="send_purchase_email@Purchase")
def send_purchase_email(sender, **kwargs):
    purchase = kwargs.get('instance')
    created = kwargs.get('created')
    if purchase and purchase.status == 'R' and not purchase.email_sent and purchase.email_address:
        message = EmailMessage()
        message.to = purchase.email_address
        if purchase.email_name:
            message.to = ['"%s" <%s>' % (purchase.email_name, purchase.email_address)]
        template = "bookstore/email_purchased.txt"
        message.subject = "Your Lillibridge Press eBook Purchase"
        message.from_email = "Lillibridge Press Sales <sales@lillibridgepress.com>"
        if purchase.transaction == "V":
            template = "bookstore/email_review.txt"
            message.subject = "Your Lillibridge Press eBook Review Copy"
        message.body = render_to_string(template, 
            dict(purchase=purchase, book=purchase.publication.book))
        
        try:
            message.send()
            purchase.email_sent_date = datetime.now()
            purchase.email_sent = True
            purchase.save()
        except Exception as e:
            logging.exception("Purchase Email")

        #subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
        #text_content = 'This is an important message.'
        #html_content = '<p>This is an <strong>important</strong> message.</p>'
        #msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        #msg.attach_alternative(html_content, "text/html")
        #msg.headers["Precendence"] = "bulk"
        #msg.headers["List-Unsubscribe"] = ...

@receiver(post_save, sender=BookPrice, dispatch_uid="update_book_modified@BookPrice")
@receiver(post_save, sender=BookReview, dispatch_uid="update_book_modified@BookReview")
@receiver(post_save, sender=BookWallpaper, dispatch_uid="update_book_modified@BookWallpaper")
@receiver(post_save, sender=BookPublication, dispatch_uid="update_book_modified@BookPublication")
@receiver(post_save, sender=BookListing, dispatch_uid="update_book_modified@BookListing")
@receiver(post_save, sender=BookMedia, dispatch_uid="update_book_modified@BookMedia")
def update_book_modified(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        instance.book.save()

@receiver(post_save, sender=BookWallpaper, dispatch_uid="wallpaper_thumbnail@BookWallpaper")
def wallpaper_thumbnail(sender, **kwargs):
    w = kwargs["instance"]
    from os import path
    try:
        wallpath = w.wallpaper.path
        thumbpath = w.thumbnail.path
    except ValueError:
        thumbpath = path.splitext(wallpath)[0] + ".thumb.jpg"
    try:
        if path.getmtime(wallpath) <= path.getmtime(thumbpath):
            return
    except EnvironmentError:
        pass
    
    from PIL import Image
    image = Image.open(w.wallpaper.path)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    image.thumbnail((220, 220), Image.ANTIALIAS)

    from StringIO import StringIO
    data = StringIO()
    image.save(data, "JPEG")
    data.size = data.tell()
    data.seek(0, 0)
    #data.name = path.basename(thumbpath)
    w.thumbnail.save(path.basename(thumbpath), File(data))
