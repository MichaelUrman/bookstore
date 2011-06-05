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
        
        
