# Generated by Django 3.1.7 on 2021-03-05 11:28

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('test1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.SmallIntegerField()),
                ('author_id', models.SmallIntegerField()),
                ('download_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('club_id', models.SmallIntegerField()),
                ('keywords', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('add_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_edit_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.SmallIntegerField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paper_id', models.SmallIntegerField()),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.TextField()),
                ('author', models.ForeignKey(default=django.contrib.auth.models.User, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentClub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('acronym', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paper_id', models.SmallIntegerField()),
                ('file', models.FileField(upload_to='paper_files<django.db.models.fields.SmallIntegerField>')),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Referats',
        ),
    ]
