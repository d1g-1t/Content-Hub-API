"""
Filters for content app.
"""
from django_filters import rest_framework as filters
from .models import Article, Comment


class ArticleFilter(filters.FilterSet):
    """
    Filter class for Article model.
    """
    title = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    tags = filters.CharFilter(lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_published = filters.BooleanFilter()
    min_views = filters.NumberFilter(field_name='views_count', lookup_expr='gte')
    
    class Meta:
        model = Article
        fields = ['title', 'author', 'tags', 'is_published', 'created_after', 'created_before', 'min_views']


class CommentFilter(filters.FilterSet):
    """
    Filter class for Comment model.
    """
    article = filters.NumberFilter(field_name='article__id')
    article_slug = filters.CharFilter(field_name='article__slug')
    author = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_reply = filters.BooleanFilter(field_name='parent', lookup_expr='isnull', exclude=True)
    
    class Meta:
        model = Comment
        fields = ['article', 'article_slug', 'author', 'created_after', 'created_before']
