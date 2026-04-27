# core/admin.py
from django.contrib import admin
from .models import Post, Comment, Profile # Add Profile
from django.utils.html import format_html

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'audio_file', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'caption')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post_id', 'text_preview', 'created_at')
    list_filter = ('user', 'created_at', 'post')
    search_fields = ('user__username', 'text')

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment Text'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 50px;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image Preview'