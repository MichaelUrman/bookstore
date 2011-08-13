from django.contrib import admin
from bookstore.models import Genre, Person, MergedUser, \
    Book, BookPrice, BookReview, BookMedia, BookWallpaper, BookFormat, BookPublication, BookReseller, BookListing, \
    SiteNewsBanner, SitePage, StorefrontNewsCard, StorefrontAd, Purchase

class GenreAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "link", "blurb", "description"]}),
        ("Display", {"fields": ["text_color", "page_color", "page_image", "display_order"]}),
        ("SEO", {"fields": ["metakeywords", "metadescription"]}),
    ]
    list_display = ("name", "link", "blurb", "page_image", "visible", "display_order")
    list_editable = ("blurb", "page_image", "visible", "display_order")
    prepopulated_fields = {"link": ("name",)}

class PersonAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["firstname", "lastname", "link", "email", "biography"]}),
        ("Role", {"fields": ["visible", "author", "editor"]}),
        ("SEO", {"fields": ["metakeywords", "metadescription"]}),
    ]
    list_display = ("firstname", "lastname", "author", "editor")
    list_editable = ("author", "editor")
    prepopulated_fields = {"link": ("firstname", "lastname")}

class MergedUserAdmin(admin.ModelAdmin):
    fieldsets = [ (None, {"fields": ["name", "accounts"]}) ]

class BookPriceInline(admin.TabularInline):
    model = BookPrice
    extra = 1

class BookReviewInline(admin.TabularInline):
    model = BookReview
    extra = 1

class BookMediaInline(admin.TabularInline):
    model = BookMedia
    extra = 1

class BookWallpaperInline(admin.TabularInline):
    model = BookWallpaper
    extra = 3
    exclude = ["thumbnail", "wallwidth", "wallheight", "thumbwidth", "thumbheight"]

class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["title", "link", "isbn", "lbpn"]}),
        ("Category", {"fields": ["authors", "genres", "size", "ero_rating"]}),
        ("Display", {"fields": ["blurb", "description", "page_image", "page_image_small", "visible", "upcoming", "feature", "bestseller"]}),
        ("Dates", {"fields": ["added_date", "publish_date"]}),
        ("SEO", {"fields": ["metakeywords", "metadescription"]}),
    ]
    inlines = [BookPriceInline, BookReviewInline, BookMediaInline, BookWallpaperInline]
    list_display = ("title", "link", "visible", "upcoming", "feature", "bestseller", "publish_date")
    list_editable = ("visible", "upcoming", "feature", "bestseller", "publish_date")
    prepopulated_fields = {"link": ("title",)}
    
class BookFormatAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "blurb"]}),
        ("Display", {"fields": ["image", "display_order", "visible"]}),
        ("Technical Details", {"fields": ["extension", "mime"]}),
    ]
    list_display = ("name", "blurb", "extension", "mime", "display_order", "visible")
    list_editable = ("blurb", "extension", "mime", "display_order", "visible")
    
class BookPublicationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["book", "format", "data"]}),
    ]
    list_display = ("book", "format", "data")

class BookResellerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "image", "display_order", "visible"]}),
    ]
    list_display = ("name", "image", "display_order", "visible")
    list_editable = ("image", "display_order", "visible")

class BookListingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["book", "reseller", "url"]}),
    ]
    list_display = ("book", "reseller", "url")
    list_editable = ("url",)

class SiteNewsBannerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["title", "text", "image", "display_order", "visible"]}),
    ]
    list_display = ("title", "text", "image", "display_order", "visible")
    list_editable = ("text", "image", "display_order", "visible")

class SitePageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["title", "link",]}),
        ("Display", {"fields": ["content", "display_order", "showinheader", "showinfooter", "visible"]}),
        ("SEO", {"fields": ["metakeywords", "metadescription"]}),
    ]
    list_display = ("title", "link", "display_order", "showinheader", "showinfooter", "visible", "frontpage")
    list_editable = ("link", "display_order", "showinheader", "showinfooter", "visible", "frontpage")
    prepopulated_fields = {"link": ("title",)}

class StorefrontNewsCardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["link", "description", "image", "display_order", "visible"]}),
    ]
    list_display = ("link", "description", "image", "display_order", "visible")
    list_editable = ("image", "display_order", "visible")

class StorefrontAdAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["link", "column", "description", "image", "display_order", "visible"]}),
    ]
    list_display = ("link", "column", "description", "image", "display_order", "visible")
    list_editable = ("image", "column", "display_order", "visible")
    
admin.site.register(Genre, GenreAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(MergedUser, MergedUserAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookFormat, BookFormatAdmin)
admin.site.register(BookPublication, BookPublicationAdmin)
admin.site.register(BookReseller, BookResellerAdmin)
admin.site.register(BookListing, BookListingAdmin)
admin.site.register(SiteNewsBanner, SiteNewsBannerAdmin)
admin.site.register(SitePage, SitePageAdmin)
admin.site.register(StorefrontNewsCard, StorefrontNewsCardAdmin)
admin.site.register(StorefrontAd, StorefrontAdAdmin)
