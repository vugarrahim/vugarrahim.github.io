import json
from itertools import chain
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, FormView, UpdateView, TemplateView, View
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.db.models import Q, Sum
from django.forms.models import inlineformset_factory
from braces.views import  LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from accounts.forms import *
from booking.utils.processing import BookingPrice
from booking.utils.tools import get_or_none, trueround, percentage
from port_app.permissions import *
from .utils.permission_tools import *
from .utils.processing import BookingProcessor
from .models import *
from .forms import *

User = get_user_model()


class TestTemplateView(TemplateView):
    template_name = "booking/user_port/booking_completed.html"

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        kwargs['login_form'] = MyAuthenticationForm(self.request)
        return super(TestTemplateView, self).get_context_data(**kwargs)


class VesselScheduleCreateView(LoginRequiredMixin, CreateView, MultiplePermissionsMixin):
    model = VesselsSchedule
    form_class = VesselsScheduleForm
    template_name = "booking/admin_port/vessel_schedule.html"
    success_url = reverse_lazy("booking:vessels-schedule-list")
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.add_vesselsschedule", ),
    }


class VesselScheduleListView(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = VesselsSchedule
    template_name = "booking/admin_port/vessel_schedule_list.html"
    paginate_by = 25
    login_url = reverse_lazy("accounts:login")
    permissions = {
        "all": ("booking.vesselschedule_all_view", ),
    }

    def get_context_data(self, **kwargs):
        context = super(VesselScheduleListView, self).get_context_data(**kwargs)
        context['directions'] = Direction.objects.all()
        context['vessels'] = Vessel.objects.all()
        return context

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        vessel = self.request.GET.get('vessel', None)
        direction = self.request.GET.get('direction', None)
        date1 = self.request.GET.get('date-1', None)
        date2 = self.request.GET.get('date-2', None)
        if date1:
            gted = parse_datetime(date1)
        else:
            gted = None
        if date2:
            lted = parse_datetime(date2)
        else:
            lted = None

        if direction and vessel and gted and lted:
            filter = {"vessel": int(vessel), "direction": int(direction),
                      "departure_date__gte": gted, "departure_date__lte": lted
                      }
            queryset = self.model.objects.filter(**filter)
            return queryset
        elif direction:
            filter = {"direction": int(direction)}
            queryset = self.model.objects.filter(**filter)
            return queryset
        elif vessel:
            filter = {"vessel": int(vessel)}
            queryset = self.model.objects.filter(**filter)
            return queryset
        elif gted:
            filter = {"departure_date__gte": gted}
            queryset = self.model.objects.filter(**filter)
            return queryset
        elif lted:
            filter = {"departure_date__lte": lted}
            queryset = self.model.objects.filter(**filter)
            return queryset

        if q:
            query = Q(vessel__name__icontains=q) | Q(direction__from_d__name__icontains=q) | \
                    Q(direction__to__name__icontains=q) | Q(shedule_id__icontains=q)
            queryset = self.model.objects.filter(query)
            return queryset
        else:
            return super(VesselScheduleListView, self).get_queryset()


class VesselScheduleUpdateView(LoginRequiredMixin, UpdateView, MultiplePermissionsMixin):
    model = VesselsSchedule
    form_class = VesselsScheduleForm
    template_name = "booking/admin_port/vessel_schedule.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.change_vesselsschedule", ),
    }


class BookingAdminListView(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = Booking
    template_name = "booking/admin_port/booking_list.html"
    paginate_by = 25
    login_url = reverse_lazy("accounts:login")
    permissions = {
        "any": ("booking.booking_all_view", "booking.booking_view"),
    }

    def get_queryset(self):
        queryset = permission_model_query(self.request.user, self.model)
        q = self.request.GET.get('q', None)
        if q:
            query = Q(booking_id__icontains=q)
            queryset = queryset.filter(query)
            return queryset
        else:
            return queryset


class BookingInformationAdminListView(LoginRequiredMixin, MultiplePermissionsMixin):
    model = BookingInformation
    template_name = "booking/admin_port/booking.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.bookinginformation_all_view",),
    }

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        bookings = BookingInformation.objects.filter(booking=booking)
        args = {
            'bookings': bookings
        }
        return render(request, self.template_name, args)


