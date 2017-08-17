from port_app.celery import app
from itertools import *
from .models import BookingInformation, Booking


# Gonderilen booking_id uygun booking tapiram ve hemin booking-in  vehicleitems ve passengeritems
# booking_items-da  birlesdirem ve yoxlayiram butun itemlar done-dursa booking-de done edirem.
@app.task(bind=True)
def booking_information_done(self, booking_id):
    booking = BookingInformation.objects.get(id=booking_id)
    booking_items = chain(booking.cargoes.all(), booking.passengers.all())
    done_list = [i.is_arrived for i in booking_items]
    if all(done_list):
        booking.done = True
        booking.save()
    else:
        if booking.done:
            booking.done = False
            booking.save()


@app.task(bind=True)
def booking_done(self, booking_id):
    booking = Booking.objects.get(id=booking_id)
    done_list = [i.done for i in booking.bookings.all()]
    if all(done_list):
        booking.done = True
        booking.save()
    else:
        if booking.done:
            booking.done = False
            booking.save()