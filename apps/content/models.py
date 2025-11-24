"""
Content models with best practices implementation.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
from django.db.models import Q, Count, Prefetch

from core.models import TimeStampedModel, SoftDeleteModel, ActiveObjectsManager


class PublishedArticleManager(models.Manager):
    """Manager for published articles."""
    
    def get_queryset(self):
        """Return only published, non-deleted articles."""
        return super().get_queryset().filter(
            is_published=True,
            is_deleted=False
        )
    
    def with_details(self):
        """
        Optimized queryset with related data.
        Use select_related for ForeignKey and prefetch_related for reverse relations.
        """
        return self.get_queryset().select_related(
            'author'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.active_objects.select_related('author')
            )
        ).annotate(
            comments_count=Count('comments', filter=Q(comments__is_deleted=False))
        )
    
    def search(self, query):
        """Search articles by title or content."""
        return self.get_queryset().filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )


class Article(TimeStampedModel, SoftDeleteModel):
    """
    Article model with advanced features.
    
    Represents a blog post/article with author, content, and metadata.
    Includes slug for SEO-friendly URLs and soft delete capability.
    """
    
    title = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(3)],
        help_text='Title of the article (3-255 characters)'
    )
    slug = models.SlugField(
        max_length=280,
        unique=True,
        db_index=True,
        help_text='URL-friendly version of title'
    )
    content = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text='Main content of the article'
    )
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text='Short excerpt/summary of the article'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Prevent deletion of users with articles
        related_name='articles',
        db_index=True
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether the article is published'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of times article has been viewed'
    )
    
    # Tags for categorization (simple implementation)
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comma-separated tags'
    )
    
    # Managers
    objects = models.Manager()  # Default manager
    active_objects = ActiveObjectsManager()  # Non-deleted objects
    published = PublishedArticleManager()  # Published articles
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_published']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['slug']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(views_count__gte=0),
                name='article_views_count_positive'
            )
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug and excerpt."""
        if not self.slug:
            self.slug = self._generate_unique_slug()
        
        if not self.excerpt and self.content:
            # Auto-generate excerpt from content
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        
        super().save(*args, **kwargs)
    
    def _generate_unique_slug(self):
        """Generate a unique slug for the article."""
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        
        while Article.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def increment_views(self):
        """Increment the view count atomically."""
        Article.objects.filter(pk=self.pk).update(views_count=models.F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])
    
    @property
    def reading_time(self):
        """Calculate estimated reading time in minutes."""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))


class CommentManager(models.Manager):
    """Manager for comments with optimized queries."""
    
    def for_article(self, article_id):
        """Get all active comments for an article."""
        return self.filter(
            article_id=article_id,
            is_deleted=False
        ).select_related('author', 'article')


class Comment(TimeStampedModel, SoftDeleteModel):
    """
    Comment model for article discussions.
    
    Allows users to comment on articles with support for
    nested threading (parent-child relationships).
    """
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    content = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(1)],
        help_text='Comment text (1-1000 characters)'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text='Parent comment for threaded discussions'
    )
    
    # Managers
    objects = CommentManager()
    active_objects = ActiveObjectsManager()
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None
