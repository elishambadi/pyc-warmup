from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from .models import Song, MP3File, Note, Reference, LyricLine, LyricTimestamp, Section, Comment, VoiceNote, VoiceNoteRequest
from .forms import SongForm, MP3FileForm, NoteForm, ReferenceForm, VoiceNoteForm, VoiceNoteRequestForm
from .utils import generate_lyric_lines
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test

from django.utils import timezone
from django.urls import reverse

import json, re

from bs4 import BeautifulSoup

def home(request):
    latest_songs = Song.objects.order_by('-created_at')  # Get 5 latest songs
    latest_voicenote_request = VoiceNoteRequest.objects.filter(deadline__gt=timezone.now()).order_by('-deadline').first()

    is_trainer = request.user.groups.filter(name="Trainers").exists() if request.user.is_authenticated else False

    print(f"Latest request {latest_voicenote_request}")
    
    return render(request, "songs/index.html", {
        'latest_songs': latest_songs,
        'latest_voicenote_request': latest_voicenote_request,
        'is_trainer': is_trainer
    })

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
                print(f"Line {index}")
                section_title = request.POST.get(f"lyrics_title_{index}", "").strip()
                lyrics_text = request.POST.get(f"lyrics_{index}", "").strip()
                
                matches = re.findall(r"\((.*?)\)", section_title)
                instruction = " ".join(matches) if matches else None
                clean_section_title = re.sub(r"\s*\(.*?\)", "", section_title).strip()

                section = Section.objects.create(
                    song=song, 
                    name=clean_section_title,
                    instruction=instruction,
                    position=index
                )

                lines = lyrics_text.splitlines()
                for line in lines:
                    matches = re.findall(r"\((.*?)\)", line)
                    instruction = " ".join(matches) if matches else None
                    line = re.sub(r"\s*\(.*?\)", "", line).strip()

                    if line:
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

            song.lyrics = "\n".join(all_lyric_lines)
            song.save()
            
            return redirect("song_list")
        else:
            song_form = SongForm(request.POST)
    else:
        song_form = SongForm()

    return render(request, "songs/add_song.html", {"song_form": song_form})

# 🎵 Delete a Song
@login_required
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
    

