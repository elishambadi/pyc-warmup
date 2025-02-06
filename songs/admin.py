from django.contrib import admin
from .models import Song, MP3File, Note, Reference

class MP3FileInline(admin.TabularInline):
    model = MP3File
    extra = 1

class NoteInline(admin.TabularInline):
    model = Note
    extra = 1

class ReferenceInline(admin.TabularInline):
    model = Reference
    extra = 1

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    inlines = [MP3FileInline, NoteInline, ReferenceInline]