class AgentBalanceListView(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = Balance
    template_name = "booking/admin_port/agent_balance_list.html"
    paginate_by = 25
    login_url = reverse_lazy("accounts:login")
    permission_required = ('booking.balance_all_view', 'booking.balance_view')
    permissions = {
        "any": ("booking.balance_all_view", "booking.balance_view"),
    }

    def get_queryset(self):
        queryset = permission_model_query(self.request.user, self.model)
        q = self.request.GET.get('q', None)
        if q:
            query = Q(owner__first_name__icontains=q) | Q(owner__last_name__icontains=q) | \
                    Q(owner__agent__name__icontains=q) | Q(owner__email__icontains=q)
            queryset = queryset.filter(query)
            return queryset
        else:
            return queryset


class AgentBalanceUpdate(LoginRequiredMixin, UpdateView, MultiplePermissionsMixin):
    model = Balance
    form_class = BalanceForm
    login_url = reverse_lazy("accounts:login")
    template_name = "booking/admin_port/agent_balance.html"

    permissions = {
        "all": ("booking.change_balance", ),
    }


class TransactionAgentBalanceCreate(LoginRequiredMixin, CreateView, MultiplePermissionsMixin):
    model = TransactionAgentBalance
    form_class = TransactionAgentBalanceCreateForm
    template_name = "booking/admin_port/agent_transaction_balance_create.html"
    success_url = reverse_lazy("booking:agent-transaction-list")
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.add_transactionagentbalance", ),
    }

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        q = request.GET.get('q', None)
        queryset = []
        if q:
            if q.isdigit():
                query = Q(email__icontains=q) | Q(first_name__icontains=q) \
                        | Q(first_name__icontains=q) | Q(pk=q) & Q(groups__name='agent')
                queryset = User.objects.filter(query)
            else:
                query = Q(email__icontains=q) | Q(first_name__icontains=q) \
                        | Q(first_name__icontains=q) & Q(groups__name='agent')
                queryset = User.objects.filter(query)
        else:
            queryset = User.objects.filter(groups__name='agent')

        return self.render_to_response(
            self.get_context_data(form=form,
                                  users=queryset, ))

    def form_valid(self, form, ):
        user = User.objects.filter(pk=int(form.cleaned_data['owner']))
        if user:
            form.instance.owner = user[0]
            return super(TransactionAgentBalanceCreate, self).form_valid(form)
        else:
            return super(TransactionAgentBalanceCreate, self).form_valid(form)


class TransactionAgentBalanceList(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = TransactionAgentBalance
    template_name = "booking/admin_port/agent_transaction_balance_list.html"
    paginate_by = 25
    login_url = reverse_lazy("accounts:login")
    permissions = {
        "any": ("booking.transactionagentbalance_all_view", "booking.transactionagentbalance_view"),
    }

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        queryset = permission_model_query(self.request.user, self.model)
        if q:
            query = Q(owner__first_name__icontains=q) | Q(owner__last_name__icontains=q) | \
                    Q(owner__agent__name__icontains=q) | Q(owner__email__icontains=q)
            queryset = queryset.filter(query)
            return queryset
        else:
            return queryset


class TransactionAgentBalanceUpdate(LoginRequiredMixin, UpdateView, MultiplePermissionsMixin):
    model = TransactionAgentBalance
    form_class = TransactionAgentBalanceForm
    template_name = "booking/admin_port/agent_transaction_balance.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.change_transactionagentbalance", ),
    }


class BookingCheckListView(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = Booking
    template_name = "booking/admin_port/booking_check_in.html"
    paginate_by = 25
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.bookingcheckin_view", ),
    }

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        if q:
            query = Q(booking_id__icontains=q)
            queryset = self.model.objects.filter(query)
            return queryset
        else:
            return super(BookingCheckListView, self).get_queryset()


