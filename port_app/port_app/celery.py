from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'port_app.settings')

app = Celery('port_app')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


"""
TUTS:
 - ref: http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
 `` (port_app) port_app_django@beta:$ celery -A port_app worker -l info ``
 `` (port_app) port_app_django@beta:$ celery help ``
 `` (port_app) port_app_django@beta:$ celery -A port_app beat  ``
 `` (port_app) port_app_django@beta:$ celery -A port_app worker -B -l info   ``
 `` (port_app) port_app_django@beta:$ celery -A port_app worker --loglevel=DEBUG --beat   ``
 `` (port_app) port_app_django@beta:$ celery multi start -A port_app w1 --beat -l info   `` *
 `` (port_app) port_app_django@beta:$ celery multi start -A port_app w1 --beat -l info --statedb=/webapps/port_app/run/celery/%n.state  ``



 `` (port_app) port_app_django@beta:$ celery -A app worker -l info
 `` (port_app) port_app_django@beta:$ celery beat -A app ``


 - this one worked:
   https://www.digitalocean.com/community/tutorials/how-to-use-celery-with-rabbitmq-to-queue-tasks-on-an-ubuntu-vps

   celery -A port_app worker -B -l info &
"""

app.conf.update(
    BROKER_URL='redis://localhost:6379/0',
    CELERYBEAT_SCHEDULER='djcelery.schedulers.DatabaseScheduler',
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERY_DISABLE_RATE_LIMITS=True,
    CELERY_ACCEPT_CONTENT=['json', ],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)
