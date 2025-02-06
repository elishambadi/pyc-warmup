from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=255)
    lyrics = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    composer = models.CharField(max_length=255, null=True)


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
