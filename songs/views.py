from django.shortcuts import render, redirect, get_object_or_404
from .models import Song, MP3File, Note, Reference
from .forms import SongForm, MP3FileForm, NoteForm, ReferenceForm
from django.http import JsonResponse
import json

def song_list(request):
    songs = Song.objects.all()
    return render(request, "songs/song_list.html", {"songs": songs})

def song_detail(request, pk):
    song = Song.objects.get(pk=pk)
    mp3s = song.mp3_files.all()  # Get all MP3s related to this song
    notes = song.notes.all()  # Get all notes related to this song
    references = song.references.all()  # Get all references related to this song
    
    return render(request, 'songs/song_detail.html', {
        'song': song,
        'mp3s': mp3s,
        'notes': notes,
        'references': references,
    })

def add_song(request):
    if request.method == "POST":
        song_form = SongForm(request.POST)
        if song_form.is_valid():
            song = song_form.save()
            return redirect("song_list")
    else:
        song_form = SongForm()

    return render(request, "songs/add_song.html", {"song_form": song_form})

# Edit functions via JS

def save_lyrics(request, song_id):
    data = json.loads(request.body)
    song = get_object_or_404(Song, id=song_id)
    song.lyrics = data['lyrics']
    song.save()
    return JsonResponse({'success': True})

# 🎵 Edit MP3 File (Update Voice Part)
def save_mp3(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mp3 = get_object_or_404(MP3File, id=data['mp3_id'])
        mp3.voice_part = data['voice_part']
        mp3.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

# 🎵 Add New MP3 File (🔗 Requires song_id)
def add_mp3(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    file = request.FILES.get('file')
    voice_part = request.POST.get('voice_part')
    
    if file and voice_part:
        mp3 = MP3File.objects.create(song=song, file=file, voice_part=voice_part)
        return JsonResponse({'success': True, 'mp3_id': mp3.id})
    
    return JsonResponse({'success': False}, status=400)

# 📝 Add a Note (🔗 Requires song_id)
def add_note(request, song_id):
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        data = json.loads(request.body)
        Note.objects.create(song=song, section=data['section'], content=data['content'])
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)

# 🔗 Add a Reference (🔗 Requires song_id)
def add_reference(request, song_id):
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        data = json.loads(request.body)
        Reference.objects.create(song=song, link=data['link'])
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)