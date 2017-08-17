from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '#{APP_NAME}.settings')

app = Celery('#{APP_NAME}')

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
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery -A #{APP_NAME} worker -l info ``
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery help ``
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery -A #{APP_NAME} beat  ``
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery -A #{APP_NAME} worker -B -l info   ``
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery -A #{APP_NAME} worker --loglevel=DEBUG --beat   ``
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery multi start -A #{APP_NAME} w1 --beat -l info   `` *
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery multi start -A #{APP_NAME} w1 --beat -l info --statedb=/webapps/#{APP_NAME}/run/celery/%n.state  ``



 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery -A app worker -l info
 `` (#{APP_NAME}) #{APP_NAME}_django@beta:$ celery beat -A app ``


 - this one worked:
   https://www.digitalocean.com/community/tutorials/how-to-use-celery-with-rabbitmq-to-queue-tasks-on-an-ubuntu-vps

   celery -A #{APP_NAME} worker -B -l info &
"""
app.conf.update(
    CELERYBEAT_SCHEDULER='djcelery.schedulers.DatabaseScheduler',
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERY_DISABLE_RATE_LIMITS = True,
    # CELERY_TIMEZONE = 'Asia/Baku',
    CELERY_ACCEPT_CONTENT = ['json',],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
)
