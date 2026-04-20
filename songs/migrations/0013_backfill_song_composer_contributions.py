from django.db import migrations


def backfill_song_contributions(apps, schema_editor):
    Song = apps.get_model('songs', 'Song')
    SongComposerContribution = apps.get_model('songs', 'SongComposerContribution')

    for song in Song.objects.all():
        if SongComposerContribution.objects.filter(song_id=song.id).exists():
            continue
        if song.composer_fk_id:
            SongComposerContribution.objects.create(
                song_id=song.id,
                composer_id=song.composer_fk_id,
                composition_type=song.composition_type or 'original',
                position=1,
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0012_auto_20260420_0904'),
    ]

    operations = [
        migrations.RunPython(backfill_song_contributions, noop_reverse),
    ]
