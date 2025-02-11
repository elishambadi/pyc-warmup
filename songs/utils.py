from django.shortcuts import render, redirect, get_object_or_404
from .models import Song, MP3File, Note, Reference, LyricLine
from .forms import SongForm, MP3FileForm, NoteForm, ReferenceForm
from django.http import JsonResponse, HttpResponse
import json

from bs4 import BeautifulSoup

def generate_lyric_lines(song_id):
    try:
        song = Song.objects.get(id=song_id)
        soup = BeautifulSoup(song.lyrics, "html.parser")

        # Extract and split lyrics
        lines = []
        for paragraph in soup.find_all("p"):
            lines.extend(paragraph.decode_contents().split("<br/>"))

        # Trim spaces and remove empty lines
        lines = [line.strip() for line in lines if line.strip()]

        # Create LyricLine objects with explicit order
        lyric_lines = [
            LyricLine(
                song=song,
                text=line,
                order=index
            ) for index, line in enumerate(lines)
        ]

        # Bulk create the lyric lines
        LyricLine.objects.bulk_create(lyric_lines)

        print(f"✅ Generated {len(lyric_lines)} lyric lines for song ID {song_id}")
        return len(lyric_lines)

    except Song.DoesNotExist:
        print(f"❌ Song with ID {song_id} not found.")
        return 0
