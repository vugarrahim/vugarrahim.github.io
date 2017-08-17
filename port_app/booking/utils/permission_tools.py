from django.contrib.auth import get_user_model
import logging
# Get an instance of a logger
logr = logging.getLogger(__name__)
from .tools import get_or_none

User = get_user_model()


def permission_model_query(user, model):
    logr.debug(user.has_perm("{}.{}_all_view".format(model._meta.app_label, model._meta.model_name)))
    if user.has_perm("{}.{}_view".format(model._meta.app_label, model._meta.model_name)):
        queryset = model.objects.filter(owner=user)
        return queryset
    elif user.has_perm("{}.{}_all_view".format(model._meta.app_label, model._meta.model_name)):
        queryset = model.objects.all()
        return queryset
    else:
        return model.objects.none()
