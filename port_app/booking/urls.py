from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^vessels-schedule/$', VesselScheduleListView.as_view(), name='vessels-schedule-list'),
    url(r'^vessels-schedule/add/$', VesselScheduleCreateView.as_view(), name='vessels-schedule-add'),
    url(r'^vessels-schedule/(?P<pk>[0-9]+)/$', VesselScheduleUpdateView.as_view(), name='vessels-schedule-update'),

    url(r'^bookings-admin/$', BookingAdminListView.as_view(), name='booking-admin-list'),
    url(r'^bookings-admin/(?P<pk>[0-9]+)/$', BookingInformationAdminListView.as_view(), name='booking-admin-update'),
    url(r'^bookings-admin/create/step1/$', BookingAdminCreateStep1.as_view(), name='booking-admin-create-step1'),
    url(r'^bookings-admin/create/step2/$', BookingAdminCreateStep2.as_view(), name='booking-admin-create-step2'),
    url(r'^bookings-admin/create/step3/$', BookingAdminCreateStep3.as_view(), name='booking-admin-create-step3'),

    url(r'^bookings-check-list/$', BookingCheckListView.as_view(), name='booking-check-list'),
    url(r'^bookings-item-list/(?P<pk>[0-9]+)/$', BookingItemsCheck.as_view(), name='booking-items-list'),


    url(r'^agent-balance/$', AgentBalanceListView.as_view(), name='agent-balance-list'),
    # url(r'^agent-balance/(?P<pk>[0-9]+)/$', AgentBalanceUpdate.as_view(), name='agent-balance-update'),

    url(r'^agent-transaction/$', TransactionAgentBalanceList.as_view(), name='agent-transaction-list'),
    url(r'^agent-transaction/add/$', TransactionAgentBalanceCreate.as_view(), name='agent-transaction-add'),
    url(r'^agent-transaction/(?P<pk>[0-9]+)/$', TransactionAgentBalanceUpdate.as_view(),
        name='agent-transaction-update'),


    url(r'^user-booking/$', UserBookingProcess.as_view(), name='user-booking'),
    url(r'^booking-schedule/$', UserBookingShipSelectView.as_view(), name='booking-schedule'),
    url(r'^booking-create/$', BookingCreate.as_view(), name='booking-create'),

    url(r'^user-booking-history/$', UserBookingHistory.as_view(), name='user-booking-history'),
    url(r'^bookings-user/(?P<pk>[0-9]+)/$', BookingInformationUserListView.as_view(), name='booking-user-update'),
    url(r'^user-overview/$', UserOverviewView.as_view(), name='user-overview'),

    url(r'^test/$', TestTemplateView.as_view(), name='test'),
]
