from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Author(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='uploads')
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

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