"""
Advanced serializers for content app with best practices.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Article, Comment


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for User as Article/Comment author."""
    
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'articles_count']
        read_only_fields = ['id', 'username']
    
    def get_articles_count(self, obj):
        """Get cached count of author's articles."""
        cache_key = f'author:{obj.id}:articles_count'
        count = cache.get(cache_key)
        
        if count is None:
            count = obj.articles.filter(is_deleted=False, is_published=True).count()
            cache.set(cache_key, count, 300)  # Cache for 5 minutes
        
        return count


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model with nested author info.
    """
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    is_reply = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'content', 'author', 'parent',
            'is_reply', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
        extra_kwargs = {
            'article': {'write_only': True}
        }
    
    def get_replies(self, obj):
        """Get nested replies (one level deep to avoid deep recursion)."""
        if obj.is_reply:
            return []  # Don't nest replies of replies
        
        replies = obj.replies.filter(is_deleted=False).select_related('author')[:5]
        return CommentListSerializer(replies, many=True).data
    
    def validate_parent(self, value):
        """Validate parent comment belongs to the same article."""
        article = self.initial_data.get('article')
        if value and str(value.article.id) != str(article):
            raise serializers.ValidationError(
                "Parent comment must belong to the same article."
            )
        return value


class CommentListSerializer(serializers.ModelSerializer):
    """Lightweight comment serializer for lists."""
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at']


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for article lists.
    """
    author = serializers.StringRelatedField()
    comments_count = serializers.IntegerField(read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author',
            'is_published', 'views_count', 'comments_count',
            'reading_time', 'tags', 'created_at'
        ]
        read_only_fields = ['slug', 'views_count', 'created_at']


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single article with all relations.
    """
    author = AuthorSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    reading_time = serializers.IntegerField(read_only=True)
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'author', 'is_published', 'views_count',
            'tags', 'tags_list', 'comments', 'comments_count',
            'reading_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'views_count', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        """Get count of active comments."""
        return obj.comments.filter(is_deleted=False).count()
    
    def get_tags_list(self, obj):
        """Parse comma-separated tags into a list."""
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating articles.
    """
    tags_list = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True,
        help_text="List of tags"
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'is_published', 'tags', 'tags_list'
        ]
        extra_kwargs = {
            'excerpt': {'required': False},
            'tags': {'required': False, 'write_only': True}
        }
    
    def validate_title(self, value):
        """Validate title uniqueness and length."""
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        
        # Check for duplicate title (case-insensitive)
        instance = self.instance
        qs = Article.objects.filter(title__iexact=value, is_deleted=False)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("An article with this title already exists.")
        
        return value
    
    def validate_content(self, value):
        """Validate content length."""
        if len(value) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value
    
    def validate_tags_list(self, value):
        """Validate tags list."""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 tags allowed.")
        return value
    
    def create(self, validated_data):
        """Create article with tags."""
        tags_list = validated_data.pop('tags_list', [])
        if tags_list:
            validated_data['tags'] = ', '.join(tags_list)
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update article with tags."""
        tags_list = validated_data.pop('tags_list', None)
        if tags_list is not None:
            validated_data['tags'] = ', '.join(tags_list)
        
        return super().update(instance, validated_data)


class ArticleStatsSerializer(serializers.Serializer):
    """Serializer for article statistics."""
    total_articles = serializers.IntegerField()
    published_articles = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    top_authors = serializers.ListField()
