# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django_extensions.db.fields import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import random


class Author(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='uploads')
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    key_activation = models.CharField(max_length=12, default=str(random.random())[2:14])
    slug = AutoSlugField(_('slug'), max_length=50, unique=True, populate_from=('user',))

    def email(self):
        return self.user.email

    def total_posts(self):
        total = Post.objects.filter(author=self.user.author).count()
        return total

    def total_comments(self):
        total = Comment.objects.filter(author=self.user.author).count()
        return total

    def last_post(self):
        try:
            last_post = Post.objects.filter(author=self.user.author).filter(
                date_pub__lte=datetime.now()).order_by('-date_pub')[0]
            return last_post
        except Exception:
            return None

    def __unicode__(self):
        return '%s' % self.user.username


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = AutoSlugField(_('slug'), max_length=50, unique=True, populate_from=('name',))

    def post_count(self):
        count = Post.objects.filter(category=self).count()
        return count

    def __unicode__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category)
    author = models.ForeignKey(Author)
    slug = AutoSlugField(_('slug'), max_length=50, unique=True, populate_from=('text_title',))
    text_title = models.CharField(max_length=70)
    text_body = models.TextField()
    date_pub = models.DateTimeField(default=datetime.now)


class Comment(models.Model):
    author = models.ForeignKey(Author, null=True, blank=True)
    parent_type = models.ForeignKey(ContentType)
    parent_id = models.PositiveIntegerField()
    parent_content = generic.GenericForeignKey('parent_type', 'parent_id')
    content = models.TextField(null=False)
    tmp_name = models.CharField(
        max_length=75)  # Temp olarak yazan kişinin adı -> sonradan içi boşaltılacak ve görmezden gelinecek
    tmp_mail = models.EmailField(max_length=75)  # Temp olarak yazan kişinin maili -> sonradan eşlenecek
    key = models.CharField(max_length=12, default='')
    is_pending = models.BooleanField(default=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    '''
    Onaylanmis child post sayisi
    '''

    def total_childs(self):
        total = Comment.objects.filter(is_root=False).filter(is_pending=False).filter(parent=self.pk).count()
        return total