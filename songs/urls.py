from django.urls import path
from .views import song_list, song_detail, save_lyrics, add_song, save_mp3, add_mp3, add_note, add_reference, sync_lyrics, save_timestamp, generate_lyrics_view, generate_lrc
from . import views

urlpatterns = [
    path('', song_list, name="song_list"),
    path('songs/<int:pk>/', song_detail, name="song_detail"),
    path('add-song/', add_song, name="add_song"),

    path('song/<int:song_id>/save-lyrics/', save_lyrics, name='save_lyrics'),
    path('save-mp3/', save_mp3, name='save_mp3'),
    path('song/<int:song_id>/add-mp3/', add_mp3, name='add_mp3'),
    path('song/<int:song_id>/add-note/', add_note, name='add_note'),
    path('song/<int:song_id>/add-reference/', add_reference, name='add_reference'),

    # Lyrics Syncing
    path("sync/<int:song_id>/", sync_lyrics, name="sync-lyrics"),
    path("save-timestamp/", save_timestamp, name="save-timestamp"),
    path("generate_lrc/<int:song_id>/", generate_lrc, name="generate-lrc"),
    path('generate-lyrics/<int:song_id>/', generate_lyrics_view, name='generate-lyrics'),
    path('delete-lyric/<int:lyric_id>/', views.delete_lyric, name='delete-lyric'),
    path('sync-mp3/<int:mp3_id>/', views.sync_lyrics, name='sync-mp3'),   path('sync-mp3/<int:mp3_id>/', views.sync_lyrics, name='sync-mp3'),
]

