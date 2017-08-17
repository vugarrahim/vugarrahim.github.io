from django.db import models
from booking.models import Booking
from django.contrib.postgres.fields import JSONField
from auditlog.registry import auditlog


class PaymentInfo(models.Model):
    booking = models.ForeignKey(Booking)
    payment_key = models.CharField(max_length=255, blank=True, null=True)
    hash_code = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=25, blank=True, null=True)
    get_payment_key = JSONField(blank=True, null=True, )
    get_payment_result = JSONField(blank=True, null=True)
    # status = models.CharField(max_length=20)
    # message = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}{}".format(self.booking.booking_id, self.payment_key)

auditlog.register(PaymentInfo)
