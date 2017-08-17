#!/bin/bash

. /vagrant/vagrant_setup/config.txt


echo "----- Backup: get backup for django app for after provision folder mount"
# mkdir -p $VAGRANT_SETUP_PATH/django-app/
# sudo cp -i -r $DJANGO_PATH/*  $VAGRANT_APP_BACKUP_PATH/
sudo cp -i -r -n $DJANGO_PATH/  $VAGRANT_APP_BACKUP_PATH/
sudo chmod u+x $VAGRANT_SCRIPT_PATH/after.sh


# Set up gunicorn_start file
echo "----- Vagrantfile: Set up synced folders..."
# sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/gunicorn_start.sh > $VAGRANT_TMP_PATH/gunicorn_start.bak
sed -i -e  's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' -e 's|#{APP_USER}|'$APP_USER'|g' -e 's|#{APP_USER_GROUP}|'$APP_USER_GROUP'|g' $VAGRANT_APP_BACKUP_PATH/Vagrantfile
# sudo mv -i $VAGRANT_TMP_PATH/gunicorn_start.bak  $APP_PATH/bin/gunicorn_start