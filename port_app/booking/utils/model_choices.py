from django.conf import settings
from django.utils.translation import ugettext_lazy as _

GENDER_CHOICES = (
    ('M', _('Male')),
    ('F', _('Female'))
)

BOOKING_TYPE_CHOICES = (
    ('1', _('One way')),
    ('2', _('Round trip'))
)

BOOKINGINFO_TYPE_CHOICES = (
    ('1', _('Away')),
    ('2', _('Return'))
)

TRANSIT_TYPE_CHOICES = (
    ('1', _('Transit')),
    ('2', _('Non Transit'))
)

TRANSACTION_TYPE_CHOICES = (
    ('income', _('Income')),
    ('expense', _('Expense'))
)

# form choices
CAR_LIMIT_PER_TYPE = [("%s" % x, "%s" % x) for x in range(settings.BOOKING_CARGO_LIMIT + 1)]
PASSENGER_LIMIT = [("%s" % x, "%s" % x) for x in range(settings.BOOKING_PASSENGER_LIMIT + 1)]