@require_http_methods(["DELETE"])
def delete_timestamp(request):
    data = json.loads(request.body)
    lyric_id = data.get('lyric_id')
    mp3_id = data.get('mp3_id')
    try:
        lyric_line = LyricLine.objects.get(id=lyric_id)
        mp3_file = MP3File.objects.get(id=mp3_id)
        
        timestamp_obj = LyricTimestamp.objects.filter(
            lyric_line=lyric_line,
            mp3_file=mp3_file
        ).first()
        
        if timestamp_obj:
            timestamp_obj.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Timestamp not found'}, status=404)
    except (LyricLine.DoesNotExist, MP3File.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Lyric or MP3 not found'}, status=404)

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

@login_required
def upload_voicenote(request, song_slug):

    song = Song.objects.get(slug=song_slug)

    latest_request = VoiceNoteRequest.objects.order_by('-created_at').first()

    # Check if there's no active request
    if not latest_request:
        messages.warning(request, "No upcoming ministries found.")
        return redirect('home')

    # Retrieve voice notes uploaded by the current user for the latest request
    user_voice_notes = VoiceNote.objects.filter(
        voicenote_request=latest_request
    )

    voicenotes_present = len(user_voice_notes) > 1

    # Filter the voice notes by voice part
    voice_notes_by_part = {
        'Soprano': user_voice_notes.filter(voice_part='Soprano'),
        'Alto': user_voice_notes.filter(voice_part='Alto'),
        'Tenor': user_voice_notes.filter(voice_part='Tenor'),
        'Bass': user_voice_notes.filter(voice_part='Bass'),
        'Other': user_voice_notes.filter(voice_part='Other'),
    }

    is_trainer = request.user.groups.filter(name="Trainers").exists() if request.user.is_authenticated else False

    if request.method == 'POST':
        form = VoiceNoteForm(request.POST, request.FILES)
        if form.is_valid():
            # Ensure that only one voice note per voice part can be uploaded
            existing_voicenote = song.voice_notes.filter(uploader=request.user).first()
            
            if existing_voicenote:
                messages.info(request, "You've already uploaded a voicenote for this song.")
                # If there's already a voice note for that voice part, redirect with an error
                return render(request, "songs/upload_voicenote.html", {'form': form, 'song': song, 'is_trainer': is_trainer, 'voice_notes_by_part': voice_notes_by_part})

            voice_note = form.save(commit=False)
            voice_note.song = song
            voice_note.uploader = request.user
            voice_note.save()
            return render(request, "songs/upload_voicenote.html", {'form': form, 'song': song, 'is_trainer': is_trainer, 'voice_notes_by_part': voice_notes_by_part})
    else:
        form = VoiceNoteForm()

    shareable_url = request.build_absolute_uri(reverse('upload_voicenotes_for_request'))  # Generate the absolute URL

    return render(request, "songs/upload_voicenote.html", {'form': form, 'song': song, 'is_trainer': is_trainer, 'voice_notes_by_part': voice_notes_by_part, 'latest_request': latest_request, 'voicenotes_present': voicenotes_present, 'shareable_url': shareable_url})


@login_required
def delete_voicenote(request, song_slug, voicenote_id):
    song = Song.objects.get(slug=song_slug)
    voice_note = get_object_or_404(VoiceNote, id=voicenote_id)
    
    if voice_note.uploader == request.user or request.user.groups.filter(name="Trainers").exists():
        voice_note.delete()
        messages.success(request, "Deleted voicenote.")
        return redirect(upload_voicenotes_for_request)
    else:
        # Show an error or permission denied
        return redirect(upload_voicenotes_for_request)


# Ensure only Trainers can access
@user_passes_test(lambda u: u.groups.filter(name='Trainers').exists())
def approve_voicenote(request, song_slug, voicenote_id):
    print(f"Voice note ID: {voicenote_id}")
    song = get_object_or_404(Song, slug=song_slug)  # Get the Song based on slug
    voice_note = get_object_or_404(VoiceNote, id=voicenote_id)

    if not voice_note:
        messages.warning(request, "Voicenote not found")
        return redirect('upload_voicenote', song_slug=song_slug)
    
    # If you found the voice note, approve it
    voice_note.approved = True
    voice_note.save()

    messages.success(request, f"{voice_note.uploader.username}'s Voice note for '{song.title}' approved successfully!")

    # Redirect back to the song detail page
    return redirect('upload_voicenote', song_slug=song_slug)

@login_required
def add_voicenote_request(request):
    if request.method == 'POST':
        form = VoiceNoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # create this later
    else:
        form = VoiceNoteRequestForm()
    return render(request, 'voicenotes/add_voicenote_request.html', {'form': form})

@login_required
def upload_voicenotes_for_request(request):
    latest_request = VoiceNoteRequest.objects.order_by('-created_at').first()

    if not latest_request:
        messages.warning(request, "No upcoming ministries found.")
        return redirect('home')

    if request.method == 'POST':
        form = VoiceNoteForm(request.POST, request.FILES)
        song_id = request.POST.get('song_id')
        song = Song.objects.get(id=song_id)

        if form.is_valid():
            voicenote = form.save(commit=False)
            voicenote.song = song
            voicenote.uploader = request.user
            voicenote.voicenote_request = latest_request
            voicenote.save()
            messages.success(request, f"Voice Note for '{song.title}' uploaded.")
            return redirect('upload_voicenotes_for_request')

    else:
        form = VoiceNoteForm()

    # Get the user's voicenotes for the latest request
    user_voicenotes = VoiceNote.objects.filter(
        voicenote_request=latest_request,
        uploader=request.user
    )

    songs = latest_request.songs.all()
    return render(request, 'voicenotes/upload_vn_for_request.html', {
        'form': form,
        'songs': songs,
        'latest_request': latest_request,
        'user_voicenotes': user_voicenotes
    })