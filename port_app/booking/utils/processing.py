from django.db.models import Sum, F
from booking.utils.model_choices import TRANSIT_TYPE_CHOICES
from booking.utils.tools import get_or_none, trueround, percentage
from booking.models import CargoType, PassengerTransportType, VesselCargoFee, VesselPassengerFee, PortFee

import logging

logr = logging.getLogger(__name__)


class BookingProcessor(object):
    """
        Handles booking pricing and availability of vessel
    """

    def __init__(self, vessel=None, direction=None, schedule=None):
        self.vessel = vessel
        self.direction = direction
        if schedule:
            self.schedule = schedule
            self.vessel = schedule.vessel
            self.direction = schedule.direction


    def pricing_cargo_type(self, type):
        """
            Get price for single cargo type
        """
        cargo_type = CargoType.objects.get(pk=type)
        vessel_fee = VesselCargoFee.objects.filter(vessel=self.vessel, direction=self.direction,
                                                   cargo_type=cargo_type).last()

        return vessel_fee.price if vessel_fee else 0


    def calc_cargo_prices(self, cargo_types=[]):
        """
            Calculate cargo prices by vessel, direction and cargo type
            - pattern for cargo types should be: [{'type_pk': 1,'count': 3},{'type_pk': 2,'count': 0},{'type_pk': 3,'count': 1}]
        """
        total = 0
        for type in cargo_types:
            total += self.pricing_cargo_type(type=type['type_pk']) * int(type['count'])

        return total


    def get_total_cargo_m(self, cargo_types=[]):
        '''
            Get total meters of cargo types
        '''
        logr.debug(cargo_types)
        total_meter = []
        for type in cargo_types:
            cargo = get_or_none(CargoType, pk=type['type_pk'])
            if cargo:
                total_meter.append(cargo.length * int(type['count']))

        return sum(total_meter)


    def get_transit_percentage(self):
        '''
            Transit fee percentage of direction from port
        '''
        portfee = PortFee.objects.filter(port=self.direction.from_d.port, direction=self.direction).last()
        return portfee.transit_price if portfee else 0


    def calc_port_fee(self, cargo_types=[], port=None):
        '''
            Calculate port fee for cargos
        '''
        port = port if port else self.direction.from_d.port

        meter = self.get_total_cargo_m(cargo_types=cargo_types)
        fee = PortFee.objects.filter(port=port, direction=self.direction).last()
        port_price = fee.price if fee else 0

        return (port_price * meter)


    def calc_passenger_price(self, type=None):
        '''
            Calculate passenger prices for schedule
        '''
        price = 0

        if type:
            passanger_price = VesselPassengerFee.objects.filter(vessel=self.vessel, direction=self.direction,
                                                                passenger_transport_type=type).last()
            price = passanger_price.price if passanger_price else 0

        return price


    def est_passenger_price(self, count=0):
        '''
            Estimate min and max price for passengers
        '''
        total_min, total_max = 0, 0
        passanger_types = PassengerTransportType.objects.all().only("id")
        passanger_prices = VesselPassengerFee.objects.filter(
            vessel=self.vessel,
            direction=self.direction,
            passenger_transport_type__id__in=[i.id for i in passanger_types]
        ).values('price')

        # logr.debug(passanger_prices)

        if len(passanger_prices):
            total_min = min([prc['price'] for prc in passanger_prices]) * count
            total_max = max([prc['price'] for prc in passanger_prices]) * count

        return {
            'min': total_min,
            'max': total_max
        }


    def check_passanger_availability(self):
        '''
            Check passanger availability of schedule
        '''
        from django.core import serializers
        import json

        lefted_spots = []
        available_passangers = {}
        booked_passangers = {}
        past_bookings = self.schedule.booking_infos.all()

        # collect all passangers
        for booking in past_bookings:
            passengers = booking.passengers.all()
            for passenger in passengers:
                type_id = "type_{0}".format(passenger.passenger_transport_type_id)
                if type_id in booked_passangers:
                    booked_passangers[type_id] += 1
                else:
                    booked_passangers[type_id] = 1

        # vessel passenger capacity
        capacities = self.vessel.capacities.all()
        for capacity in capacities:
            type_id = "type_{0}".format(capacity.passenger_transport_type_id)
            if not type_id in available_passangers:
                available_passangers[type_id] = {
                    'count': capacity.count * capacity.passenger_transport_type.passenger_count,
                    'obj': json.loads(serializers.serialize("json", [capacity.passenger_transport_type, ]))[0]
                }

        # logr.debug(booked_passangers)
        # logr.debug(available_passangers)

        # total result
        for key, val in available_passangers.items():
            booked_spot = booked_passangers[key] if key in booked_passangers else 0
            lefted_spots.append({
                'spot': val['count'] - booked_spot,
                'obj': val['obj']
            })

        return lefted_spots


    def is_passenger_availabile(self, passenger_type=None):
        '''
            Check single passenger
        '''
        booked_count = self.schedule.booking_infos.filter(passengers__passenger_transport_type=passenger_type).count()
        type_capacity = self.vessel.capacities.filter(passenger_transport_type=passenger_type).aggregate(total=Sum(F('count') * F('passenger_transport_type__passenger_count')))

        return type_capacity['total'] - booked_count > 0


    def is_cargoes_availabile(self, cargoes_types=None):
        '''
            Check all cargo
        '''
        if cargoes_types:
            load_capacity = self.schedule.vessel.load_capacity
            occupied_space = self.schedule.booking_infos.all().aggregate(total_length=Sum('cargoes__cargo_type__length'))
            requested_space = sum([type.length for type in cargoes_types])
            occupied_length = occupied_space['total_length'] if occupied_space['total_length'] else 0

            return (occupied_length + requested_space) <= load_capacity

        return True


    def is_passengers_availabile(self, passenger_types=None):
        '''
            Check all passengers
        '''
        from collections import Counter

        if passenger_types:
            capacities = self.vessel.capacities.all().values('id').annotate(
                transport_id=F('passenger_transport_type__id'),
                capacity=F('count') * F('passenger_transport_type__passenger_count'))
            counter = Counter([ty.id for ty in passenger_types])
            avialability = []

            for capacity in capacities:
                # logic: capacity - used - requested_spots > 0
                avialability.append(
                    capacity['capacity'] - self.schedule.booking_infos.filter(
                        passengers__passenger_transport_type__id=capacity['transport_id']).count() - counter[
                        capacity['transport_id']] >= 0
                )

            return all(avialability)

        return True


    def is_availabile(self, passenger_formset, cargo_formset, type=None):
        '''
            Check availability
        '''
        # passenger stuff
        passenger_types = []
        for form in passenger_formset:
            if type == 'away':
                passenger_types.append(form.cleaned_data['passenger_transport_type'])
            elif type == 'back':
                passenger_types.append(form.cleaned_data['transport_type_return'])

        # cargo stuff
        cargo_types = []
        for form in cargo_formset:
            cargo_types.append(form.cleaned_data['cargo_type'])

        return self.is_cargoes_availabile(cargoes_types=cargo_types) and self.is_passengers_availabile(
            passenger_types=passenger_types)



