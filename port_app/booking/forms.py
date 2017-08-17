from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from django.forms.models import inlineformset_factory
from django.utils import timezone
from django.conf import settings
from django import forms
from booking.models import Booking, PassengerTransportType
from booking.utils.processing import BookingProcessor
from .models import VesselsSchedule, BookingInformation, Balance, TransactionAgentBalance, Terminal, Direction, \
    CargoType, BookingCargoItem, BookingPassengerItem, Vessel
from booking.utils.model_choices import PASSENGER_LIMIT, BOOKING_TYPE_CHOICES, CAR_LIMIT_PER_TYPE
# from .models import *
# import the logging library
import logging

# Get an instance of a logger
logr = logging.getLogger(__name__)


class VesselsScheduleForm(forms.ModelForm):
    class Meta:
        model = VesselsSchedule
        fields = ("vessel", "direction", "arrival_date", "departure_date", 'description')


class BookingInformationAdminForm(forms.ModelForm):
    class Meta:
        model = BookingInformation
        fields = ('vessel_schedule', 'done')


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = ('owner', 'amount',)


class TransactionAgentBalanceForm(forms.ModelForm):
    class Meta:
        model = TransactionAgentBalance
        fields = ('owner', 'amount', 'transaction_type', 'method', 'description')


class TransactionAgentBalanceCreateForm(forms.ModelForm):
    owner = forms.CharField(required=True, max_length=50, widget=forms.HiddenInput())

    class Meta:
        model = TransactionAgentBalance
        fields = ('amount', 'transaction_type', 'method', 'description')


class BookingInitialForm(forms.Form):
    """
        Booking form for main page
        - type: one way | round trip
        - dir_from: get value from directions 'from_d' terminals
        - dir_to: get value from directions 'to' terminals
        - departure_date: when have to leave terminal
        - return_date: if booking type round then get what return date should be
    """
    transit = forms.BooleanField(required=False, initial=False, label=_('Transit'))
    type = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=BOOKING_TYPE_CHOICES)
    dir_from = forms.ModelChoiceField(queryset=Terminal.objects.none(), label=_('From'))
    dir_to = forms.ModelChoiceField(queryset=Terminal.objects.none(), label=_('To'))

    departure_date = forms.DateField(initial=timezone.now().date)
    return_date = forms.DateField(required=False)

    passenger_count = forms.ChoiceField(label=_('Passengers'), required=True, choices=PASSENGER_LIMIT)

    def __init__(self, *args, **kwargs):
        """
            Dinamically create cargo type
        """
        super(BookingInitialForm, self).__init__(*args, **kwargs)
        cargo_types = CargoType.objects.all()
        self.cargo_fields = []

        # dynamic filter queryset
        self.fields['dir_from'].queryset = Terminal.objects.filter(
            id__in=[t.from_d.id for t in Direction.objects.all()])
        self.fields['dir_to'].queryset = Terminal.objects.filter(id__in=[t.to.id for t in Direction.objects.all()])

        for type in cargo_types:
            self.fields['cargo_type_{index}'.format(index=type.pk)] = forms.ChoiceField(required=False, label=type.name,
                                                                                        choices=CAR_LIMIT_PER_TYPE)
            self.cargo_fields.append(self.fields['cargo_type_{index}'.format(index=type.pk)])

    def save(self, *args, **kwargs):
        """
            Save form data to session
        """
        cargo_count = []
        request = kwargs.get('request', None)
        cleaned_data = self.cleaned_data

        if request:
            # store all form data to session
            for key, value in cleaned_data.items():

                if 'cargo_type_' in key:  # store overall cargo count
                    cargo_count.append(int(value))

                if isinstance(value, Terminal):
                    request.session[key] = value.id
                else:
                    request.session[key] = str(value)

            request.session['cargo_count'] = sum(cargo_count)

    def clean_departure_date(self):
        '''
            Validate departure date
        '''
        departure_date = self.cleaned_data['departure_date']
        if departure_date < timezone.now().date():
            raise forms.ValidationError(_("The date cannot be in the past."))
        return departure_date

    def clean_return_date(self):
        '''
            Validate return date
        '''
        type = self.cleaned_data.get('type', None)
        return_date = self.cleaned_data.get('return_date', None)
        departure_date = self.cleaned_data.get('departure_date', None)

        if return_date and departure_date and (return_date < departure_date):
            raise forms.ValidationError(_("The date cannot be in the past."))

        if type == '2' and not return_date:
            raise forms.ValidationError(_('This field is required.'))

        return return_date

    def clean(self):
        """
            Validate booking
            - check if from and to destination the same
            - check if passanger and cargo counts greater than 0
        """
        dir_from = self.cleaned_data.get('dir_from', None)
        dir_to = self.cleaned_data.get('dir_to', None)

        if dir_from and dir_to and (dir_from == dir_to):
            raise forms.ValidationError(_('You have to choose different directions for booking'))

        cargo_count = []
        for key, value in self.cleaned_data.items():
            if 'cargo_type_' in key:
                cargo_count.append(int(value))

        if int(self.cleaned_data.get('passenger_count', 0)) <= 0 and sum(cargo_count) <= 0:
            raise forms.ValidationError(_('For booking you must to have a passenger or a cargo.'))

        if sum(cargo_count) > settings.BOOKING_CARGO_LIMIT:
            raise forms.ValidationError(
                _('Maximum number of vehicles: %(value)s'),
                params={'value': settings.BOOKING_CARGO_LIMIT},
            )

        return self.cleaned_data

    def get_temp_cargo_fields(self):
        """
            Display cargo fields in template
        """
        cargo_types = CargoType.objects.all()
        fields = []
        for type in cargo_types:
            fields.append(self['cargo_type_%s' % type.pk])
        return fields


