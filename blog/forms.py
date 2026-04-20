from django import forms
from django_tiptap.widgets import TipTapWidget
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    excerpt = forms.CharField(required=False, widget=TipTapWidget())
    body = forms.CharField(widget=TipTapWidget())

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'excerpt', 'body', 'cover_image', 'published']
