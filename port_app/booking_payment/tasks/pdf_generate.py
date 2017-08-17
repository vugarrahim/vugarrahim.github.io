from weasyprint import *
from django.template import Context
from django.template.loader import get_template
from django.template import *
from django.conf import settings
from django.core.files import File
from booking.models import *

MEDIA_ROOT = settings.MEDIA_ROOT


def ticket_pdf(args, id):
    b = Booking.objects.get(pk=id)
    ticket_html = get_template("booking_payment/partials/ticket.html")
    context = Context(args)
    render_ticket_html = ticket_html.render(context)
    pdf_path = MEDIA_ROOT + "/temp_pdf/{}_ticket.pdf".format(b.booking_id)

    HTML(string=render_ticket_html).write_pdf(pdf_path)

    ticket_pdf_file = open(pdf_path, 'rb')
    ticket_pdf_file_dj = File(ticket_pdf_file)
    b.ticket_pdf = ticket_pdf_file_dj
    b.save()

    return "ok"



