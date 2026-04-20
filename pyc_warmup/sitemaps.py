from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from songs.models import Song, Composer
from blog.models import BlogPost


class SongSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Song.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return obj.get_absolute_url()


class ComposerSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Composer.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog_detail', args=[obj.slug])


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['song_list', 'blog_list', 'composer_list', 'landing']

    def location(self, item):
        return reverse(item)
