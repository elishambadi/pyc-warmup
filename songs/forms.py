from django import forms
from django_tiptap.widgets import TipTapWidget
from .models import Song, MP3File, Note, Reference, VoiceNote, VoiceNoteRequest, ScoreSheet, SongRequest

class SongForm(forms.ModelForm):
    lyrics = forms.CharField(widget=forms.Textarea, required=False)
    slogan = forms.CharField(widget=TipTapWidget(), required=False)

    class Meta:
        model = Song
        fields = ['title', 'composer', 'lyrics', 'youtube_link', 'slogan']

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


class ScoreSheetForm(forms.ModelForm):
    class Meta:
        model = ScoreSheet
        fields = ['file']

    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'accept': '.xml,.mxl,.musicxml,.pdf,.png,.jpg,.jpeg,.mid,.midi',
        }),
        required=True
    )


class SongRequestForm(forms.ModelForm):
    # Hidden honeypot: real users never fill this in, bots usually do.
    website = forms.CharField(required=False)

    class Meta:
        model = SongRequest
        fields = [
            'song_title', 'artist', 'request_type', 'voice_part',
            'details', 'requester_name', 'requester_email',
        ]

    def clean_song_title(self):
        title = (self.cleaned_data.get('song_title') or '').strip()
        if len(title) < 2:
            raise forms.ValidationError("Please enter the song title.")
        return title

    def clean_artist(self):
        return (self.cleaned_data.get('artist') or '').strip()

    def clean_details(self):
        details = (self.cleaned_data.get('details') or '').strip()
        if len(details) > 2000:
            raise forms.ValidationError("Please keep the message under 2000 characters.")
        return details

    def clean_requester_name(self):
        return (self.cleaned_data.get('requester_name') or '').strip()
