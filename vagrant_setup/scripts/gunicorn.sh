#!/bin/bash

. /vagrant/vagrant_setup/config.txt


# Install Gunicorn to app's vortual envoirenment
echo "----- Gunicorn: Installing..."
sudo -u $APP_USER bash << EOF
# -------[script begins]-------

cd $APP_PATH
source bin/activate
pip install --no-cache-dir gunicorn setproctitle

# -------[script ends]-------
EOF


# Set up gunicorn_start file
echo "----- Gunicorn: Set up gunicorn_start file..."
sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/gunicorn_start.sh > $VAGRANT_TMP_PATH/gunicorn_start.bak
sed -i -e  's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' -e 's|#{APP_USER_GROUP}|'$APP_USER_GROUP'|g' $VAGRANT_TMP_PATH/gunicorn_start.bak
sudo mv -i $VAGRANT_TMP_PATH/gunicorn_start.bak  $APP_PATH/bin/gunicorn_start
sudo chmod u+x $APP_PATH/bin/gunicorn_start
sudo chown -R $APP_USER:$APP_USER_GROUP $APP_PATH/bin/gunicorn_start