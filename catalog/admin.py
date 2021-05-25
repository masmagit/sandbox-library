from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language

class BooksInline(admin.TabularInline):
    model = Book
    extra = 0
    can_delete = False

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name',  'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back')
    fieldsets = (
        ("None", {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    list_filter = ('title', 'author')
    inlines = [BooksInstanceInline]

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Language)

