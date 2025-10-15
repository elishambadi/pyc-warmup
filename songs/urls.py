from django.urls import path
from .views import home, song_detail, save_lyrics, add_song, save_mp3, add_mp3, add_note, add_reference, sync_lyrics, save_timestamp, generate_lrc, delete_timestamp
from . import views

urlpatterns = [
    path('songs/', home, name="song_list"),
    path('songs/<slug:slug>/', song_detail, name="song_detail"),
    path('add-song/', add_song, name="add_song"),

    path('song/<int:song_id>/save-lyrics/', save_lyrics, name='save_lyrics'),
    path('save-mp3/', save_mp3, name='save_mp3'),
    path('song/<int:song_id>/add-mp3/', add_mp3, name='add_mp3'),
    path('song/<int:song_id>/add-note/', add_note, name='add_note'),
    path('song/<int:song_id>/add-reference/', add_reference, name='add_reference'),

    path('song/<slug:song_slug>/upload-voicenote/', views.upload_voicenote, name='upload_voicenote'),
    path('song/<slug:song_slug>/delete-voicenote/<int:voicenote_id>/', views.delete_voicenote, name='delete_voicenote'),
    path('song/<slug:song_slug>/approve-voicenote/<int:voicenote_id>/', views.approve_voicenote, name='approve_voicenote'),

    # Lyrics Syncing
    path("sync/<int:song_id>/", sync_lyrics, name="sync-lyrics"),
    path("save-timestamp/", save_timestamp, name="save-timestamp"),
    path("delete-timestamp/", delete_timestamp, name="delete-timestamp"),
    path("generate_lrc/<int:song_id>/", generate_lrc, name="generate-lrc"),
    path('delete-lyric/<int:lyric_id>/', views.delete_lyric, name='delete-lyric'),
    path('sync-mp3/<int:mp3_id>/', views.sync_lyrics, name='sync-mp3'),

    path('comments/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comments/<int:comment_id>/dislike/', views.dislike_comment, name='dislike_comment'),
    path('comments/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('add_song_comment/<int:song_id>/', views.add_song_comment, name='add_song_comment'),

    path('delete-song/<int:song_id>/', views.delete_song, name='delete-song'),
    path('delete-mp3/<int:mp3_id>/', views.delete_mp3, name='delete-mp3'),

    # VoiceNote requests
    path('voicenote-request/new/', views.add_voicenote_request, name='add_voicenote_request'),
    path('submit-voicenotes/', views.upload_voicenotes_for_request, name='upload_voicenotes_for_request'),

]
