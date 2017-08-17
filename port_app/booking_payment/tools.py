import datetime
import requests
import xmltodict
from booking.models import *


def get_currency():
    today_list = datetime.date.today().isoformat().split('-')
    today_xml = "{}.{}.{}.xml".format(today_list[2], today_list[1], today_list[0])
    res = requests.get("http://www.cbar.az/currencies/{}".format(today_xml))
    d = xmltodict.parse(res.content, xml_attribs=True)
    for i in d['ValCurs']['ValType'][1]['Valute']:
        if i['@Code'] == 'USD':
            return i['Value']


def vessel_schedule_capacity_update(booking_id):
    booking = Booking.objects.get(pk=booking_id)
    cargo_capacity = BookingCargoItem.objects.filter(booking__booking=booking)
    pass
