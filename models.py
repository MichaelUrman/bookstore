from django.db import models
from django.db.models.signals import post_save
from django.core.files import File
from datetime import datetime, date

# TODO:
# consider dijit.Editor instead of minifmt: http://lazutkin.com/blog/2011/mar/13/using-dojo-rich-editor-djangos-admin/

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
    modified = models.DateField(auto_now=True)

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.link)

    @models.permalink
    def get_absolute_url(self):
        return ('bookstore.views.genre_detail', (), dict(genre_link=self.link))

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
    modified = models.DateField(auto_now=True)
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
    isbn = models.SlugField("ISBN", max_length=50, blank=True, help_text="ISBN, if available")
    lbpn = models.SlugField("LBPN", max_length=50, blank=True, help_text="LBPN, if available")
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
    price = models.CharField("price", max_length=20, help_text="Price to display on the book's page")
    upcoming = models.BooleanField(default=True, help_text="Include in upcoming lists if Publish Date is in the future")
    feature = models.BooleanField(default=False, help_text="Include this book as a potential featured item")
    bestseller = models.BooleanField(default=False, help_text="Include this book as a potential bestseller")

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
    def is_free(self):
        return self.price.upper() == "FREE"

    def publications_by_format(self):
        return self.bookpublication_set.filter(format__visible=True).order_by('format__display_order').all()

    def listings_by_reseller(self):
        return self.booklisting_set.filter(reseller__visible=True).order_by('reseller__display_order').all()

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
    youtube = models.SlugField("Youtube Video Key", max_length=50, blank=True)

    def __unicode__(self):
        return "%s %s (%s)" % (self.book.title, self.video_size, self.youtube)

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
    
post_save.connect(wallpaper_thumbnail, sender=BookWallpaper)

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

    class Meta:
        unique_together = ("book", "format")

    def __unicode__(self):
        return "%s in %s" % (self.book.title, self.format.name)

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
    link = models.SlugField("Page Link", max_length=200, blank=True, unique=True, help_text="Page: /[LINK]; a blank one is used for the front page")
    title = models.CharField(max_length=50, blank=True, unique=True, help_text="Page title, used for page title (except on front page) and tab")
    metakeywords = models.TextField("Page Keywords", blank=True, help_text="Leave empty to use defaults")
    metadescription = models.TextField("Page Description", blank=True, help_text="Leave empty to use defaults")
    content = models.TextField()
    visible = models.BooleanField(default=True, help_text="Allow page to be loaded")
    display_order = models.IntegerField("Order", default=100, help_text="Show page links in this order; 0 or negative numbers to hide")

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.link)

    @models.permalink
    def get_absolute_url(self):
        if self.link:
            return ('bookstore.views.site_page', (), dict(page_link=self.link))
        else:
            return ('bookstore.views.storefront', (), {})

class StorefrontNewsCard(models.Model):
    display_order = models.IntegerField("Order", default=100, help_text="Show news cards in this order")
    visible = models.BooleanField("Visible", default=True, help_text="Show this news card")
    image = models.ImageField(upload_to='bookstore/img/card', width_field="width", height_field="height")
    width = models.IntegerField()
    height = models.IntegerField()
    link = models.URLField(verify_exists=False)
    description = models.TextField(help_text="Text for those who don't see the image")

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
    link = models.URLField(verify_exists=False)
    column = models.CharField(max_length=5, choices=(
        ('L', 'Left (165 px wide)'),
        ('C', 'Center (600 px wide)'),
        ('R', 'Right (125 or 137 px wide)'),
    ))
    description = models.TextField(help_text="Text for those who don't see the image")

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):
        return "%s [%s] (%s)" % (self.description, self.column, self.link)