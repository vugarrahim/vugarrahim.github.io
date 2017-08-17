from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^payment/(?P<pk>[0-9]+)/$', PaymentProcess.as_view(), name='payment-process'),
    url(r'^payment-admin/(?P<pk>[0-9]+)/$', PaymentProcessAdmin.as_view(), name='payment-process-admin'),
    url(r'^success/$', PaymentSuccess.as_view(), name='payment-success'),
    url(r'^error/$', PaymentError.as_view(), name='payment-error'),
]
