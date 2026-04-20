from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'excerpt', 'body', 'cover_image', 'published']
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }
