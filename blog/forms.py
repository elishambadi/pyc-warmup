from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    excerpt = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}))
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 12}))

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'excerpt', 'body', 'cover_image', 'published']
