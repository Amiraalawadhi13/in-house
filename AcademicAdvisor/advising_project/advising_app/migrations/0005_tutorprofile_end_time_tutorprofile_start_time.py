# Generated by Django 4.0.3 on 2023-12-11 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advising_app', '0004_alter_course_course_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
