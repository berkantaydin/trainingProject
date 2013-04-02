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
    name = models.CharField(max_length=50, unique=True, error_messages={
        'required': _('Please insert a name for new category'),
        'unique': _('This category is already been registered. Please choose an another one.'), },
        verbose_name=_('Name'),
        help_text=_('The name is how it appears on your site.'),)

    def __unicode__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category)
    author = models.ForeignKey(Author)
    text_title = models.CharField(max_length=70)
    text_body = models.TextField()
    date_pub = models.DateTimeField(default=datetime.now)


class Comment(models.Model):
    author = models.ForeignKey(Author)
    parent = models.ManyToManyField('self', symmetrical=False)
    text_body = models.TextField()
    is_hide = models.BooleanField(default=True)
    date_pub = models.DateTimeField(default=datetime.now)
    to = models.CharField(max_length=1, choices=(
        ('p', 'to Post'),  # Yorum posta atildi.
        ('c', 'to Comment')))  # Yorum bir baska commente atildi.
