from django.contrib import admin
from .models import Movie, Category

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):

    list_display = ('title', 'slug', 'year', 'description', 'created_date')
    list_filter = ('created_date', 'title')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_date'

admin.site.register(Category)
