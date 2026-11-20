# forum/admin.py
from django.contrib import admin
from .models import ForumPost, ForumComment


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('author', 'short_content', 'is_approved', 'total_likes', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__phone_number', 'author__first_name', 'title')
    list_editable = ('is_approved',)
    readonly_fields = ('likes', 'created_at')
    
    def short_content(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    short_content.short_description = "متن"


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'short_content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__phone_number')
    readonly_fields = ('likes', 'created_at')
    
    def short_content(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    short_content.short_description = "متن"
