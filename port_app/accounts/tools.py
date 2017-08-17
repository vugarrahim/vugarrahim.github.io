import hashlib
import datetime
import random
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage


# User kimi qeydiyyatdan kecenden sonra email tesdiq funksiyasi

def send_activation(user):
    salt = hashlib.sha1(str(random.random()).encode("utf-8")).hexdigest()[:10]
    key = hashlib.sha256(str(user.email + salt).encode("utf-8")).hexdigest()
    user.activation_key = key
    user.expiration_date = timezone.now() + datetime.timedelta(days=1)
    user.save()

    subject = "Confirmation of registration"
    txt = """Thank you for registration,
        please click the following link in order to confirm your registration:
        {link}?activation={key}
        """.format(link="".join([settings.HOST, reverse('accounts:confirm')]), key=key)
    to = [user.email]
    from_email = settings.EMAIL_HOST_USER
    EmailMessage(subject, txt, to=to, from_email=from_email).send()