class BookingItemsCheck(LoginRequiredMixin, MultiplePermissionsMixin):
    template_name = 'booking/admin_port/booking_check_items.html'
    login_url = reverse_lazy("accounts:login")
    permissions = {
        "all": ("booking.bookingcheckin_view", ),
    }

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BookingItemsCheck, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        args = {}
        booking = get_object_or_404(Booking, pk=pk)
        args['booking'] = booking
        bookings = booking.bookings.all()
        l = []
        d = {}

        for booking in bookings:
            items = chain(booking.cargoes.all(), booking.passengers.all())
            d['booking'] = booking
            d['items'] = items
            l.append(d)
            d = {}
        logr.debug(l[0]['booking'])
        args['bookings'] = l
        logr.debug(args)

        return render(request, self.template_name, args)

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)

        if request.is_ajax():
            json_str = request.body.decode(encoding='UTF-8')
            data = json.loads(json_str)
            # logr.debug(data)
            for item in data['items']:
                if item['class_name'] == 'cargo':
                    cargo = get_object_or_404(BookingCargoItem, ticket_id=item['ticket_id'])
                    if cargo.booking.booking == booking:
                        cargo.is_arrived = item['is_arrived']
                    else:
                        return HttpResponse(status=403)
                    cargo.save()
                elif item['class_name'] == 'passenger':
                    passenger = get_object_or_404(BookingPassengerItem, ticket_id=item['ticket_id'])
                    if passenger.booking.booking == booking:
                        passenger.is_arrived = item['is_arrived']
                    else:
                        return HttpResponse(status=403)
                    passenger.save()
            return HttpResponse(status=200)
        return HttpResponse(status=400)


