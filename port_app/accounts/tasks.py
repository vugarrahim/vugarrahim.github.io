# -*- coding: utf-8 -*-
from __future__ import absolute_import
from port_app.celery import app
from .tools import send_activation
from django.contrib.auth import get_user_model

User = get_user_model()


# import the logging library
import logging
# Get an instance of a logger
logr = logging.getLogger(__name__)


#User kimi qeydiyyatdan kecenden sonra email tesdiq taski
@app.task(bind=True)
def send_activation_task(self, id):
    """
     When user creates responsible person for the debts Collection shares with automatically
    """
    user = User.objects.get(id=id)
    send_activation(user=user)
