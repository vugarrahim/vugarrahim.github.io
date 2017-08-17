#!/bin/bash

. /vagrant/vagrant_setup/config.txt



# Development tools
echo "----- Supervisor: Starting and monitoring..."
sudo aptitude install -y supervisor


# Install Gunicorn to app's vortual envoirenment
echo "----- Supervisor: Create log file"
sudo -u $APP_USER bash << EOF
# -------[script begins]-------

test -d $APP_PATH/logs/ || mkdir -p $APP_PATH/logs/
touch $APP_PATH/logs/gunicorn_supervisor.log

# -------[script ends]-------
EOF

echo "----- Supervisor: Create the Config file for $APP_NAME..."
sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/supervisor.conf > $VAGRANT_TMP_PATH/supervisor.conf.bak
sed -i -e  's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/supervisor.conf.bak
sudo mv -i $VAGRANT_TMP_PATH/supervisor.conf.bak  /etc/supervisor/conf.d/$APP_NAME.conf

# Read newly created supervisior apps
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart $APP_NAME 