class BookingShipSelectForm(forms.Form):
    """
        Booking ship select form
        - filter queryset based on data from directions and dates which user provided
        - check if schedules vessel can carry cargo or passenger
    """
    schedule = forms.ModelChoiceField(required=True, queryset=VesselsSchedule.objects.all(),
                                      widget=forms.RadioSelect,
                                      empty_label=None)

    def get_departure_date_query(self, queryset, str_date):
        """
            Departure date filter
            - timezne aware datetime object
            - time gap which defined beforehand in settings
        """
        tz_info = timezone.get_default_timezone()

        # datetime objects
        arr_date_from = datetime.strptime(str_date, '%Y-%m-%d').replace(tzinfo=tz_info)
        arr_date_to = arr_date_from + timedelta(days=settings.BOOKING_DATE_RANGE_GAP)

        # update queryset
        queryset['departure_date__gte'] = arr_date_from
        queryset['departure_date__lte'] = arr_date_to

    def __init__(self, *args, **kwargs):
        """
            Dynamically create queryset for schedule field
        """
        queryset = {}

        initial = kwargs.get('initial', None)

        if initial:
            # filter queryset
            direction = initial.pop('filterby_direction', None)
            departure_date = initial.pop('filterby_departure_date', None)
            cargo_availability = initial.pop('filterby_cargo_availability', None)
            passenger_availability = initial.pop('filterby_passenger_availability', None)

            if direction:
                queryset['direction'] = direction

            if departure_date:
                self.get_departure_date_query(queryset, departure_date)

            if cargo_availability:
                queryset['current_cargo_capacity__gte'] = 0
                queryset['vessel__cargo_availability'] = True

            if passenger_availability:
                queryset['current_passenger_count__gte'] = 0
                queryset['vessel__passenger_availability'] = True

        # return filtered queryset
        super(BookingShipSelectForm, self).__init__(*args, **kwargs)
        self.fields['schedule'].queryset = self.fields['schedule'].queryset.filter(**queryset)


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            'owner', 'booking_type', 'transit_type', 'cargo_count', 'passenger_count', 'contact_phone', 'contact_mail',)
        widgets = {
            'owner': forms.HiddenInput(),
            'booking_type': forms.HiddenInput(),
            'transit_type': forms.HiddenInput(),
            'cargo_count': forms.HiddenInput(),
            'passenger_count': forms.HiddenInput()
        }


