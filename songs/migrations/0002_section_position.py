# Generated by Django 3.2.25 on 2025-02-18 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='position',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
