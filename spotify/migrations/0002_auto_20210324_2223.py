# Generated by Django 3.1.7 on 2021-03-25 02:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SpotifyToken',
            new_name='SpotifyTokens',
        ),
    ]
