from django.contrib import admin
from trainingApp.models import Author
from trainingApp.models import Category
from trainingApp.models import Post


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'total_posts')

admin.site.register(Author, AuthorAdmin)


class CategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category)


class PostAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post)