class UserBookingHistory(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = Booking
    template_name = "booking/user_port/user_booking_history.html"
    login_url = reverse_lazy("accounts:user-login")
    paginate_by = 25
    permissions = {
        "all": ("booking.booking_view", ),
    }

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


class BookingInformationUserListView(BookingInformationAdminListView):
    template_name = "booking/user_port/booking.html"
    login_url = reverse_lazy("accounts:user-login")

    permissions = {
        "all": ("booking.bookinginformation_view",),
    }


class UserOverviewView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("accounts:user-login")
    template_name = "booking/user_port/overview.html"

    def get_context_data(self, **kwargs):
        context = super(UserOverviewView, self).get_context_data(**kwargs)
        context['booked'] = Booking.objects.filter(owner=self.request.user).count()
        context['payed'] = Transaction.objects.filter(booking__booking__owner=self.request.user).aggregate(
            Sum('price')).get(
            'price__sum')
        return context


# -------------------------------------------------------
# Booking views | Users
# -------------------------------------------------------
class UserBookingProcess(TemplateView):
    '''
        First step of booking process
        - initial infos about booking: date, type, cargo types, passenger numbers, etc.
    '''
    template_name = 'booking/user_port/booking_step_one.html'
    success_url = reverse_lazy('booking:booking-schedule')


    def get_context_data(self, **kwargs):
        """
        Get the context data for the first step of booking process.
        """
        kwargs['login_form'] = MyAuthenticationForm(self.request)
        kwargs['booking_form'] = BookingInitialForm(initial={'type': '2'})

        return super(UserBookingProcess, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        '''
            Handle first step of booking attempt
        '''
        form = BookingInitialForm(request.POST)
        if form.is_valid():
            # save form data to user session
            form.save(request=request)
        else:
            context = self.get_context_data()
            context['booking_form'] = form

            return self.render_to_response(context)

        return redirect(self.success_url)


class UserBookingShipSelectView(TemplateView):
    """
        Second step of the booking process
        - define the booking schedule
    """
    template_name = 'booking/user_port/booking_select_ship.html'
    success_url = reverse_lazy("booking:booking-create")


    def get_ship_form(self, *args, **kwargs):
        """
            Create form based on params which stored in session
            - filter by directions from session
            - filter by arrival date from session
            - filter by departure date from session
        """
        # session data
        session = self.get_session_data()
        booking_type = session['booking_type']
        booking_from = session['booking_from']
        booking_to = session['booking_to']
        booking_departure = session['booking_departure']
        booking_return = session['booking_return']
        passenger_count = int(session['passenger_count'])
        cargo_count = int(session['cargo_count'])

        # create forms
        form_count = 1 if booking_type == '1' else 2
        BookingShipFormSet = formset_factory(BookingShipSelectForm, extra=form_count, max_num=form_count)

        # if booking for one way
        initial_data = [{}]
        if cargo_count:
            initial_data[0]['filterby_cargo_availability'] = cargo_count
        if passenger_count:
            initial_data[0]['filterby_passenger_availability'] = passenger_count

        if booking_from and booking_to:  # filter by direction
            direction = Direction.objects.filter(from_d=booking_from, to=booking_to).last()
            initial_data[0]['filterby_direction'] = direction

        if booking_departure:  # filter by departure date
            initial_data[0]['filterby_departure_date'] = booking_departure

        # if booking w/ round trip
        if booking_type == '2':
            initial_data.append({})
            if cargo_count:
                initial_data[1]['filterby_cargo_availability'] = cargo_count
            if passenger_count:
                initial_data[1]['filterby_passenger_availability'] = passenger_count

            if booking_from and booking_to:  # filter by direction
                direction_back = Direction.objects.filter(from_d=booking_to, to=booking_from).last()
                initial_data[1]['filterby_direction'] = direction_back

            if booking_return:  # filter by departure date
                initial_data[1]['filterby_departure_date'] = booking_return

        kwargs['initial'] = initial_data
        return BookingShipFormSet(*args, **kwargs)

    def get_form_detail_info(self, formset, **kwargs):
        '''
            Get detailed infor for each form in formset:
            - direction object
            - date object
            - schedule object
        '''
        from django.utils.timezone import get_current_timezone
        from datetime import datetime

        tz = get_current_timezone()

        formset_info = {}
        session = self.get_session_data()
        booking_type = session['booking_type']
        booking_from = session['booking_from']
        booking_to = session['booking_to']
        booking_departure = session['booking_departure']
        booking_return = session['booking_return']

        formset_info['direction_to'] = Direction.objects.filter(from_d=booking_from, to=booking_to).last()
        formset_info['booking_departure'] = tz.localize(datetime.strptime(booking_departure, '%Y-%m-%d'))

        if booking_type == '2':
            formset_info['booking_return'] = tz.localize(datetime.strptime(booking_return, '%Y-%m-%d'))

        formset_info['prices'] = self.get_form_price(formset)

        return formset_info

    def get_form_price(self, formset):
        """
            Get price per schedule
        """
        session = self.request.session
        # cargo_types = CargoType.objects.all()
        types = []
        prices = []
        for key, val in session.items():
            if 'cargo_type_' in key:
                types.append({
                    'type_pk': key.replace("cargo_type_", ""),
                    'count': val
                })

        for form in formset:
            form_price = []
            for schedule in form.fields['schedule'].queryset:
                process = BookingProcessor(schedule=schedule)

                # calculations
                schedule_cargo_price = process.calc_cargo_prices(cargo_types=types)
                schedule_traveler_price = process.est_passenger_price(count=int(session['passenger_count']))
                schedule_port_price = process.calc_port_fee(cargo_types=types, port=schedule.direction.from_d.port)

                form_price.append({
                    'cargo': schedule_cargo_price,
                    'passenger': schedule_traveler_price,
                    'port': schedule_port_price,
                })

            prices.append(form_price)

        return prices

    def get_session_data(self, *args, **kwargs):
        """
            Get necessary infos from session
        """
        logr.debug(self.request.session.items())
        return {
            'booking_type': self.request.session.get('type', None),
            'booking_from': self.request.session.get('dir_from', None),
            'booking_to': self.request.session.get('dir_to', None),
            'booking_departure': self.request.session.get('departure_date', None),
            'booking_return': self.request.session.get('return_date', None),
            'passenger_count': self.request.session.get('passenger_count', '0'),
            'cargo_count': self.request.session.get('cargo_count', '0')
        }

    def clear_schedule_session(self, request):
        schedule_to = request.session.get('schedule_to', None)
        schedule_bak = request.session.get('schedule_bak', None)

        if schedule_to:
            del request.session['schedule_to']

        if schedule_bak:
            del request.session['schedule_bak']

    def get_context_data(self, **kwargs):
        """
            Get the context data for the second step of the booking process:
            - show the login form if user not authenticated
            - show the vessels and the prices w/ given data on the first step
        """
        formset = self.get_ship_form()
        formset_info = self.get_form_detail_info(formset)

        # update kwargs
        kwargs['login_form'] = MyAuthenticationForm(self.request)
        kwargs['formset'] = formset
        kwargs['info'] = formset_info

        return super(UserBookingShipSelectView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        '''
            Handle Post request
        '''
        self.clear_schedule_session(request)
        formset = self.get_ship_form(request.POST)
        if formset.is_valid():
            for index, form in enumerate(formset):
                data = form.cleaned_data
                if index == 0:
                    request.session['schedule_to'] = str(data['schedule'].id)
                elif index == 1:
                    request.session['schedule_bak'] = str(data['schedule'].id)
        else:
            context = self.get_context_data(**kwargs)
            context['formset'] = formset
            return self.render_to_response(context)

        logr.debug(request.session.items())
        return redirect(self.success_url)


class BookingCreate(CreateView):
    '''
        Third/Final step of the booking
        - validate all the data collected through the entire process
        - calculate the overall price for the booking
        - save booking and relational data
    '''
    template_name = 'booking/user_port/booking_items_create.html'
    model = None
    form_class = BookingCreateForm

    # success_url = reverse_lazy("payment:payment-process")

    # ------------------------------------
    # built-in methods
    # ------------------------------------

    def get_success_url(self):
        return reverse("payment:payment-process", args=(self.object.id,))

    def get_initial(self):
        '''
            Get initial for the self.form_class
        '''
        initial = {}

        # if user authenticated
        if self.request.user.is_authenticated():
            initial['owner'] = self.request.user
            initial['contact_phone'] = self.request.user.telephone
            initial['contact_mail'] = self.request.user.email

        # vessel count
        cargo_count = self.request.session.get('cargo_count', None)
        if cargo_count:
            initial['cargo_count'] = cargo_count

        # passenger count
        passenger_count = self.request.session.get('passenger_count', None)
        if passenger_count:
            initial['passenger_count'] = passenger_count

        # booking type
        type = self.request.session.get('type', None)
        if type:
            initial['booking_type'] = type

        # booking type
        if 'transit' in self.request.session:
            initial['transit_type'] = TRANSIT_TYPE_CHOICES[0][0] if self.request.session['transit'] == 'True' else \
            TRANSIT_TYPE_CHOICES[1][0]

        return initial

    def get_context_data(self, **kwargs):
        '''
            Additional context data for the view
        '''
        kwargs['login_form'] = MyAuthenticationForm(self.request)
        passenger_count = self.request.session.get('passenger_count', '0')

        # passenger formsets
        if passenger_count:
            kwargs['passenger_formset'] = self.get_passenger_formset()
            kwargs['passenger_acount'] = int(passenger_count)

        # cargo formsets
        kwargs['cargo_formset'] = self.get_cargo_formset()
        kwargs['cargo_count'] = int(self.request.session.get('cargo_count', '0'))
        kwargs['cargo_prices'] = self.get_cargo_prices()

        # schedule informations
        schedules = self.get_schedules()
        kwargs['schedule_to'] = schedules[0]
        if len(schedules) > 1:
            kwargs['schedule_bak'] = schedules[1]

        # price
        kwargs['price'] = self.get_initial_prices()

        return super(BookingCreate, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None
        if request.is_ajax():
            return self.ajax_get(request)

        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        '''
            Handle forms submits
        '''
        self.object = None

        # forms
        form = self.get_form()
        passenger_formset = self.get_passenger_formset(request.POST)
        cargo_formset = self.get_cargo_formset(request.POST)

        if form.is_valid() and passenger_formset.is_valid() and cargo_formset.is_valid():
            if not self.is_availabile(passenger_formset, cargo_formset):
                return HttpResponseRedirect(reverse("home"))
            return self.form_valid(form, passenger_formset, cargo_formset)
        else:
            return self.form_invalid(form, passenger_formset, cargo_formset)

    def form_valid(self, form, passenger_formset, cargo_formset):
        '''
            If all of the submited forms are valid
        '''
        # parent booking
        self.object = form.save()

        # create booking information for away voyage
        schedules = self.get_schedules()
        away_booking = BookingInformation(booking=self.object, vessel_schedule=schedules[0], type='1')
        away_booking.save()

        # passengers for away voyage
        passenger_formset.instance = away_booking
        passenger_formset.save()

        # cargos for away voyage
        cargo_formset.instance = away_booking
        cargo_formset.save()

        # save return way
        if len(schedules) > 1:
            self.save_back_way(booking=self.object, passenger_formset=passenger_formset, cargo_formset=cargo_formset,
                               schedule=schedules[1])

        # transactions
        self.create_transactions(booking=self.object)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, passenger_formset, cargo_formset):
        '''
            If any of submited forms invalid
        '''
        logr.debug(form.errors)
        logr.debug(passenger_formset.errors)
        logr.debug(cargo_formset.errors)
        context = self.get_context_data()
        context['form'] = form
        context['passenger_formset'] = passenger_formset
        context['cargo_formset'] = cargo_formset
        return self.render_to_response(context)

    # ------------------------------------
    # helper methods
    # ------------------------------------

    def is_availabile(self, passenger_formset, cargo_formset):
        '''
            Checks if desired booking types and formats avaible
        '''
        schedules = self.get_schedules()
        availability = []
        # away
        process_away = BookingProcessor(schedule=schedules[0])
        availability.append(process_away.is_availabile(passenger_formset, cargo_formset, type='away'))

        # back
        if len(schedules) > 1:
            process_back = BookingProcessor(schedule=schedules[1])
            availability.append(process_back.is_availabile(passenger_formset, cargo_formset, type='back'))

        return all(availability)

    def calc_booking_price(self, request=None):
        '''
            Calculate
        '''
        if request.method == 'GET':
            response = {'passenger': {}}
            schedules = self.get_schedules()

            # ------------------------------------------
            # passenger nums
            # ------------------------------------------
            passenger_nums = int(request.GET.get('passengers-MAX_NUM_FORMS', 0))
            passenger_away_type_ids = {}
            passenger_back_type_ids = {}
            process_away = BookingProcessor(schedule=schedules[0])
            for num in range(passenger_nums):
                away_type = request.GET.get('passengers-{0}-passenger_transport_type'.format(num), None)
                back_type = request.GET.get('passengers-{0}-transport_type_return'.format(num), None)
                if away_type:
                    type_id = "pk_{0}".format(away_type)
                    if type_id in passenger_away_type_ids:
                        passenger_away_type_ids[type_id]['count'] += 1
                    else:
                        passenger_away_type_ids[type_id] = {
                            'pk': away_type,
                            'count': 1
                        }
                if back_type:
                    type_back_id = "pk_{0}".format(back_type)
                    if type_back_id in passenger_back_type_ids:
                        passenger_back_type_ids[type_back_id]['count'] += 1
                    else:
                        passenger_back_type_ids[type_back_id] = {
                            'pk': back_type,
                            'count': 1
                        }

            passenger_away_prices = sum([process_away.calc_passenger_price(type=v['pk']) * v['count'] for k, v in
                                         passenger_away_type_ids.items()])
            response['passenger']['away'] = passenger_away_prices

            if len(schedules) > 1:
                process_back = BookingProcessor(schedule=schedules[1])
                passenger_back_prices = sum([process_back.calc_passenger_price(type=v['pk']) * v['count'] for k, v in
                                             passenger_back_type_ids.items()])
                response['passenger']['back'] = passenger_back_prices

            # ------------------------------------------
            # cargo prices & port fee
            # - inherited from initial prices
            # ------------------------------------------
            initial_prices = self.get_initial_prices()
            response['cargo'] = initial_prices['cargo']
            response['portfee'] = initial_prices['portfee']

            # ------------------------------------------
            # cargo + passenger + portfee
            # ------------------------------------------
            total_away = sum([v['away'] for k, v in response.items() if ('away' in v)])
            total_back = sum([v['back'] for k, v in response.items() if ('back' in v)])

            # ------------------------------------------
            # transit price
            # ------------------------------------------

            if 'transit_fee' in initial_prices:
                transit_persentages = initial_prices['transit_fee']
                transit_away = trueround(percentage(transit_persentages['away'], total_away), 2)
                transit_back = trueround(percentage(transit_persentages['back'], total_back),
                                         2) if 'back' in transit_persentages else 0
                response['transit_fee'] = {'away': transit_away, 'back': transit_back,
                                           'total': trueround(transit_away + transit_back, 2)}

            # ------------------------------------------
            # grand total
            # ------------------------------------------
            grand_total_away = sum([v['away'] for k, v in response.items() if ('away' in v)])
            grand_total_back = sum([v['back'] for k, v in response.items() if ('back' in v)])
            response['total'] = {'away': grand_total_away, 'back': grand_total_back}
            response['grand_total'] = trueround(grand_total_away + grand_total_back, 2)

            logr.debug(request.GET)

            return response

        return None

    def ajax_get(self, request):
        response = {}
        schedules = self.get_schedules()
        passenger_spots = {}

        process_to = BookingProcessor(schedule=schedules[0])
        passenger_spots['away'] = process_to.check_passanger_availability()

        if len(schedules) > 1:
            process_bak = BookingProcessor(schedule=schedules[1])
            passenger_spots['return'] = process_bak.check_passanger_availability()

        response['passenger_spots'] = passenger_spots

        # calculate prices
        prices = self.calc_booking_price(request=request)
        if prices:
            response['prices'] = prices

        return JsonResponse(response)

    def get_initial_prices(self):
        '''
            Calculate initial prices
        '''
        total = {}
        types = []
        session = self.request.session
        for key, val in session.items():
            if 'cargo_type_' in key:
                types.append({
                    'type_pk': key.replace("cargo_type_", ""),
                    'count': val
                })

        schedules = self.get_schedules()
        cargo_prices = self.get_cargo_prices()
        cargo_away = sum([price['price_to'] for price in cargo_prices if ('price_to' in price)])
        cargo_back = sum([price['price_bak'] for price in cargo_prices if ('price_bak' in price)])
        total['cargo'] = {'away': cargo_away, 'back': cargo_back}

        # passenger est
        process_away = BookingProcessor(schedule=schedules[0])
        passenger_away = process_away.est_passenger_price(count=int(self.request.session.get('passenger_count', 0)))
        total['passenger'] = {'away': passenger_away, }

        # port fee
        portfee_away = process_away.calc_port_fee(cargo_types=types)
        total['portfee'] = {'away': portfee_away, }

        # transit
        if 'transit' in session:
            transit = session['transit'] == 'False'
            if transit:
                total['transit_fee'] = {'away': process_away.get_transit_percentage(), }

        if len(schedules) > 1:
            process_back = BookingProcessor(schedule=schedules[1])
            passenger_back = process_back.est_passenger_price(count=int(self.request.session.get('passenger_count', 1)))
            total['passenger']['back'] = passenger_back

            # port fee
            portfee_back = process_back.calc_port_fee(cargo_types=types)
            total['portfee']['back'] = portfee_back

            # transit
            if 'transit' in session and (session['transit'] == 'False'):
                total['transit_fee']['back'] = process_back.get_transit_percentage()

        logr.debug(total)

        return total

    def get_schedules(self):
        '''
            Get schedules
        '''
        result = []
        session = self.request.session

        if 'schedule_to' in session:
            result.append(get_or_none(VesselsSchedule, pk=session['schedule_to']))

        if 'schedule_bak' in session:
            result.append(get_or_none(VesselsSchedule, pk=session['schedule_bak']))

        return result

    def get_passenger_formset(self, *args, **kwargs):
        '''
            Complex passenger form
        '''
        passenger_count = int(self.request.session.get('passenger_count', '0'))
        PassengerFormSet = inlineformset_factory(BookingInformation, BookingPassengerItem,
                                                 form=BookingPassengerItemCreateForm, can_delete=False,
                                                 extra=passenger_count, max_num=passenger_count)

        # filter the passenger type
        initial_data = []
        schedules = self.get_schedules()
        # logr.debug(schedules)
        for form in range(passenger_count):
            initial = {
                'filter_by_schedule': schedules[0]
            }
            if len(schedules) < 2:
                initial['delete_transport_type_return'] = True
            else:
                initial['filter_by_schedule_return'] = schedules[1]

            initial_data.append(initial)

        kwargs['initial'] = initial_data
        return PassengerFormSet(*args, **kwargs)

    def get_cargo_formset(self, *args, **kwargs):
        '''
            Cargo formset for the dynamic use
        '''
        cargo_types = CargoType.objects.all()
        cargo_count = self.request.session.get('cargo_count', 0)
        initial_data = []

        # collect initial data
        for type in cargo_types:
            type_count = int(self.request.session.get('cargo_type_%s' % type.pk, 0))
            for i in range(type_count):
                initial_data.append({'cargo_type': type})

        kwargs['initial'] = initial_data

        CargoFormset = inlineformset_factory(BookingInformation, BookingCargoItem,
                                             form=BookingCargoItemForm, can_delete=False,
                                             extra=cargo_count, max_num=cargo_count)

        return CargoFormset(*args, **kwargs)

    def get_cargo_prices(self):
        '''
            Calculate prices
        '''
        booking_type = self.request.session.get('type', None)
        cargo_types = CargoType.objects.all()
        prices = []

        # schedule informations
        schedule_to_ses = self.request.session.get('schedule_to', None)
        if schedule_to_ses:
            schedule_to = get_or_none(VesselsSchedule, pk=schedule_to_ses)

        # one way price
        processor_to = BookingProcessor(schedule=schedule_to)

        if booking_type == '2':  # if with return
            schedule_bak_ses = self.request.session.get('schedule_bak', None)
            if schedule_bak_ses:
                schedule_bak = get_or_none(VesselsSchedule, pk=schedule_bak_ses)
                processor_bak = BookingProcessor(schedule=schedule_bak)

        for type in cargo_types:
            type_count = int(self.request.session.get('cargo_type_%s' % type.pk))
            for i in range(type_count):
                single = {
                    'type_pk': type.pk,
                    'price_to': processor_to.pricing_cargo_type(type.pk)
                }
                if booking_type == '2':
                    single['price_bak'] = processor_bak.pricing_cargo_type(type.pk)
                prices.append(single)

        return prices

    def save_back_way(self, booking=None, passenger_formset=None, cargo_formset=None, schedule=None):
        '''
            Handles round trip type boooking saving
        '''
        # booking info
        booking_info = BookingInformation(booking=booking, vessel_schedule=schedule, type='2')
        booking_info.save()

        # save passengers
        for form in passenger_formset:
            passenger = BookingPassengerItem(booking=booking_info,
                                             first_name=form.cleaned_data['first_name'],
                                             last_name=form.cleaned_data['last_name'],
                                             gender=form.cleaned_data['gender'],
                                             passport=form.cleaned_data['passport'],
                                             birth_date=form.cleaned_data['birth_date'],
                                             passenger_transport_type=form.cleaned_data['transport_type_return'])
            passenger.save()

        # save cargos
        for form in cargo_formset:
            cargo = BookingCargoItem(booking=booking_info,
                                     cargo_type=form.cleaned_data['cargo_type'],
                                     mark=form.cleaned_data['mark'],
                                     plate_no=form.cleaned_data['plate_no'])
            cargo.save()

    def create_transactions(self, booking=None):
        '''
            Create transactions
        '''
        if booking:
            calc = BookingPrice(booking=booking)
            result = calc.result()
            for book_info in booking.bookings.all():
                # away
                if book_info.type == BOOKINGINFO_TYPE_CHOICES[0][0]:
                    payinfo_away = {'booking': book_info}
                    if 'non-transit' in result and result['non-transit']:
                        payinfo_away['transit_fee'] = result['non-transit']['away']['value']
                        payinfo_away['transit_percent'] = result['non-transit']['away']['percentage']

                    payinfo_away['passenger_fee'] = result['passengers']['away']
                    payinfo_away['cargo_fee'] = result['cargos']['away']
                    payinfo_away['port_fee'] = result['portfee']['away']
                    payinfo_away['price'] = result['total']['away']

                    transaction_away = Transaction(**payinfo_away)
                    transaction_away.save()

                # back
                elif book_info.type == BOOKINGINFO_TYPE_CHOICES[1][0]:
                    payinfo_back = {'booking': book_info}
                    if 'non-transit' in result and result['non-transit']:
                        payinfo_back['transit_fee'] = result['non-transit']['back']['value']
                        payinfo_back['transit_percent'] = result['non-transit']['back']['percentage']

                    payinfo_back['passenger_fee'] = result['passengers']['back']
                    payinfo_back['cargo_fee'] = result['cargos']['back']
                    payinfo_back['port_fee'] = result['portfee']['back']
                    payinfo_back['price'] = result['total']['back']

                    transaction_back = Transaction(**payinfo_back)
                    transaction_back.save()


# ------------------------------------------------------
# Booking admin views
# ------------------------------------------------------
class BookingAdminCreateStep1(LoginRequiredMixin, UserBookingProcess, MultiplePermissionsMixin):
    '''
        Admin view
    '''
    template_name = 'booking/admin_port/booking_step_one.html'
    login_url = reverse_lazy("accounts:login")
    success_url = reverse_lazy('booking:booking-admin-create-step2')

    permissions = {
        "all": ("booking.bookinginformation_super_create", ),
    }


class BookingAdminCreateStep2(LoginRequiredMixin, UserBookingShipSelectView, MultiplePermissionsMixin):
    '''
        Admin view
    '''
    template_name = 'booking/admin_port/booking_step_two.html'
    login_url = reverse_lazy("accounts:login")
    success_url = reverse_lazy('booking:booking-admin-create-step3')

    permissions = {
        "all": ("booking.bookinginformation_super_create", ),
    }


class BookingAdminCreateStep3(LoginRequiredMixin, BookingCreate, MultiplePermissionsMixin):
    '''
        Admin view
    '''
    template_name = 'booking/admin_port/booking_step_three.html'
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("booking.bookinginformation_super_create", ),
    }

    def get_success_url(self):
        return reverse("booking:booking-admin-list")
        # success_url = reverse_lazy('booking:booking-admin-create-step3')