class BookingPrice(object):
    def __init__(self, booking=None):
        '''
            Class to calculate booking price more effectively
        '''
        self.booking = booking
        self.booking_infos = booking.bookings.all()
        self.passenger_prices = {}
        self.cargo_prices = {}
        self.port_fees = {}
        self.non_transit = {}

        # store schedules for referring multiple times
        if len(self.booking_infos):
            self.schedule_away = self.booking_infos[0].vessel_schedule
            self.process_away = BookingProcessor(schedule=self.schedule_away)
        if len(self.booking_infos) > 1:
            self.schedule_back = self.booking_infos[1].vessel_schedule
            self.process_back = BookingProcessor(schedule=self.schedule_back)

    def calc_passenger(self):
        '''
            Calculate passenger prices
        '''
        if self.schedule_away:
            passengers_away = self.booking_infos[0].passengers.all()
            passengers_away_prices = []

            for passenger in passengers_away:
                passengers_away_prices.append(
                    self.process_away.calc_passenger_price(type=passenger.passenger_transport_type)
                )
            self.passenger_prices['away'] = sum(passengers_away_prices)

        try:
            if self.schedule_back:
                passengers_back = self.booking_infos[1].passengers.all()
                passengers_back_prices = []

                for passenger in passengers_back:
                    passengers_back_prices.append(
                        self.process_back.calc_passenger_price(type=passenger.passenger_transport_type)
                    )
                self.passenger_prices['back'] = sum(passengers_back_prices)
        except:
            pass

        return self.passenger_prices

    def calc_cargo(self):
        '''
            Calculate cargo prices
        '''
        if self.schedule_away:
            cargoes_away = self.booking_infos[0].cargoes.all()
            cargoes_away_prices = []

            for cargo in cargoes_away:
                cargoes_away_prices.append(
                    self.process_away.pricing_cargo_type(type=cargo.cargo_type_id)
                )
            self.cargo_prices['away'] = sum(cargoes_away_prices)

        try:
            if self.schedule_back:
                cargoes_back = self.booking_infos[1].cargoes.all()
                cargoes_back_prices = []

                for cargo in cargoes_back:
                    cargoes_back_prices.append(
                        self.process_back.pricing_cargo_type(type=cargo.cargo_type_id)
                    )
                self.cargo_prices['back'] = sum(cargoes_back_prices)
        except:
            pass

        return self.cargo_prices

    def calc_portfee(self):
        '''
            Calculate port fee
        '''
        from collections import Counter

        if self.schedule_away:
            cargoes_away = self.booking_infos[0].cargoes.all().values('cargo_type')
            counter_away = Counter([i['cargo_type'] for i in cargoes_away])
            cargo_types_away = [{'type_pk': key, 'count': val} for key, val in counter_away.items()]
            self.port_fees['away'] = self.process_away.calc_port_fee(cargo_types=cargo_types_away)

        try:
            if self.schedule_back:
                cargoes_back = self.booking_infos[1].cargoes.all().values('cargo_type')
                counter_back = Counter([i['cargo_type'] for i in cargoes_back])
                cargo_types_back = [{'type_pk': key, 'count': val} for key, val in counter_back.items()]
                self.port_fees['back'] = self.process_back.calc_port_fee(cargo_types=cargo_types_back)
        except:
            pass

        return self.port_fees

    def calc_non_transit(self):
        '''
            Calculate non-transit fee
        '''
        if self.booking.transit_type == TRANSIT_TYPE_CHOICES[1][0]:
            percentage_away = self.process_away.get_transit_percentage()
            total_away = 0
            total_back = 0

            if 'away' in self.passenger_prices:
                total_away += self.passenger_prices['away']

            if 'away' in self.cargo_prices:
                total_away += self.cargo_prices['away']

            if 'away' in self.port_fees:
                total_away += self.port_fees['away']

            self.non_transit['away'] = {
                'percentage': percentage_away,
                'value': trueround(percentage(percentage_away, total_away), 2)
            }

            try:
                if self.schedule_back:
                    percentage_back = self.process_back.get_transit_percentage()

                    if 'back' in self.passenger_prices:
                        total_back += self.passenger_prices['back']

                    if 'back' in self.cargo_prices:
                        total_back += self.cargo_prices['back']

                    if 'back' in self.port_fees:
                        total_back += self.port_fees['back']

                    self.non_transit['back'] = {
                        'percentage': percentage_back,
                        'value': trueround(percentage(percentage_back, total_back), 2)
                    }
            except:
                pass

        return self.non_transit

    def calc_total(self):
        '''
            Calculate total
        '''
        self.calc_passenger()
        self.calc_cargo()
        self.calc_portfee()
        self.calc_non_transit()
        total = {'away': 0}

        if 'away' in self.passenger_prices:
            total['away'] += self.passenger_prices['away']

        if 'away' in self.cargo_prices:
            total['away'] += self.cargo_prices['away']

        if 'away' in self.port_fees:
            total['away'] += self.port_fees['away']

        if 'away' in self.non_transit:
            total['away'] += self.non_transit['away']['value']

        total['away'] = trueround(total['away'], 2)

        try:
            if self.schedule_back:
                total['back'] = 0
                if 'back' in self.passenger_prices:
                    total['back'] += self.passenger_prices['back']

                if 'back' in self.cargo_prices:
                    total['back'] += self.cargo_prices['back']

                if 'back' in self.port_fees:
                    total['back'] += self.port_fees['back']

                if 'back' in self.non_transit:
                    total['back'] += self.non_transit['back']['value']

                total['back'] = trueround(total['back'], 2)
        except:
            pass

        return total

    def result(self):
        '''
            Get results
        '''
        total = self.calc_total()
        return {
            'passengers': self.passenger_prices,
            'cargos': self.cargo_prices,
            'portfee': self.port_fees,
            'non-transit': self.non_transit,
            'total': total,
        }

