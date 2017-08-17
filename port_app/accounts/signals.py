from .tools import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from booking.utils.tools import get_or_none
from .tasks import *
from .models import Agent
from booking.models import Balance
# import the logging library
import logging

# Get an instance of a logger
logr = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid="user registration signal")
def user_email_send(created, sender, instance=None, **kwargs):
    if created and not instance.is_active:
        send_activation_task.delay(instance.id)


@receiver(post_save, sender=Agent, dispatch_uid="balance create")
def agent_balance(created, sender, instance=None, **kwargs):
    if created:
        if not Balance.objects.filter(owner=instance.owner):
            balance = Balance(owner=instance.owner, amount=0)
            balance.save()


cardType = "v"
lang = "lv"
merchantName = "portofbaku"
auth_key = "ad1947d345624106b67a35ebd4f6ed76"
description = "test payment"
amount = 11