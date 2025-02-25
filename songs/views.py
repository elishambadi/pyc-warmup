from django.shortcuts import render, redirect, get_object_or_404
from .models import Song, MP3File, Note, Reference, LyricLine, LyricTimestamp, Section, Comment
from .forms import SongForm, MP3FileForm, NoteForm, ReferenceForm
from .utils import generate_lyric_lines
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

import json, re

from bs4 import BeautifulSoup

def home(request):
    latest_songs = Song.objects.order_by('-created_at')[:5]  # Get 5 latest songs
    return render(request, "songs/index.html", {"latest_songs": latest_songs})

def song_detail(request, slug):
    song = get_object_or_404(Song, slug=slug)
    mp3s = song.mp3_files.all()  # Get all MP3s related to this song
    notes = song.notes.all()  # Get all notes related to this song
    lyric_lines = list(song.lyric_lines.all())  # Get all lyric lines related to this song
    references = song.references.all()  # Get all references related to this song

    annotated_lines = []
    current_section = None

    for line in lyric_lines:
        # Determine if this line starts a new section.
        is_new_section = line.section != current_section
        if is_new_section:
            current_section = line.section
        annotated_lines.append({
            'line': line,
            'is_new_section': is_new_section,
        })

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
        'annotated_lines': annotated_lines,
    })

def add_song(request):
    if request.method == "POST":
        song_form = SongForm(request.POST)
        if song_form.is_valid():
            # Create the Song instance without committing to the database yet.
            song = song_form.save(commit=False)
            # Temporarily assign an empty string to lyrics; we will update after processing lyric lines.
            song.lyrics = ""
            song.save()  # Now song has a primary key so it can be referenced.

            all_lyric_lines = []  # Will collect all lyric texts in order.
            order = 1             # Order counter for lyric lines.
            index = 1             # Index for sections: expecting keys like lyrics_title_0, lyrics_0, etc.

            # Loop as long as the POST data contains a key for the section title.
            while f"lyrics_title_{index}" in request.POST:
                # Grab the section title and lyrics text.
                print(f"Line {index}")
                section_title = request.POST.get(f"lyrics_title_{index}", "").strip()
                lyrics_text = request.POST.get(f"lyrics_{index}", "").strip()
                
                matches = re.findall(r"\((.*?)\)", section_title)
                instruction = " ".join(matches) if matches else None
                clean_section_title = re.sub(r"\s*\(.*?\)", "", section_title).strip()

                section = Section.objects.create(
                    song=song, 
                    name=clean_section_title,  # Save the cleaned section title
                    instruction=instruction,   # Save extracted instruction
                    position=index
                )


                # Split the submitted lyrics text into individual lines.
                lines = lyrics_text.splitlines()
                for line in lines:
                    matches = re.findall(r"\((.*?)\)", line)
                    instruction = " ".join(matches) if matches else None
                    line = re.sub(r"\s*\(.*?\)", "", line).strip()

                    if line:  # Only create a LyricLine for nonempty lines.
                        LyricLine.objects.create(
                            song=song,
                            section=section,
                            text=line,
                            instruction=instruction,
                            order=order
                        )
                        all_lyric_lines.append(line)
                        order += 1

                index += 1

            # After processing all sections, join all lyric lines with newline characters.
            song.lyrics = "\n".join(all_lyric_lines)
            song.save()  # Save the final lyrics string to the Song instance.
            
            return redirect("song_list")
        else:
            song_form = SongForm(request.POST)
    else:
        song_form = SongForm()

    return render(request, "songs/add_song.html", {"song_form": song_form})

# 🎵 Delete a Song
@require_http_methods(["DELETE"])
def delete_song(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
        # Delete all LyricTimestamps related to the song
        LyricTimestamp.objects.filter(lyric_line__song=song).delete()
        # Delete all MP3 files related to the song
        song.mp3_files.all().delete()
        song.delete()
        return JsonResponse({'status': 'success', 'success': True})
    except Song.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Song not found', 'success': False}, status=404)

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

@require_http_methods(["DELETE"])
def delete_mp3(request, mp3_id):
    try:
        mp3_file = MP3File.objects.get(id=mp3_id)
        LyricTimestamp.objects.filter(mp3_file=mp3_file).delete()
        mp3_file.delete()
        return JsonResponse({'status': 'success',  'success': True})
    except MP3File.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'MP3 file not found', 'success': False}, status=404)

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

@require_http_methods(["DELETE"])
def delete_lyric(request, lyric_id):
    try:
        lyric = LyricLine.objects.get(id=lyric_id)
        lyric.delete()
        return JsonResponse({'status': 'success'})
    except LyricLine.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Lyric line not found'}, status=404)
    
def add_song_comment(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    
    if request.method == 'POST':
        text = request.POST.get('comment_text')
        
        if not text:
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        
        # Create the new comment for the song
        comment = Comment.objects.create(
            song=song,
            text=text
        )
        
        return JsonResponse({
            'id': comment.id,
            'text': comment.text,
            'likes': comment.likes,
            'dislikes': comment.dislikes
        })
    
    # Return a page with the comment form (or a simple JSON response if needed)
    return render(request, 'add_comment.html', {'song': song})


# Like a comment
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.likes += 1
    comment.save()
    
    # You can return a JSON response or redirect as necessary
    return JsonResponse({'likes': comment.likes})

# Dislike a comment
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.dislikes += 1
    comment.save()
    
    return JsonResponse({'dislikes': comment.dislikes})

# Reply to a comment
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            reply = Comment.objects.create(
                text=text,
                parent=parent_comment,
                song=parent_comment.song,
                user=request.user  # Assuming you have a user model
            )
            return redirect('song_detail', song_id=parent_comment.song.id)
    
    return render(request, 'comments/reply_comment.html', {'parent_comment': parent_comment})