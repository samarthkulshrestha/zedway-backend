# Generated by Django 3.0.8 on 2020-09-10 12:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_auto_20200910_0658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='following_genres',
        ),
    ]
