from django.contrib import admin
from .models import Category, Idea, Vote, Comment

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'idea', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'idea__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'idea', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'idea__title')
