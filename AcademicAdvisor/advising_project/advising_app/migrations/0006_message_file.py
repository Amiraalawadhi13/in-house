# Generated by Django 4.0.3 on 2023-12-19 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advising_app', '0005_tutorprofile_end_time_tutorprofile_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='message_files/'),
        ),
    ]