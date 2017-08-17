#!/bin/bash

. /vagrant/vagrant_setup/config.txt



echo "----- RabbitMQ: Installing..."
sudo apt-get install -y rabbitmq-server




# Install Gunicorn to app's vortual envoirenment
echo "----- Celery: Installing within your virtualenv..."
sudo -u $APP_USER bash << EOF
# -------[script begins]-------

cd $APP_PATH
source bin/activate
pip install celery django-celery

# -------[script ends]-------
EOF


printf "\n\n--- Celery Ready: Now 
	1) Create the 'celery.py' file in the '$DJANGO_PATH/$APP_NAME' directory next to 'settings.py';
	2) Add the 'djcelery' to Django settings.INSTALLED_APPS;
	3) Then run the command below from within your virtualenv (you should be using virtual environments!); \n
	(your_app):$ celery -A $APP_NAME  worker -B -l info \n
"

# Create celery.py example for the app from template
sed 's|#{APP_NAME}|'$APP_NAME'|g' $VAGRANT_TMP_PATH/celery.py > $VAGRANT_TMP_PATH/celery.py.bak
sudo mv -i -n $VAGRANT_TMP_PATH/celery.py.bak  $DJANGO_PATH/$APP_NAME/celery.py


