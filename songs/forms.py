from django import forms
from .models import Song, MP3File, Note, Reference, VoiceNote, VoiceNoteRequest
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

class VoiceNoteForm(forms.ModelForm):
    class Meta:
        model = VoiceNote
        fields = ['voice_part', 'file']

    # Override the file field widget to restrict file types to audio
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'accept': 'audio/*'}),  # Restrict file input to audio files
        required=True  # Make the field required
    )


class VoiceNoteRequestForm(forms.ModelForm):
    class Meta:
        model = VoiceNoteRequest
        fields = ['title', 'songs', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(VoiceNoteRequestForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 5 classes to form fields
        self.fields['title'].widget.attrs.update({'class': 'form-control mb-3', 'placeholder': 'Name of the ministry'})
        self.fields['songs'].widget.attrs.update({'class': 'form-select mb-3'})
        self.fields['deadline'].widget.attrs.update({'class': 'form-control mb-3'})
