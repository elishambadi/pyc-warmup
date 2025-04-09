from django.contrib import admin
from .models import Song, MP3File, Note, Reference, LyricTimestamp, LyricLine, Section, SongStructure, VoiceNote, VoiceNoteRequest
from django.contrib.auth.models import Group, User


class MP3FileInline(admin.TabularInline):
    model = MP3File
    extra = 1

class NoteInline(admin.TabularInline):
    model = Note
    extra = 1

class ReferenceInline(admin.TabularInline):
    model = Reference
    extra = 1

class LyricInline(admin.TabularInline):
    model = LyricLine
    extra = 1

class LyricTimetampInline(admin.TabularInline):
    model = LyricTimestamp
    extra = 1

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    inlines = [MP3FileInline, NoteInline, ReferenceInline, SectionInline, LyricInline]

@admin.register(MP3File)
class MP3Admin(admin.ModelAdmin):
    inlines = [LyricTimetampInline]

@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    list_display = ('song', 'voice_part', 'uploader', 'created_at')

@admin.register(VoiceNoteRequest)
class VoiceNoteRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'created_at', 'song_count')
    search_fields = ('title',)
    list_filter = ('created_at', 'deadline')

    def song_count(self, obj):
        return obj.songs.count()
    song_count.admin_order_field = 'songs'  # Allow ordering by song count

    def save_model(self, request, obj, form, change):
        if not obj.created_at:
            obj.created_at = timezone.now()  # Set created_at only when it's a new entry
        obj.save()