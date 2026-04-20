from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('technique', 'Vocal Technique'),
        ('warmup', 'Warm-Up Tips'),
        ('theory', 'Music Theory'),
        ('health', 'Voice Health'),
        ('performance', 'Performance'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='technique')
    excerpt = models.TextField(blank=True, help_text='Short summary shown on the listing page')
    body = models.TextField()
    cover_image = models.ImageField(upload_to='blog/covers/', null=True, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)
