from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import logging
from auditlog.registry import auditlog
from booking.utils.model_choices import BOOKING_TYPE_CHOICES, TRANSIT_TYPE_CHOICES, GENDER_CHOICES, \
    TRANSACTION_TYPE_CHOICES, BOOKINGINFO_TYPE_CHOICES
from .utils.tools import rand_key, rand_vessel_shedule

# Get an instance of a logger
logr = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


# BUTUN YARADILAN PERMISSION-LAR UCUN
# Eger userin sadece ozunun sahibi oldugu obyekti gormeyini isteyirikse
# hemin userin daxil oldugu groupa usere model_name_view permissionunu veririk.
# Eger userin butun obyektleri gormeyini isteyirikse onda hemin
# userin daxil oldugu groupa model_name_all_view permissionunu veririk.
# Hansisa groupa daxil olan userin obyekte sahib olmasini isteyirkse
# hemin userin daxil oldugu groupa model_name_object_owner permissionunu veririk


# ----------------------------------------------------------------------------------------
# Sistemde istifade olunacaq portlar
class Port(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Port')
        verbose_name_plural = _('Ports')
        permissions = (("port_view", "Can view Port"),
                       ("port_all_view", "Can view ALL Port")
                       )


auditlog.register(Port)


# ----------------------------------------------------------------------------------------
class Terminal(models.Model):
    name = models.CharField(max_length=50, verbose_name="Terminal name")
    port = models.ForeignKey("Port", verbose_name="Port")
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Terminal')
        verbose_name_plural = _('Terminals')
        permissions = (("terminal_view", "Can view Terminal"),
                       ("terminal_all_view", "Can view ALL Terminal")
                       )


auditlog.register(Terminal)


# ----------------------------------------------------------------------------------------
# Portdan gedilecek istiqametler
class Direction(models.Model):
    # connection
    from_d = models.ForeignKey("Terminal", verbose_name=_('From'), related_name='from_d')
    to = models.ForeignKey("Terminal", verbose_name=_('To'), related_name='to')

    # information
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str('%s --> %s' % (self.from_d.name, self.to.name))

    class Meta:
        verbose_name = _('Direction')
        verbose_name_plural = _('Directions')
        unique_together = (("from_d", "to"),)
        permissions = (("direction_view", "Can view Direction"),
                       ("direction_all_view", "Can view ALL Direction")
                       )

    # Override olunmus clean ve save metodlarinin ikisininde meqsedi from_t ve to propertylerinin eyni olmamasini yoxlamaqdir
    def clean(self, *args, **kwargs):
        if self.from_d == self.to:
            raise ValidationError(_('İki eyni istiqamət seçmək olmaz'))
        super(Direction, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.from_d == self.to:
            raise ValidationError(_('İki eyni istiqamət seçmək olmaz'))
        super(Direction, self).save(*args, **kwargs)


auditlog.register(Direction)


# --------------------------------------------------------------------------
# Her port muxtelif istiqametler ucun cargonun metrini ferqli qiymetlerle tenzimleyir.
class PortFee(models.Model):
    port = models.ForeignKey("Port", verbose_name=_("Port"))
    direction = models.ForeignKey("Direction", verbose_name=_("Direction"))
    price = models.FloatField(verbose_name=_("Price"))
    transit_price = models.FloatField(verbose_name=_("Transit price"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} azn/m".format(self.price)

    class Meta:
        verbose_name = _('PortFee')
        verbose_name_plural = _('PortFees')
        unique_together = (("port", "direction"),)


auditlog.register(PortFee)


# ----------------------------------------------------------------------------------------
# Portda olan gemiler
class Vessel(models.Model):
    # general information
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    cargo_availability = models.BooleanField()
    passenger_availability = models.BooleanField()
    load_capacity = models.FloatField(
        verbose_name=_("Load Capacity"))  # geminin yuk goturme yerinin uzunlugu metrle ifade olunur

    # technical inoformation
    imo = models.CharField(max_length=50, blank=True, null=True)
    mmsi = models.CharField(max_length=50, blank=True, null=True)
    call_sign = models.CharField(max_length=50, blank=True, null=True)

    # moderetional information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Vessel')
        verbose_name_plural = _('Vessels')
        permissions = (("vessel_view", "Can view Vessel"),
                       ("vessel_all_view", "Can view ALL Vessels")
                       )


auditlog.register(Vessel)


# ----------------------------------------------------------------------------------------
# Portlarin hereket cedveli
class VesselsSchedule(models.Model):
    vessel = models.ForeignKey("Vessel", verbose_name=_("Vessel"))
    direction = models.ForeignKey("Direction", verbose_name=_("Direction"))
    arrival_date = models.DateTimeField(verbose_name=_("Arrival date"))
    departure_date = models.DateTimeField(verbose_name=_("Departure date"))
    schedule_id = models.CharField(max_length=25, verbose_name=_("Schedule ID"), default=rand_vessel_shedule,
                                   unique=True)
    description = models.TextField(blank=True, null=True)
    current_passenger_count = models.IntegerField(blank=True, null=True)
    current_cargo_capacity = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.schedule_id)

    def get_absolute_url(self):
        return reverse("booking:vessels-schedule-update", kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        s = 0
        if self.pk is None:
            self.current_cargo_capacity = self.vessel.load_capacity
            for vessel_p_c in self.vessel.capacities.all():
                s += vessel_p_c.count * vessel_p_c.passenger_transport_type.passenger_count
            self.current_passenger_count = s
        try:
            super(VesselsSchedule, self).save(*args, **kwargs)
        except:
            self.schedule_id = rand_vessel_shedule()
            super(VesselsSchedule, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Vessels Schedule')
        verbose_name_plural = _('Vessels Schedules')
        permissions = (("vesselschedule_view", "Can view Vessels Schedule"),
                       ("vesselschedule_all_view", "Can view ALL Vessels Schedules")
                       )


auditlog.register(VesselsSchedule)


# ----------------------------------------------------------------------------------------
# Cargolarin tipi. meselen car < 1.5 m
class CargoType(models.Model):
    name = models.CharField(max_length=25)
    length = models.FloatField(verbose_name=_("Length"))
    height = models.FloatField(verbose_name=_("Height"))

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Cargo Type')
        verbose_name_plural = _('Cargo Types')
        permissions = (("cargotype_view", "Can view CargoType"),
                       ("cargotype_all_view", "Can view ALL CargoTypes")
                       )


auditlog.register(CargoType)


# ----------------------------------------------------------------------------------------
# Sernisin dasima ucun istifade olunan tipler, mes kayut,vip zal
class PassengerTransportType(models.Model):
    name = models.CharField(max_length=25, verbose_name=_("Name"))
    passenger_count = models.IntegerField(verbose_name=_("Count"))
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Passenger Transport Type')
        verbose_name_plural = _('Passenger Transport Types')
        permissions = (("passengertransporttype_view", "Can view PassengerTransportType"),
                       ("passengertransporttype_all_view", "Can view ALL PassengerTransportTypes")
                       )


auditlog.register(PassengerTransportType)


# ----------------------------------------------------------------------------------------
# Gemilerin cargo tiplerine gore dasima tarifi
class VesselCargoFee(models.Model):
    vessel = models.ForeignKey("Vessel", verbose_name=_("Vessel"))
    direction = models.ForeignKey("Direction", verbose_name=_("Direction"))
    cargo_type = models.ForeignKey("CargoType", verbose_name=_("Cargo type"))
    price = models.FloatField(verbose_name=_("Price"))
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.price)

    class Meta:
        verbose_name = _('Vessel Cargo Fee')
        verbose_name_plural = _('Vessel Cargo Fees')
        permissions = (("vesselcargofee_view", "Can view VesselCargoFee"),
                       ("vesselcargofee_all_view", "Can view ALL VesselCargoFees")
                       )


auditlog.register(VesselCargoFee)


# ----------------------------------------------------------------------------------------
# Sernisinlerin transport typena gore dasima tarifi
class VesselPassengerFee(models.Model):
    vessel = models.ForeignKey("Vessel", verbose_name=_("Vessel"))
    direction = models.ForeignKey("Direction", verbose_name=_("Direction"))
    passenger_transport_type = models.ForeignKey("PassengerTransportType", verbose_name=_("Passenger transport type"))
    price = models.FloatField(verbose_name=_("Price"))
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.price)

    class Meta:
        verbose_name = _('Vessel Passenger Fee')
        verbose_name_plural = _('Vessel Passenger Fees')


auditlog.register(VesselPassengerFee)


# ----------------------------------------------------------------------------------------
# Gemilerin sernisin tutumu
class VesselPassengerCapacity(models.Model):
    vessel = models.ForeignKey("Vessel", verbose_name=_("Vessel"), related_name="capacities")
    passenger_transport_type = models.ForeignKey("PassengerTransportType", verbose_name=_("Passenger transport type"),
                                                 related_name="capacities")
    count = models.IntegerField(verbose_name=_("Count"))

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = _('Vessel Passenger Capacity')
        verbose_name_plural = _('Vessel Passenger Capacities')


auditlog.register(VesselPassengerCapacity)


# ------------------------------------------------------------------------------------------
class Booking(models.Model):
    # information
    owner = models.ForeignKey(User, blank=True, null=True, verbose_name=_("Owner"))
    booking_id = models.CharField(max_length=15, unique=True, default=rand_key)
    booking_type = models.CharField(max_length=25, choices=BOOKING_TYPE_CHOICES)
    transit_type = models.CharField(max_length=25, choices=TRANSIT_TYPE_CHOICES)
    cargo_count = models.IntegerField(verbose_name=_("Cargo count"), default=0)
    passenger_count = models.IntegerField(verbose_name=_("Passenger count"), default=0)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_mail = models.EmailField(blank=True, null=True)
    ticket_pdf = models.FileField(upload_to="booking_ticket/", blank=True, null=True)
    done = models.BooleanField(verbose_name=_("Done"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.booking_id)

    def __init__(self, *args, **kwargs):
        super(Booking, self).__init__(*args, **kwargs)
        self.done_cache = self.done

    def get_absolute_url(self):
        return reverse('booking:booking-admin-update', kwargs={'pk': self.pk})

    # tekrar olmamasi ucun
    def save(self, *args, **kwargs):
        try:
            super(Booking, self).save(*args, **kwargs)
        except:
            self.booking_id = rand_key()
            super(Booking, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        permissions = (
            ("bookingcheckin_view", "Can check in Booking"),
            ("booking_view", "Can view Booking"),
            ("booking_all_view", "Can view ALL Bookings"),
        )


auditlog.register(Booking)


# ------------------------------------------------------------------------------------------
# Sifaris haqqinda melumat
class BookingInformation(models.Model):
    booking = models.ForeignKey("Booking", blank=True, null=True, related_name="bookings")
    vessel_schedule = models.ForeignKey("VesselsSchedule", verbose_name=_("Voyage"), related_name="booking_infos")
    done = models.BooleanField(verbose_name=_("Done"), default=False)
    type = models.CharField(max_length=25, choices=BOOKINGINFO_TYPE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.pk is None:
            if BookingInformation.objects.filter(booking=self.booking).count() == 2:
                raise ValidationError("Secilen bookinge bagli yalniz bir ve ya iki bookinginformation yaratmaq olar")
        super(BookingInformation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if BookingInformation.objects.filter(booking=self.booking).count() == 2:
                raise ValidationError("Secilen bookinge bagli yalniz bir ve ya iki bookinginformation yaratmaq olar")
        super(BookingInformation, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(BookingInformation, self).__init__(*args, **kwargs)
        self.done_cache = self.done

    def __str__(self):
        return "{}: {}".format(self.booking.booking_id, self.pk)

    class Meta:
        verbose_name = _('Booking Information')
        verbose_name_plural = _('Booking Information')
        permissions = (("bookinginformation_view", "Can view Booking"),
                       ("bookinginformation_all_view", "Can view ALL Bookings"),
                       ("bookinginformation_super_create", "Can SUPER create Booking"),
                       ("bookinginformation_object_owner", "Can own Booking"),
                       )


auditlog.register(BookingInformation)


# --------------------------------------------------------------------------------------------------------
class BookingCargoItem(models.Model):
    booking = models.ForeignKey("BookingInformation", verbose_name=_("Booking"), related_name="cargoes")
    ticket_id = models.CharField(max_length=25, unique=True, blank=True, null=True)
    cargo_type = models.ForeignKey("CargoType", verbose_name=_("Cargo type"))
    mark = models.CharField(max_length=25, verbose_name=_("Mark/Model"))
    plate_no = models.CharField(max_length=25, verbose_name=_("Plate NO"))
    is_arrived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(BookingCargoItem, self).__init__(*args, **kwargs)
        self.is_arrived_cache = self.is_arrived

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.ticket_id = self.booking.booking.booking_id + '-' + rand_vessel_shedule()
        super(BookingCargoItem, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.ticket_id)

    @property
    def class_name(self):
        return "cargo"

    class Meta:
        verbose_name = _('Booking Cargo Item')
        verbose_name_plural = _('Booking Cargo Items')
        permissions = (("bookingcargoitem_view", "Can view Booking Cargo Item"),
                       ("bookingcargoitem_all_view", "Can view ALL Booking Cargo Item"),
                       ("bookingcargoitem_super_create", "Can super create Booking Cargo Item"),
                       )


auditlog.register(BookingCargoItem)


# --------------------------------------------------------------------------------------------------------
class BookingPassengerItem(models.Model):
    booking = models.ForeignKey("BookingInformation", verbose_name=_("Booking"), related_name="passengers")
    passenger_transport_type = models.ForeignKey("PassengerTransportType", verbose_name=_("Passenger transport type"))
    ticket_id = models.CharField(max_length=25, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=25, verbose_name=_("First name"))
    last_name = models.CharField(max_length=25, verbose_name=_("Last name"))
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name=_("Gender"))
    passport = models.CharField(max_length=25, verbose_name=_("Passport"))
    birth_date = models.DateField(verbose_name=_("Birth date"))
    is_arrived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(BookingPassengerItem, self).__init__(*args, **kwargs)
        self.is_arrived_cache = self.is_arrived

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def class_name(self):
        return "passenger"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.ticket_id = self.booking.booking.booking_id + '-' + rand_vessel_shedule()
        super(BookingPassengerItem, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Booking Passenger Item')
        verbose_name_plural = _('Booking Passenger Items')
        permissions = (("bookingpassengeritem_view", "Can view Booking Passenger Item"),
                       ("bookingpassengeritem_all_view", "Can view ALL Booking Passenger Item"),
                       ("bookingpassengeritem_super_create", "Can SUPER create Booking Passenger Item"),
                       )


auditlog.register(BookingPassengerItem)


# ----------------------------------------------------------------------------------------
# Agentlerin balansi
class Balance(models.Model):
    owner = models.OneToOneField(User, verbose_name=_("Owner"))
    amount = models.FloatField(verbose_name=_("Amount"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} : {}".format(self.owner.get_full_name(), str(self.amount))

    def get_absolute_url(self):
        return reverse('booking:agent-balance-update', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Balance')
        verbose_name_plural = _('Balances')
        permissions = (("balance_view", "Can view Balance"),
                       ("balance_all_view", "Can view ALL Balances"),
                       ("balance_object_owner", "Can own Balance")
                       )


auditlog.register(Balance)


# # Agentlerin fakturasi
# class Invoice(models.Model):
#     # Connection fields
#     owner = models.ForeignKey(User)
#     booking = models.OneToOneField(BookingInformation)
#
#     # İnformation fields
#     amount = models.FloatField()
#     is_pay = models.BooleanField(verbose_name=_('Payed'), default=False)
#
#     # moderation information
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.amount)
#
#     class Meta:
#         verbose_name = _('Invoice')
#         verbose_name_plural = _('Invoices')
#         permissions = (
#             ("invoice_view", "Can view Invoice"),
#             ("invoice_all_view", "Can view ALL Invoices"),
#             ("invoice_object_owner", "Can own Invoice"),
#         )


# ----------------------------------------------------------------------------------------
# Bas veren tranzaksiyalar odemeler veya balansdan silinmeler
class TransactionAgentBalance(models.Model):
    # choices

    # Connection fields
    owner = models.ForeignKey(User)

    # Information fields
    amount = models.FloatField(verbose_name=_('Amount'))
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    method = models.CharField(max_length=125)
    description = models.TextField(blank=True, null=True)

    # moderation information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.amount)

    def get_absolute_url(self):
        return reverse('booking:agent-transaction-update', kwargs={'pk': self.pk})

    def __init__(self, *args, **kwargs):
        super(TransactionAgentBalance, self).__init__(*args, **kwargs)
        self.transaction_type_cache = self.transaction_type
        self.amount_cache = self.amount

    class Meta:
        verbose_name = _('Transaction agent')
        verbose_name_plural = _('Transactions agent')
        permissions = (
            ("transactionagentbalance_view", "Can view Transaction Agent Balance"),
            ("transactionagentbalance_all_view", "Can view ALL Transactions Agent Balance"),
            ("transactionagentbalance_object_owner", "Can own Transaction Agent Balance"),
        )


auditlog.register(TransactionAgentBalance)


# -----------------------------------------------------------------------------------
class Transaction(models.Model):
    booking = models.OneToOneField("BookingInformation", verbose_name=_("Booking"), related_name="transaction")
    payment_date = models.DateTimeField(verbose_name=_("Payment date"), blank=True, null=True)
    transit_fee = models.FloatField(default=0, verbose_name=_("Transit fee"))
    transit_percent = models.FloatField(default=0, verbose_name=_("Transit percent"))
    passenger_fee = models.FloatField(default=0, verbose_name=_("Passenger fee"))
    cargo_fee = models.FloatField(default=0, verbose_name=_("Cargo fee"))
    port_fee = models.FloatField(default=0, verbose_name=_("Port fee"))
    price = models.FloatField(verbose_name=_("Price"))
    # paid_price = models.FloatField(default=0, verbose_name=_("Paid price"))
    is_pay = models.BooleanField(default=False, verbose_name=_("Is Pay"))
    description = models.TextField(blank=True, null=True)

    # moderation information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        permissions = (
            ("transaction_view", "Can view Transaction"),
            ("transaction_all_view", "Can view ALL Transactions"),
            ("transaction_object_owner", "Can own Transaction"),
        )

    def __str__(self):
        return str(self.price)


auditlog.register(Transaction)