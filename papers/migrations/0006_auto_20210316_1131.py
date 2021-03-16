# Generated by Django 3.1.7 on 2021-03-16 10:31

from django.db import migrations, models
import papers.models


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0005_auto_20210310_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coauthor',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(blank=True, upload_to=papers.models.paper_directory_path),
        ),
    ]
