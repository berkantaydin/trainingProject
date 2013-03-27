from django.core.mail import send_mail
from django.utils.translation import gettext as _
from models import User
from models import Author
from django.core.urlresolvers import reverse

# Need for long time... Need Rabbit MQ..! Need some little good things.

# Daha sonra Q'dan gonderir hale getirilecek //BA--


def sendConfirmationMail(user_id):
    user = User.objects.get(id=user_id)

    if user.is_active:
        raise ValueError(_('%s is already activated') % user.username)

    author = Author.objects.get(user=user_id)
    link = reverse('pageConfirmMail', kwargs={'key': author.key_activation})

    return send_mail(_('Activation Mail'),
              _('Please click link for account confirmation %(confirmation_link)s') % {'confirmation_link': link},
              'noreply@example.com', [user.email], fail_silently=False)