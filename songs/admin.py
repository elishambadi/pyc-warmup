from django.contrib import admin
from .models import Song, MP3File, Note, Reference, LyricTimestamp, LyricLine, Section, SongStructure, VoiceNote, VoiceNoteRequest, Composer, SongComposerContribution
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


class SongComposerContributionInline(admin.TabularInline):
    model = SongComposerContribution
    extra = 1
    ordering = ('position',)

@admin.register(Composer)
class ComposerAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'born', 'died', 'song_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'nationality')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'image', 'nationality', 'born', 'died', 'website')}),
        ('Biography', {'fields': ('bio',)}),
    )

    def song_count(self, obj):
        return obj.song_links.values('song_id').distinct().count()
    song_count.short_description = 'Songs'


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'composer_fk', 'composer', 'composition_type', 'created_at')
    list_filter = ('composer_fk', 'composition_type')
    search_fields = ('title', 'composer', 'composer_fk__name')
    inlines = [SongComposerContributionInline, MP3FileInline, NoteInline, ReferenceInline, SectionInline, LyricInline]


@admin.register(SongComposerContribution)
class SongComposerContributionAdmin(admin.ModelAdmin):
    list_display = ('song', 'composer', 'composition_type', 'position')
    list_filter = ('composition_type', 'composer')
    search_fields = ('song__title', 'composer__name')

@admin.register(MP3File)
class MP3Admin(admin.ModelAdmin):
    inlines = [LyricTimetampInline]

@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    list_display = ('song', 'voice_part', 'uploader', 'created_at', 'voicenote_request_title')

    def voicenote_request_title(self, obj):
        return obj.voicenote_request.title if obj.voicenote_request else "—"
    voicenote_request_title.short_description = "The Ministry"


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