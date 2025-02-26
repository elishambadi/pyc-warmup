from django.contrib import admin
from .models import Song, MP3File, Note, Reference, LyricTimestamp, LyricLine, Section, SongStructure
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

