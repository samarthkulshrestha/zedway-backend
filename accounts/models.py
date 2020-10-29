from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from posts.models import Post, Tag
import json


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.FileField(default='dummy.png', upload_to='profile_pictures', blank=True)
    bio = models.TextField(max_length=200, blank=True)
    birth_date = models.DateField(null=True)
    age = models.IntegerField(default=0, blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    following = models.ManyToManyField(User, blank=True, related_name='following')
    following_tags = models.ManyToManyField(Tag, blank=True, default=None, related_name='following_tags')
    verified = models.BooleanField(default=False)
    blocked = models.ManyToManyField(User, blank=True, related_name='blocked_users')
    accent1 = models.CharField(max_length=20, default='#aab4e4')
    accent2 = models.CharField(max_length=20, default='#dfa8b5')

    def __str__(self):
        return self.user.username

    def get_user_feed(self):
        following = self.following.all()
        posts = Post.objects.filter(creator=self.user).distinct()
        following_tags = self.following_tags.all()
        if self.age < 16:
            for user in following:
                posts = posts | Post.objects.filter(creator__exact=user, is_safe=True).distinct()
            for tag in following_tags:
                posts = posts | tag.posts.filter(is_safe=True).distinct()
            return (posts.order_by('created_on'))
        else:
            for user in following:
                posts = posts | Post.objects.filter(creator__exact=user).distinct()
            for tag in following_tags:
                posts = posts | tag.posts.all().distinct()
            return (posts.order_by('created_on'))

    def save(self, *args, **kwargs):
        value = self.user.username
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


def create_user_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(create_user_profile, sender=User)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()


class UserReport(models.Model):
    user_to_report = models.ManyToManyField(User, blank=True, related_name='user_to_report')
    reporting_user = models.ManyToManyField(User, blank=True, related_name='reporting_user')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reporting_user) + ' reported ' + str(self.user_to_report)


