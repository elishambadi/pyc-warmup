from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=255)
    lyrics = models.TextField()
    composer = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)  # new field for song likes

    def __str__(self):
        return self.title

class MP3File(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="mp3_files")
    file = models.FileField(upload_to='mp3/')
    voice_part = models.CharField(max_length=50, choices=[
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
    name = models.CharField(max_length=100)
    position = models.IntegerField(null=True, blank=True, default=None)

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

class ChoirMember(models.Model):
    USER_ROLES = (
        ("admin", "Admin"),
        ("member", "Member"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default="member")
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Comment(models.Model):
    # A comment may be related to either a Song or a specific LyricLine.
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    lyric_line = models.ForeignKey(LyricLine, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    # For replies, a comment may have a parent.
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="replies", null=True, blank=True)
    
    text = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
