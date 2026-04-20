from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def blog_list(request):
    category = request.GET.get('category', '')
    posts = BlogPost.objects.filter(published=True)
    if category:
        posts = posts.filter(category=category)
    categories = BlogPost.CATEGORY_CHOICES
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'categories': categories,
        'active_category': category,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    related = BlogPost.objects.filter(published=True, category=post.category).exclude(pk=post.pk)[:3]
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'related': related,
    })
