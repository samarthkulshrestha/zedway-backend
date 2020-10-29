from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Post(models.Model):
    TYPE_CHOICE = [
        ('IMG', 'Image'),
        ('AU', 'Audio'),
        ('VID', 'Video'),
        ('TXT', 'Text')
    ]
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    desc = models.TextField()
    file = models.FileField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICE, blank=True)
    is_safe = models.BooleanField(default=True)
    liked = models.ManyToManyField(User, default=None, blank=True, related_name='liked')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator', default=None, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    explore = models.BooleanField()

    def __str__(self):
        return str(self.slug)

    @property
    def num_likes(self):
        return self.liked.all().count()

    def save(self, *args, **kwargs):
        value = str(self.pk)
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class Tag(models.Model):
    tag = models.CharField(max_length=50)
    posts = models.ManyToManyField(Post, default=None, blank=True, related_name='posts_with_tag')
    followers = models.ManyToManyField(User, blank=True, default=None, related_name='tag_followers')

    def __str__(self):
        return self.tag


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike')
)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

    def __str__(self):
        return str(self.post)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', default=None, blank=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.user)


class PostReport(models.Model):
    post_to_report = models.ManyToManyField(Post, blank=True, related_name='post_to_report')
    reporting_user = models.ManyToManyField(User, blank=True, related_name='post_reporting_user')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reporting_user) + ' reported ' + str(self.post_to_report)


class CommentReport(models.Model):
    comment_to_report = models.ManyToManyField(Comment, blank=True, related_name='comment_to_report')
    reporting_user = models.ManyToManyField(User, blank=True, related_name='comment_reporting_user')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reporting_user) + ' reported ' + str(self.comment_to_report)

