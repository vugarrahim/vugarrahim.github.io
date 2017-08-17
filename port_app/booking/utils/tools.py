import logging
import random
import string

# Get an instance of a logger
logr = logging.getLogger(__name__)


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def rand_key(size=8):
    import uuid

    return uuid.uuid1().hex[0:12].upper()


def rand_vessel_shedule():
    letter_upper = list(string.ascii_uppercase)
    ran_number = random.randint(1000, 9999)
    letter1 = random.choice(letter_upper)
    letter2 = random.choice(letter_upper)
    return "{}{}{}".format(letter1, letter2, ran_number)


def percentage(percent, whole):
    return (percent * whole) / 100.0


def calc_schedule_capacity(schedule):
    '''
        Helper function for the calculating schedule capacity and saving them
    '''
    s = 0
    schedule.current_cargo_capacity = schedule.vessel.load_capacity
    for vessel_p_c in schedule.vessel.capacities.all():
        s += vessel_p_c.count * vessel_p_c.passenger_transport_type.passenger_count
    schedule.current_passenger_count = s
    schedule.save()


def trueround(number, places=0):
    '''
    trueround(number, places)

    example:

        >>> trueround(2.55, 1) == 2.6
        True

    uses standard functions with no import to give "normal" behavior to
    rounding so that trueround(2.5) == 3, trueround(3.5) == 4,
    trueround(4.5) == 5, etc. Use with caution, however. This still has
    the same problem with floating point math. The return object will
    be type int if places=0 or a float if places=>1.

    number is the floating point number needed rounding

    places is the number of decimal places to round to with '0' as the
        default which will actually return our interger. Otherwise, a
        floating point will be returned to the given decimal place.

    Note:   Use trueround_precision() if true precision with
            floats is needed

    GPL 2.0
    copywrite by Narnie Harshoe <signupnarnie@gmail.com>
    '''
    place = 10 ** (places)
    rounded = (int(number * place + 0.5 if number >= 0 else -0.5)) / place
    if rounded == int(rounded):
        rounded = int(rounded)
    return rounded


def trueround_precision(number, places=0, rounding=None):
    '''
    trueround_precision(number, places, rounding=ROUND_HALF_UP)

    Uses true precision for floating numbers using the 'decimal' module in
    python and assumes the module has already been imported before calling
    this function. The return object is of type Decimal.

    All rounding options are available from the decimal module including
    ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN,
    ROUND_HALF_UP, ROUND_UP, and ROUND_05UP.

    examples:

        >>> trueround(2.5, 0) == Decimal('3')
        True
        >>> trueround(2.5, 0, ROUND_DOWN) == Decimal('2')
        True

    number is a floating point number or a string type containing a number on
        on which to be acted.

    places is the number of decimal places to round to with '0' as the default.

    Note:   if type float is passed as the first argument to the function, it
            will first be converted to a str type for correct rounding.

    GPL 2.0
    copywrite by Narnie Harshoe <signupnarnie@gmail.com>
    '''
    from decimal import Decimal as dec
    from decimal import ROUND_HALF_UP
    from decimal import ROUND_CEILING
    from decimal import ROUND_DOWN
    from decimal import ROUND_FLOOR
    from decimal import ROUND_HALF_DOWN
    from decimal import ROUND_HALF_EVEN
    from decimal import ROUND_UP
    from decimal import ROUND_05UP

    if type(number) == type(float()):
        number = str(number)
    if rounding == None:
        rounding = ROUND_HALF_UP
    place = '1.'
    for i in range(places):
        place = ''.join([place, '0'])
    return dec(number).quantize(dec(place), rounding=rounding)