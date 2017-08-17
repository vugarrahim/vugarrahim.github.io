from django import forms
from django.utils.safestring import mark_safe

# import the logging library
import logging

# Get an instance of a logger
logr = logging.getLogger(__name__)


class PlainTextWidget(forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is not None:
            for choice in self.choices:
                if value == choice[0]:
                    return mark_safe(choice[1])
        else:
            return '-'