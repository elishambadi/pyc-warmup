# Generated by Django 3.2.25 on 2025-04-09 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0003_voicenote_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voicenote',
            name='name',
            field=models.CharField(default='', max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='VoiceNoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('deadline', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('songs', models.ManyToManyField(to='songs.Song')),
            ],
        ),
        migrations.AddField(
            model_name='voicenote',
            name='voicenote_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voicenotes', to='songs.voicenoterequest'),
        ),
    ]
