"""
ViewSets for content app with advanced features.
"""
from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response

from .models import Article, Comment
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
    ArticleStatsSerializer,
    CommentSerializer,
    CommentListSerializer,
)
from .permissions import IsAuthorOrReadOnly
from .filters import ArticleFilter, CommentFilter


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Article model with full CRUD operations.
    
    list: Get all articles with filtering, search, and pagination
    retrieve: Get single article by ID or slug
    create: Create new article (authenticated users only)
    update: Update article (author only)
    partial_update: Partially update article (author only)
    destroy: Delete article (author only - soft delete)
    """
    
    queryset = Article.published.with_details()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        return ArticleDetailSerializer
    
    def get_queryset(self):
        """
        Customize queryset based on action and user.
        """
        queryset = super().get_queryset()
        
        # If user is authenticated, show their unpublished articles too
        if self.request.user.is_authenticated:
            user_articles = Article.active_objects.filter(author=self.request.user)
            queryset = queryset | user_articles
        
        # Optimize queries
        if self.action == 'list':
            queryset = queryset.select_related('author').annotate(
                comments_count=Count('comments', filter=Q(comments__is_deleted=False))
            )
        elif self.action == 'retrieve':
            queryset = queryset.prefetch_related('comments__author')
        
        return queryset.distinct()
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve single article with caching and view count increment.
        """
        slug = kwargs.get('slug')
        cache_key = f'article:slug:{slug}'
        
        # Try to get from cache
        instance = cache.get(cache_key)
        
        if instance is None:
            instance = self.get_object()
            # Cache for 5 minutes
            cache.set(cache_key, instance, 300)
        
        # Increment view count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Set author to current user when creating."""
        serializer.save(author=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def statistics(self, request):
        """
        Get article statistics.
        
        Returns aggregated statistics about articles.
        """
        stats = {
            'total_articles': Article.active_objects.count(),
            'published_articles': Article.published.count(),
            'total_views': Article.published.aggregate(Sum('views_count'))['views_count__sum'] or 0,
            'total_comments': Comment.active_objects.count(),
            'top_authors': list(
                Article.published.values('author__username')
                .annotate(article_count=Count('id'))
                .order_by('-article_count')[:5]
            )
        }
        
        serializer = ArticleStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, slug=None):
        """
        Get all comments for an article.
        """
        article = self.get_object()
        comments = article.comments.filter(
            is_deleted=False,
            parent__isnull=True  # Only top-level comments
        ).select_related('author').prefetch_related('replies')
        
        # Apply pagination
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def my_articles(self, request):
        """
        Get articles created by the current user.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        articles = Article.active_objects.filter(
            author=request.user
        ).select_related('author').annotate(
            comments_count=Count('comments', filter=Q(comments__is_deleted=False))
        )
        
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model.
    
    list: Get all comments with filtering
    retrieve: Get single comment
    create: Create new comment (authenticated users only)
    update: Update comment (author only)
    destroy: Delete comment (author only - soft delete)
    """
    
    queryset = Comment.active_objects.select_related('author', 'article')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CommentFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return CommentListSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """Set author to current user when creating."""
        serializer.save(author=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()
    
    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        """
        Get comments created by the current user.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comments = Comment.active_objects.filter(
            author=request.user
        ).select_related('article', 'author')
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentListSerializer(comments, many=True)
        return Response(serializer.data)
