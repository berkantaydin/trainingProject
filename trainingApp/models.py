from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
import random


class Author(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='uploads')
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    key_activation = models.CharField(max_length=12, default=str(random.random())[2:14])

    def email(self):
        return self.user.email

    def total_posts(self):
        total = Post.objects.filter(author=self.user.id).count()
        return total

    def __unicode__(self):
        return '%s' % self.user.username


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category)
    author = models.ForeignKey(Author)
    text_title = models.CharField(max_length=70)
    text_body = models.TextField()
    date_pub = models.DateTimeField(default=datetime.now)


class Comment(models.Model):
    author = models.ForeignKey(Author, null=True, blank=True)
    parent = models.PositiveIntegerField(blank=False, null=False)
    is_root = models.BooleanField(default=True)  # On post or On comment
    is_pending = models.BooleanField(default=True)
    date_pub = models.DateTimeField(default=datetime.now)

    '''
    Onaylanmış child post sayısı
    '''
    def total_childs(self):
        total = Comment.objects.filter(is_root=False).filter(is_pending=False).filter(parent=self.pk).count()
        return total