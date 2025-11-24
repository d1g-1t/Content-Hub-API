"""Admin configuration for content app."""
from django.contrib import admin
from django.db.models import Count
from .models import Article, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for Article model."""
    
    list_display = ['title', 'author', 'is_published', 'views_count', 'created_at', 'comment_count']
    list_filter = ['is_published', 'created_at', 'is_deleted']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'tags')
        }),
        ('Metadata', {
            'fields': ('author', 'is_published', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with comment count."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('author').annotate(
            _comment_count=Count('comments')
        )
        return queryset
    
    def comment_count(self, obj):
        """Display comment count."""
        return obj._comment_count
    comment_count.admin_order_field = '_comment_count'
    comment_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""
    
    list_display = ['id', 'article', 'author', 'content_preview', 'created_at', 'is_reply']
    list_filter = ['created_at', 'is_deleted']
    search_fields = ['content', 'author__username', 'article__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment', {
            'fields': ('article', 'content', 'author', 'parent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('author', 'article', 'parent')
        return queryset
    
    def content_preview(self, obj):
        """Display truncated content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def is_reply(self, obj):
        """Display if comment is a reply."""
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'