class BookingCargoItemForm(forms.ModelForm):
    '''
        Form creates booking cargo items
    '''

    def __init__(self, *arg, **kwarg):
        super(BookingCargoItemForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = False

    class Meta:
        model = BookingCargoItem
        fields = ('cargo_type', 'mark', 'plate_no')
        widgets = {'cargo_type': forms.Select(attrs={'class': 'hide select-plain'})}
        # widgets = { 'cargo_type' : forms.Select(attrs={'disabled':'disabled'})}


class BookingPassengerItemCreateForm(forms.ModelForm):
    '''
        Create passanger for form
    '''
    transport_type_return = forms.ModelChoiceField(queryset=PassengerTransportType.objects.all(), required=True,
                                                   empty_label=None, widget=forms.RadioSelect(),
                                                   label=_('Seat for return way'))

    class Meta:
        model = BookingPassengerItem
        fields = ('gender', 'first_name', 'last_name', 'gender', 'passport', 'birth_date', 'passenger_transport_type',
                  'transport_type_return')
        widgets = {'passenger_transport_type': forms.RadioSelect()}
        labels = {"passenger_transport_type": _("Seat for away")}

    def filter_passenger_transport_type(self, query, schedule=None):
        '''
            Filter queryset
        '''
        if schedule:
            capacities = schedule.vessel.capacities.all().only('id')
            query['id__in'] = [i.passenger_transport_type_id for i in capacities]

    def filter_passenger_transport_type_bak(self, query, schedule=None):
        '''
            Filter queryset
        '''
        if schedule:
            capacities = schedule.vessel.capacities.all().only('id')
            query['id__in'] = [i.passenger_transport_type_id for i in capacities]

    def calc_passenger_price(self, schedule=None, type=None):
        '''
            Calculate passenger type price
        '''
        if schedule:
            processor = BookingProcessor(schedule=schedule)

            return processor.calc_passenger_price(type=type)

    def __init__(self, *arg, **kwarg):
        # general stuff
        super(BookingPassengerItemCreateForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = False
        self.fields['passenger_transport_type'].empty_label = None

        initial_data = kwarg.get('initial', None)
        if initial_data:
            # filter
            queryset = {}
            schedule = initial_data.pop('filter_by_schedule', None)
            self.filter_passenger_transport_type(queryset, schedule=schedule)
            self.fields['passenger_transport_type'].queryset = self.fields['passenger_transport_type'].queryset.filter(
                **queryset)
            self.fields['passenger_transport_type'].label_from_instance = lambda obj: "%s (%s usd)" % (
                obj, self.calc_passenger_price(schedule=schedule, type=obj))

            queryset_return = {}
            schedule_return = initial_data.pop('filter_by_schedule_return', None)
            self.filter_passenger_transport_type_bak(queryset_return, schedule=schedule_return)
            self.fields['transport_type_return'].queryset = self.fields['transport_type_return'].queryset.filter(
                **queryset_return)
            self.fields['transport_type_return'].label_from_instance = lambda obj: "%s (%s usd)" % (
                obj, self.calc_passenger_price(schedule=schedule_return, type=obj))

            # remove field
            if 'delete_transport_type_return' in initial_data:
                self.fields.pop('transport_type_return')


# class VSCFilter(forms.Form):
#     direction = forms.ModelChoiceField(queryset=Direction.objects.all(), label=_("Direction"))
#     vessel = forms.ModelChoiceField(queryset=Vessel.objects.all(), label=_("Vessel"))
#     date1 = forms.DateTimeField(required=True)
#     date2 = forms.DateTimeField(required=True)


class CargoItemUpdateForm(forms.ModelForm):
    class Meta:
        model = BookingCargoItem
        exclude = ("created_at", "updated_at", "is_arrived")


class PassengerItemUpdateForm(forms.ModelForm):
    class Meta:
        model = BookingPassengerItem
        exclude = ("created_at", "updated_at", "is_arrived")
