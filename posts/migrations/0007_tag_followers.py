# Generated by Django 3.0.8 on 2020-09-13 10:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_auto_20200913_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='followers',
            field=models.ManyToManyField(blank=True, default=None, related_name='tag_followers', to=settings.AUTH_USER_MODEL),
        ),
    ]
