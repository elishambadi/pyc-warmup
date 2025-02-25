from django import forms
from .models import Song, MP3File, Note, Reference
from ckeditor.widgets import CKEditorWidget

class SongForm(forms.ModelForm):
    lyrics = forms.CharField(widget=CKEditorWidget(), required=False)

    slogan = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Song
        fields = ['title', 'lyrics', 'composer', 'youtube_link', 'slogan']

class MP3FileForm(forms.ModelForm):
    class Meta:
        model = MP3File
        fields = ['file', 'voice_part']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['section', 'content']

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['link']
