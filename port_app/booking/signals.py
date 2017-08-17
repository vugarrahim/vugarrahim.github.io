from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .utils.tools import get_or_none
from .models import TransactionAgentBalance, Balance, BookingCargoItem, BookingPassengerItem, VesselsSchedule
from .tasks import *
import logging

# Get an instance of a logger
logr = logging.getLogger(__name__)


# @receiver(post_save, sender=VesselsSchedule, dispatch_uid="vessel schedule capacity")
# def vessel_schedule_capacity(created, sender, update_fields, instance=None, **kwargs):
#     if created:
#         instance.current_cargo_capacity = instance.vessel.load_capacity


@receiver(post_save, sender=BookingInformation, dispatch_uid="booking_information_save")
def booking_information_status(created, sender, update_fields, instance=None, **kwargs):
    if instance.done_cache != instance.done:
        booking_done.delay(instance.booking.id)


@receiver(post_save, sender=BookingCargoItem, dispatch_uid="booking_cargo_save")
def booking_cargo_post_save(created, sender, update_fields, instance=None, **kwargs):
    if instance.is_arrived_cache != instance.is_arrived:
        booking_information_done.delay(instance.booking.id)
    else:
        if created:
            booking_information_done.delay(instance.booking.id)


@receiver(post_save, sender=BookingPassengerItem, dispatch_uid="booking_passenger_save")
def booking_passenger_item_done(created, sender, update_fields, instance=None, **kwargs):
    if instance.is_arrived_cache != instance.is_arrived:
        booking_information_done.delay(instance.booking.id)
    else:
        if created:
            booking_information_done.delay(instance.booking.id)


# Transaksiya zamani user veya comapny ucun balance varsa update olunur yoxdursa yaradilir.
# transaction_type 'income' olsa var olan balance artirilir yoxdursa musbet balance yaradilir.
# transaction_type 'expense' olsa var olan balance azaldir ve ya menfi balance yaradilir
@receiver(post_save, sender=TransactionAgentBalance, dispatch_uid='transaction_balance')
def transaction_balance(created, sender, update_fields, instance=None, **kwargs):
    balance = get_or_none(Balance, owner=instance.owner)
    if instance.owner.groups.filter(name='agent'):
        if created:
            if balance:
                if instance.transaction_type == 'income':
                    balance.amount += instance.amount
                    balance.save()
                else:
                    balance.amount -= instance.amount
                    balance.save()
            else:
                if instance.transaction_type == 'income':
                    balance = Balance(owner=instance.owner, amount=instance.amount)
                    balance.save()
                else:
                    balance = Balance(owner=instance.owner, amount=-instance.amount)
                    balance.save()
        else:
            if instance.transaction_type_cache != instance.transaction_type:
                if balance:
                    if instance.transaction_type == 'income':
                        balance.amount += instance.amount_cache
                        balance.amount += instance.amount
                        balance.save()
                    elif instance.transaction_type == 'expense':
                        balance.amount -= instance.amount_cache
                        balance.amount -= instance.amount
                        balance.save()
                        # else:
                        #     balance.amount -= instance.amount
                        #     balance.save()
                else:
                    if instance.transaction_type == 'income':
                        balance = Balance(owner=instance.owner, amount=instance.amount)
                        balance.save()
                    else:
                        balance = Balance(owner=instance.owner, amount=-instance.amount)
                        balance.save()
            else:
                if balance:
                    if instance.transaction_type == 'income':
                        balance.amount -= instance.amount_cache
                        balance.amount += instance.amount
                        balance.save()
                    else:
                        balance.amount += instance.amount_cache
                        balance.amount -= instance.amount
                        balance.save()
