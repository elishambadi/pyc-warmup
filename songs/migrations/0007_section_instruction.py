# Generated by Django 3.2.25 on 2025-02-25 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0006_lyricline_instruction'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='instruction',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
