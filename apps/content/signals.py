"""Signals for content app."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Article, Comment


@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
def invalidate_article_cache(sender, instance, **kwargs):
    """Invalidate cache when article is saved or deleted."""
    cache_keys = [
        f'article:{instance.id}',
        f'article:slug:{instance.slug}',
        'articles:list:*',
    ]
    for key in cache_keys:
        cache.delete(key)


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def invalidate_comment_cache(sender, instance, **kwargs):
    """Invalidate cache when comment is saved or deleted."""
    cache_keys = [
        f'comment:{instance.id}',
        f'article:{instance.article.id}:comments',
    ]
    for key in cache_keys:
        cache.delete(key)
