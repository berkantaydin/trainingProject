from celery.task import task
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from models import User
from models import Author
from models import Comment
from django.core.urlresolvers import reverse
from PIL import Image


@task(ignore_result=True)
def sendConfirmationMail(user_id):
    user = User.objects.get(id=user_id)
    author = Author.objects.get(user=user)
    if author.is_verified:
        raise ValueError(_('%s is already activated') % user.username)

    author = Author.objects.get(user=user_id)
    link = reverse('pageConfirmMail', kwargs={'key': author.key_activation})

    return send_mail(_('Activation Mail'),
                     _('Please click link for account confirmation %(confirmation_link)s') % {
                         'confirmation_link': link},
                     'noreply@example.com', [user.email], fail_silently=False)


@task(ignore_result=True)
def sendCommentConfirmationMail(comment_id):
    comment = Comment.objects.get(id=comment_id)
    link = reverse('pageConfirmCommentWithMail',
                   kwargs={'post_id': comment.base_post_id, 'comment_id': comment.id, 'key': comment.key_activation})

    return send_mail(_('Comment Activation Mail'),
                     _('Please click link for comment confirmation %(confirmation_link)s') % {
                         'confirmation_link': link},
                     'noreply@example.com', [comment.tmp_mail], fail_silently=False)


@task(ignore_result=True)
def updateComments(user_id):
    author = Author.objects.get(id=user_id)
    Comment.objects.filter(tmp_email=author.email).update(author=author, tmp_email='', tmp_name='')
    return True


@task(ignore_result=True)
def createProfileImages(user_id):
    size = 64, 64
    name = str(user_id) + "_avatar.jpg"
    user = User.objects.get(id=user_id)
    author = Author.objects.get(user=user)
    im = Image.open(author.avatar)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save('uploads/' + str(name), "JPEG")
    #DB Kaydet
    author.avatar = name
    author.save()
    return True