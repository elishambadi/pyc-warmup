from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    excerpt = forms.CharField(
        required=False,
        widget=CKEditorWidget(config_name='minimal'),
        help_text='Short summary shown on the listing page (max 300 chars)'
    )
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'excerpt', 'body', 'cover_image', 'published']
