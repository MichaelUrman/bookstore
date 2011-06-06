from django.db import models

# Storage models
class ImageBlob(models.Model):
    modified = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='bookstore/img')

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
    #page_image = models.ForeignKey(ImageBlob, related_name='+')
    page_image = models.ImageField(upload_to='bookstore/img')
    metakeywords = models.TextField("Page Keywords", blank=True)
    metadescription = models.TextField("Page Description", blank=True)
    modified = models.DateField(auto_now=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.link)
        
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
    
    # sales = db.IntegerProperty()
    
    def __unicode__(self):
        return "%s, %s <%s>" % (self.lastname, self.firstname, self.email)
        
        
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
    page_image = models.ImageField(upload_to='bookstore/img', help_text="Generally a 400x600 image of the book's cover")
    page_image_small = models.ImageField(upload_to='bookstore/img', help_text="Generally a 150x225 version of the book's cover")
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

    def __unicode__(self):
        return "%s, a %s (%s)" % (self.title, self.size, self.link)
