#!/bin/bash

. /vagrant/vagrant_setup/config.txt



echo "----- Redis: Installing..."
sudo apt-get install -y redis-server
redis-server --version
redis-cli ping



# Install Gunicorn to app's vortual envoirenment
echo "----- Celery: Installing within your virtualenv..."
sudo -u $APP_USER bash << EOF
# -------[script begins]-------

cd $APP_PATH
source bin/activate
pip install --no-cache-dir celery[redis] django-celery

mkdir -p $APP_PATH/logs/
touch $APP_PATH/logs/celery-worker.log
# -------[script ends]-------
EOF


# Create celery.py example for the app from template
sed 's|#{APP_NAME}|'$APP_NAME'|g' $VAGRANT_TMP_PATH/celery_redis.py > $VAGRANT_TMP_PATH/celery.py.bak
sudo mv -i -n $VAGRANT_TMP_PATH/celery.py.bak  $DJANGO_PATH/$APP_NAME/celery.py

echo "----- Supervisor: Create the Config file for Celery..."
sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/celery_supervisor.conf > $VAGRANT_TMP_PATH/supervisor_celery.conf.bak
sed -i -e  's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' -e 's|#{DJANGO_PATH}|'$DJANGO_PATH'|g' $VAGRANT_TMP_PATH/supervisor_celery.conf.bak
sudo mv -i $VAGRANT_TMP_PATH/supervisor_celery.conf.bak  "/etc/supervisor/conf.d/${APP_NAME}_celery.conf"

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart $APP_NAME-celery

printf "\n\n--- Celery Ready: Now
	1) Create the 'celery.py' file in the '$DJANGO_PATH/$APP_NAME' directory next to 'settings.py';
	2) Add the 'djcelery' to Django settings.INSTALLED_APPS;
	3) Then run the command below from within your virtualenv (you should be using virtual environments!); \n
	(your_app):$ celery -A $APP_NAME  worker -B -l info \n
"