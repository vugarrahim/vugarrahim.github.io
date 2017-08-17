from decimal import Decimal, ROUND_UP
from itertools import chain
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from braces.views import LoginRequiredMixin
from booking.models import *
from accounts.forms import *
from .models import *
from .tools import *
from .tasks.pdf_generate import *
import hashlib
import requests
import json
import xmltodict
# import the logging library
import logging

# Get an instance of a logger
logr = logging.getLogger(__name__)


class PaymentProcess(View):
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    template_name = "booking_payment/payment_page.html"
    merchantName = settings.MERCHANTNAME
    lang = "lv"
    auth_key = settings.AUTH_KEY
    get_payment_key_url = settings.GET_PAYMENT_KEY_URL
    payment_url = settings.PAYMENT_URL
    currency_usd = get_currency()

    def get(self, request, pk):
        args = {}
        args['login_form'] = MyAuthenticationForm(self.request)
        booking = get_object_or_404(Booking, pk=pk)
        transactions = Transaction.objects.filter(booking__booking=booking, is_pay=False)
        booking_amount = transactions.aggregate(Sum('price')).get(
            'price__sum')
        if not booking_amount:
            return redirect(reverse("booking:user-overview"))

        amount = Decimal(booking_amount)
        args['booking'] = booking
        args['transactions'] = transactions
        args['total'] = booking_amount
        args['pay'] = Decimal((Decimal(booking_amount) * Decimal(self.currency_usd)).quantize(Decimal('.01'),
                                                                                              rounding=ROUND_UP))
        return render(request, self.template_name, args)

    def post(self, request, pk):
        card_type = request.POST.get('card_type')
        booking = get_object_or_404(Booking, pk=pk)

        booking_amount = Transaction.objects.filter(booking__booking=booking, is_pay=False).aggregate(Sum('price')).get(
            'price__sum')
        if not booking_amount:
            return redirect(reverse("booking:user-overview"))
        else:
            paid_price = Decimal((Decimal(booking_amount) * Decimal(self.currency_usd)).quantize(Decimal('.01'),
                                                                                                 rounding=ROUND_UP))
            description = "{}".format(booking.pk)
            s = self.auth_key + self.merchantName + card_type + str(int(paid_price * 100)) + description
            hash_code = hashlib.md5(s.encode('utf-8')).hexdigest()

            send_json = {
                "merchantName": self.merchantName,
                "cardType": card_type,
                "hashCode": hash_code,
                "lang": self.lang,
                "amount": str(int(paid_price * 100)),
                "description": description
            }
            response = requests.post(self.get_payment_key_url, data=json.dumps(send_json), headers=self.headers)
            response_data = response.json()
            if response_data['status']['code'] == 1:
                payment_key = response_data['paymentKey']

                # # logr.debug(simplejson.dumps(response.text))
                # payment_key = xmltodict.parse(response.content)['paymentKeyResult']['paymentKey']
                logr.debug(response.json()['status'])
                redirect_url = "{}?payment_key={}".format(self.payment_url, payment_key)
                if requests.get(redirect_url).status_code == 200:
                    payment_info = PaymentInfo(booking=booking, payment_key=payment_key, currency=self.currency_usd,
                                               hash_code=hash_code, get_payment_key=response_data)
                    payment_info.save()
                    return redirect(redirect_url)
                else:
                    return HttpResponse("error")
            else:
                return redirect(reverse("booking:user-overview"))


class PaymentSuccess(View):
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    template_name = "booking_payment/success_page.html"
    get_payment_result_url = settings.GET_PAYMENT_RESULT_URL
    auth_key = settings.AUTH_KEY

    def get(self, request):
        args = {}
        args['login_form'] = MyAuthenticationForm(self.request)
        payment_key = request.GET.get('payment_key')
        payment_info = get_object_or_404(PaymentInfo, payment_key=payment_key)
        # if not payment_info.get_payment_result:
        booking = payment_info.booking

        s = self.auth_key + payment_info.payment_key
        hash_code = hashlib.md5(s.encode('utf-8')).hexdigest()
        params = {
            "hash_code": hash_code,
            "payment_key": payment_key
        }
        logr.debug(params['hash_code'])
        get_payment_result = requests.get(self.get_payment_result_url, params=params, headers=self.headers)
        payment_info.get_payment_result = get_payment_result.json()
        payment_info.save()
        logr.debug(hash_code)
        logr.debug(payment_key)
        logr.debug(get_payment_result.json())
        t = Transaction.objects.filter(booking__booking=booking, is_pay=False).update(
            payment_date=get_payment_result.json()['paymentDate'],
            is_pay=True)
        transactions = Transaction.objects.filter(booking__booking=booking, is_pay=True)
        direction = transactions[0].booking.vessel_schedule.direction
        bookings = booking.bookings.all()
        args['booking'] = booking
        args['payment_detail'] = {
            'total': transactions.aggregate(Sum('price')).get('price__sum'),
            'passenger_fee': transactions.aggregate(Sum('passenger_fee')).get('passenger_fee__sum'),
            'cargo_fee': transactions.aggregate(Sum('cargo_fee')).get('cargo_fee__sum'),
            'port_fee': transactions.aggregate(Sum('port_fee')).get('port_fee__sum'),
        }

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
        args['direction'] = direction
        args['transactions'] = transactions
        ticket_pdf(args, booking.pk)
        # request.session.pop('passenger_count')
        # request.session.pop('schedule_to')
        # request.session.pop('dir_from')
        # request.session.pop('return_date')
        # request.session.pop('departure_date')
        # request.session.pop('type')
        # request.session.pop('cargo_count')
        # request.session.pop('dir_to')
        # request.session.pop('transit')
        # if request.user.is_authenticated():
        #     for session in request.session.keys():
        #         if session != '_auth_user_hash' and session != '_auth_user_backend' and session != '_auth_user_hash':
        #             request.session.pop(session)
        # else:
        #     request.session.clear()
        logr.debug(request.session.keys())

        return render(request, self.template_name, args)
        # else:
        #     return redirect(reverse("booking:user-overview"))

    def post(self):
        pass


class PaymentError(View):
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    template_name = "booking_payment/error_page.html.html"
    get_payment_result_url = settings.GET_PAYMENT_RESULT_URL
    auth_key = settings.AUTH_KEY

    def get(self, request):
        args = {}

        args['login_form'] = MyAuthenticationForm(self.request)
        payment_key = request.GET.get('payment_key')
        args['payment_key'] = payment_key
        payment_info = get_object_or_404(PaymentInfo, payment_key=payment_key)
        if not payment_info.get_payment_result:
            booking = payment_info.booking

            s = self.auth_key + payment_info.payment_key
            hash_code = hashlib.md5(s.encode('utf-8')).hexdigest()
            params = {
                "hash_code": hash_code,
                "payment_key": payment_key
            }
            logr.debug(params['hash_code'])
            get_payment_result = requests.get(self.get_payment_result_url, params=params, headers=self.headers)
            logr.debug(get_payment_result.json())
            payment_info.get_payment_result = get_payment_result.json()
            payment_info.save()
            logr.debug(hash_code)
            logr.debug(payment_key)
            logr.debug(get_payment_result.json())

            return render(request, self.template_name, args)
        else:
            return redirect(reverse("booking:user-overview"))

    def post(self, request):
        pass


# --------------------------------------------------
# Admin views
# --------------------------------------------------
class PaymentProcessAdmin(LoginRequiredMixin, PaymentProcess):
    template_name = "booking_payment/admin_port/payment_page.html"
    login_url = reverse_lazy("accounts:login")

