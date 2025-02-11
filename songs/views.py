from django.shortcuts import render, redirect, get_object_or_404
from .models import Song, MP3File, Note, Reference, LyricLine, LyricTimestamp
from .forms import SongForm, MP3FileForm, NoteForm, ReferenceForm
from .utils import generate_lyric_lines
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

import json

from bs4 import BeautifulSoup

def song_list(request):
    songs = Song.objects.all()
    return render(request, "songs/song_list.html", {"songs": songs})

def song_detail(request, pk):
    song = Song.objects.get(pk=pk)
    mp3s = song.mp3_files.all()  # Get all MP3s related to this song
    notes = song.notes.all()  # Get all notes related to this song
    references = song.references.all()  # Get all references related to this song

    mp3_timestamps = {}
    for line in song.lyric_lines.all():
        timestamps = {
            ts.mp3_file_id: ts.timestamp 
            for ts in line.timestamps.all()
        }
        mp3_timestamps[line.id] = json.dumps(timestamps)
    
    return render(request, 'songs/song_detail.html', {
        'song': song,
        'mp3s': mp3s,
        'notes': notes,
        'references': references,
        'mp3_timestamps': mp3_timestamps,
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

# ---------------- Lyric Syncing Code --------------------

def sync_lyrics(request, mp3_id):
    """Render the lyric syncing page for a specific MP3 file"""
    mp3_file = get_object_or_404(MP3File, id=mp3_id)
    lyrics = mp3_file.song.lyric_lines.all()
    
    # Get existing timestamps for this MP3
    timestamps = {
        ts.lyric_line_id: ts.timestamp 
        for ts in mp3_file.lyric_timestamps.all()
    }
    
    return render(request, "songs/sync_lyrics.html", {
        "mp3_file": mp3_file,
        "song": mp3_file.song,
        "lyrics": lyrics,
        "timestamps": timestamps,
    })

@require_http_methods(["POST"])
def save_timestamp(request):
    data = json.loads(request.body)
    lyric_id = data.get('lyric_id')
    mp3_id = data.get('mp3_id')
    timestamp = data.get('timestamp')

    try:
        lyric_line = LyricLine.objects.get(id=lyric_id)
        mp3_file = MP3File.objects.get(id=mp3_id)
        
        timestamp_obj, created = LyricTimestamp.objects.update_or_create(
            lyric_line=lyric_line,
            mp3_file=mp3_file,
            defaults={'timestamp': timestamp}
        )
        
        return JsonResponse({'success': True})
    except (LyricLine.DoesNotExist, MP3File.DoesNotExist):
        return JsonResponse({'success': False}, status=404)

def generate_lrc(request, song_id):
    """Generate and download an LRC file"""
    song = get_object_or_404(MP3File, id=song_id)
    lyrics = LyricLine.objects.filter(mp3=song).order_by("timestamp")

    lrc_content = ""
    for lyric in lyrics:
        if lyric.timestamp is not None:
            minutes = int(lyric.timestamp // 60)
            seconds = lyric.timestamp % 60
            lrc_content += f"[{minutes:02}:{seconds:05.2f}] {lyric.text}\n"

    response = HttpResponse(lrc_content, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="{song.voice_part}.lrc"'
    return response

# Generate lyrics view

def generate_lyrics_view(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    count = generate_lyric_lines(song_id)

    if count:
        messages.success(request, f"Successfully generated {count} lyric lines.")
    else:
        messages.error(request, "Failed to generate lyric lines.")

    return redirect('sync-lyrics', song_id=song.id)  # Redirect to sync page

@require_http_methods(["DELETE"])
def delete_lyric(request, lyric_id):
    try:
        lyric = LyricLine.objects.get(id=lyric_id)
        lyric.delete()
        return JsonResponse({'status': 'success'})
    except LyricLine.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Lyric line not found'}, status=404)