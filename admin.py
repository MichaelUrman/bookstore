from django.contrib import admin
from bookstore.models import Genre, Person, Book, BookReview, BookMedia, BookWallpaper, BookFormat, BookPublication

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
        ("Category", {"fields": ["authors", "genres", "size", "ero_rating", "price"]}),
        ("Display", {"fields": ["blurb", "description", "page_image", "page_image_small", "visible", "upcoming", "feature", "bestseller"]}),
        ("Dates", {"fields": ["added_date", "publish_date"]}),
        ("SEO", {"fields": ["metakeywords", "metadescription"]}),
    ]
    inlines = [BookReviewInline, BookMediaInline, BookWallpaperInline]
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
    
admin.site.register(Genre, GenreAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookFormat, BookFormatAdmin)
admin.site.register(BookPublication, BookPublicationAdmin)