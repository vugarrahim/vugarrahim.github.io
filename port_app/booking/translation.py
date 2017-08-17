from modeltranslation.translator import translator, TranslationOptions
from .models import Port, Vessel, Terminal, CargoType, PassengerTransportType


class PortsTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(Port, PortsTranslationOptions)


class VesselsTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(Vessel, VesselsTranslationOptions)


class TerminalsTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(Terminal, TerminalsTranslationOptions)


class CargoTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(CargoType, CargoTypeTranslationOptions)


class PassengerTransportTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


translator.register(PassengerTransportType, PassengerTransportTypeTranslationOptions)