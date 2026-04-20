from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import Group


class Composer(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    bio = models.TextField(blank=True, help_text="Short biography shown on the composer page")
    image = models.ImageField(upload_to='composers/', null=True, blank=True)
    born = models.CharField(max_length=100, blank=True, help_text="e.g. 1856 or March 3, 1856")
    died = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('composer_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Composer.objects.filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Song(models.Model):
    COMPOSITION_TYPE_CHOICES = [
        ('original', 'Original'),
        ('arranged', 'Arranged'),
        ('transcribed', 'Transcribed'),
    ]

    title = models.CharField(max_length=255)
    lyrics = models.TextField()
    composer = models.CharField(max_length=255, null=True, blank=True)
    composer_fk = models.ForeignKey(
        Composer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='songs', verbose_name='Composer (from table)'
    )
    composition_type = models.CharField(
        max_length=20, choices=COMPOSITION_TYPE_CHOICES,
        default='original', blank=True
    )
    slug = models.SlugField(max_length=255, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)  # new field for song likes
    youtube_link = models.URLField(null=True, blank=True)  # new field for YouTube link
    slogan = models.CharField(max_length=1024, null=True, blank=True)  # new field for slogan
    views = models.IntegerField(default=0)  # track page views

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("song_detail", args=[self.slug])

    
    def save(self, *args, **kwargs):
        if not self.slug:
            composer_name = self.composer_fk.name if self.composer_fk else (self.composer or '')
            base_slug = slugify(f"{self.title} {composer_name}")
            unique_slug = base_slug
            counter = 1

            # Ensure uniqueness
            while Song.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

class MP3File(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="mp3_files")
    file = models.FileField(upload_to='mp3/')
    voice_part = models.CharField(max_length=200, choices=[
        ('Soprano 1', 'Soprano 1'), ('Soprano 2', 'Soprano 2'),
        ('Alto 1', 'Alto 1'), ('Alto 2', 'Alto 2'),
        ('Tenor 1', 'Tenor 1'), ('Tenor 2', 'Tenor 2'),
        ('Bass 1', 'Bass 1'), ('Bass 2', 'Bass 2'),
        ('Lead 1', 'Lead 1'), ('Lead 2', 'Lead 2'),
        ('Other', 'Other')
    ])

    def __str__(self):
        return f"{self.song.title} - {self.voice_part}"

    def get_timestamps(self):
        """Get all timestamps for this MP3 file ordered by lyric line order"""
        return self.lyric_timestamps.select_related('lyric_line').order_by('lyric_line__order')

    @property
    def is_fully_synced(self):
        """Check if all lyric lines have timestamps for this MP3"""
        total_lyrics = self.song.lyric_lines.count()
        total_timestamps = self.lyric_timestamps.count()
        return total_lyrics == total_timestamps
    
class Section(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100, blank=True)
    position = models.IntegerField(null=True, blank=True, default=None)
    instruction = models.CharField(max_length=200, null=True, blank=True)
    passage = models.TextField(null=True, blank=True)  # new field for passage

    def __str__(self):
        return self.name

class LyricLine(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="lyric_lines")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lyric_lines", null=True, blank=True)
    text = models.TextField()
    VOICE_PART_CHOICES = [
        ('soprano', 'Soprano'),
        ('alto', 'Alto'),
        ('tenor', 'Tenor'),
        ('bass', 'Bass'),
    ]

    voice_part = models.CharField(
        max_length=10,
        choices=VOICE_PART_CHOICES,
        null=True,
        blank=True
    )

    order = models.IntegerField()
    instruction = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ["order"]

class LyricTimestamp(models.Model):
    lyric_line = models.ForeignKey(LyricLine, on_delete=models.CASCADE, related_name='timestamps')
    mp3_file = models.ForeignKey(MP3File, on_delete=models.CASCADE, related_name='lyric_timestamps')
    timestamp = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('lyric_line', 'mp3_file')


# Song structure models

class SongStructure(models.Model):
    """Defines the order of sections in the song"""
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="structure")
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.song.title} - {self.section.name} (Part {self.order})"


class Note(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="notes")
    section = models.CharField(max_length=100)
    content = models.TextField()

class Reference(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="references")
    link = models.URLField()


class Comment(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="comments", default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", default=1)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="replies", null=True, blank=True)
    
    text = models.TextField()
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.song.title}: {self.text[:50]}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"



class VoiceNoteRequest(models.Model):
    title = models.CharField(max_length=255)
    songs = models.ManyToManyField('Song')  # assuming you already have a Song model
    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Deadline: {self.deadline})"



class VoiceNote(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='voice_notes')  # Multiple voice notes per song
    file = models.FileField(upload_to='voice_notes/')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_voice_notes')
    voice_part = models.CharField(max_length=200, choices=[  # Specify the voice part
        ('Soprano', 'Soprano'),
        ('Alto', 'Alto'),
        ('Tenor', 'Tenor'),
        ('Bass', 'Bass'),
        ('Other', 'Other'),
    ])
    approved = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)  # Comment field to specify voice type
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, default="")  # Add unique name field

    voicenote_request = models.ForeignKey(
        VoiceNoteRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voicenotes"
    )

    def __str__(self):
        return f"{self.song.title} - {self.voice_part} ({self.uploader.username})"