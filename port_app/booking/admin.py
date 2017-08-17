from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *
from django.contrib.admin.models import LogEntry as django_log
from auditlog.models import LogEntry

admin.site.register(LogEntry)
admin.site.register(django_log)
admin.site.register(Booking)


class PortFeesInline(admin.StackedInline):
    model = PortFee
    fields = ('direction', 'price', 'transit_price')
    extra = 1


@admin.register(Port)
class PortsAdmin(TranslationAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ("__str__",)
    fieldsets = [
        (None, {'fields': ['name', 'description', 'created_at', 'updated_at']}),
    ]
    inlines = [PortFeesInline]

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


# ------------------------------------------------------------
@admin.register(Direction)
class DirectionsAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


# -------------------------------------------------------------
@admin.register(PortFee)
class PortFeesAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


# -------------------------------------------------------------
class VesselCargoFeesInline(admin.StackedInline):
    model = VesselCargoFee
    extra = 1


# -------------------------------------------------------------
class VesselPassengerFeesInline(admin.StackedInline):
    model = VesselPassengerFee
    extra = 1


# -------------------------------------------------------------
class VesselPassengerCapacityInline(admin.StackedInline):
    model = VesselPassengerCapacity
    extra = 1


# ------------------------------------------------------------
@admin.register(Vessel)
class VesselsAdmin(TranslationAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ("__str__",)
    fieldsets = [
        (None, {'fields': ['name', 'cargo_availability', 'passenger_availability', 'load_capacity', 'description',
                           'imo', 'mmsi', 'call_sign', 'created_at', 'updated_at']}),

    ]
    inlines = [VesselCargoFeesInline, VesselPassengerFeesInline, VesselPassengerCapacityInline]

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


# --------------------------------------------------------------
@admin.register(VesselsSchedule)
class VesselsScheduleAdmin(admin.ModelAdmin):
    readonly_fields = ('current_passenger_count', 'current_cargo_capacity', 'created_at', 'updated_at', 'schedule_id')
    list_display = ("schedule_id", "vessel", "direction", "arrival_date", "departure_date", )
    fieldsets = [
        (None, {'fields': ['vessel', 'direction', 'arrival_date', 'departure_date', 'schedule_id', 'description',
                           'current_passenger_count', 'current_cargo_capacity', 'created_at', 'updated_at']}),

    ]


@admin.register(CargoType)
class CargoTypeAdmin(TranslationAdmin):
    list_display = ("name", "length", "height")

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(PassengerTransportType)
class PassengerTransportTypeAdmin(TranslationAdmin):
    list_display = ("__str__",)

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class BookingCargoItemInline(admin.StackedInline):
    model = BookingCargoItem
    extra = 1


class BookingPassengerItemInline(admin.StackedInline):
    model = BookingPassengerItem
    extra = 1


# ------------------------------------------------------------
@admin.register(BookingInformation)
class BookingInformationAdmin(admin.ModelAdmin):
    fields = ('booking', 'vessel_schedule', 'type', 'done', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at',)
    list_filter = ('done', 'type')
    inlines = [BookingCargoItemInline, BookingPassengerItemInline]
    # def _owner(self, obj):
    #     if obj.owner.is_user:
    #         return obj.owner.get_full_name()
    #     elif obj.owner.is_company:
    #         return obj.owner.company.name
    #     else:
    #         return obj.owner.email


@admin.register(Terminal)
class TerminalsAdmin(TranslationAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ("__str__",)
    fieldsets = [
        (None, {'fields': ['name', 'port', 'description', 'created_at', 'updated_at']}),
    ]

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(BookingCargoItem)
class BookingCargoItemAdmin(admin.ModelAdmin):
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    list_display = ("__str__",)


@admin.register(BookingPassengerItem)
class BookingPassengerItemAdmin(admin.ModelAdmin):
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    list_display = ("__str__",)

admin.site.register(Balance)
admin.site.register(TransactionAgentBalance)
admin.site.register(Transaction)
