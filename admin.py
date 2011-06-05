from django.contrib import admin
from bookstore.models import Genre, Person

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

admin.site.register(Genre, GenreAdmin)
admin.site.register(Person, PersonAdmin)