# Generated by Django 3.2.25 on 2025-04-11 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0006_auto_20250411_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='slug',
            field=models.SlugField(max_length=255, null=True, unique=True),
        ),
    ]
