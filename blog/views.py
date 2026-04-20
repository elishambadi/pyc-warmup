from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BlogPost
from .forms import BlogPostForm
from songs.models import Song


def blog_list(request):
    category = request.GET.get('category', '')
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        posts = BlogPost.objects.all()  # staff see drafts too
    else:
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
    # Surface up to 4 songs as contextual CTAs — most viewed first
    related_songs = Song.objects.order_by('-views')[:4]
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'related': related,
        'related_songs': related_songs,
    })


@login_required
def add_blog_post(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to write blog posts.')
        return redirect('blog_list')
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, f'Post "{post.title}" saved.')
            return redirect('blog_detail', slug=post.slug)
    else:
        form = BlogPostForm()
    return render(request, 'blog/blog_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('blog_detail', slug=slug)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, f'Post "{post.title}" updated.')
            return redirect('blog_detail', slug=post.slug)
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog/blog_form.html', {'form': form, 'action': 'Edit', 'post': post})
