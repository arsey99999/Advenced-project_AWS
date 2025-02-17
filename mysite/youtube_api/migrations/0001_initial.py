# Generated by Django 5.1.5 on 2025-01-27 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='YouTubeVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('video_id', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('captions', models.TextField(blank=True, null=True)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
