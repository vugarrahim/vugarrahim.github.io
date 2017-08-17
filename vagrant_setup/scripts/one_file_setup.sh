#!/usr/bin/env bash

# This script is calling directly from the Vagrantfile and sets up
# Ubuntu 14.04 server with: 
#  - Python2.7 & Python3.4
#  - Django
#  - Git
#  - Gunicorn
#  - Supervisior
#  - Nginx
#  - PostgreSQL
#  - Fabric
# It also creates a database for the project
# and a user that can access it.

# GET APP VARIABLES FROM CONFIG
. /vagrant/vagrant_setup/config.txt



# login as root
sudo su
echo "Starting Provision as `whoami`"

echo "----- Provision: System Update & Upgrade..."
sudo aptitude -y update
sudo aptitude -y upgrade

# Development tools
echo "----- Provision: Installing SUDO Requirements..."
sudo aptitude install -y postgresql postgresql-contrib libpq-dev python-dev supervisor nginx git python3-pip fabric


# Create user group and assign home directory
echo "----- Provision: Create APP User and assign home directory..."
sudo groupadd --system $APP_USER_GROUP
sudo useradd --system --gid $APP_USER_GROUP --shell /bin/bash --home $APP_PATH $APP_USER

# Create apps user and assign app directory to him
sudo mkdir -p $APP_PATH
sudo chown $APP_USER $APP_PATH

# Give write permission to app user
sudo chown -R $APP_USER:users $APP_PATH
sudo chmod -R g+w $APP_PATH
sudo usermod -a -G users `whoami`






# ------------------------------------------------------------------------------
# Database creation
# http://dba.stackexchange.com/a/27034
# sudo su - postgres
# createuser --interactive -P
# createdb --owner socset db_socset
# psql -U postgres -l
# psql -U postgres -d db_socset
# \dt
# SELECT * FROM reports_data;
# \q
echo "----- PostgreSQL: Creating database and user..."
sudo su postgres << EOF
# -------[script begins]-------

# psql --help
psql -c "
CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASSWORD';
"
createdb --owner $APP_DB_USER $APP_DB_NAME


# -------[script ends]-------
EOF








# ------------------------------------------------------------------------------
# RUN SCRIPTS AS APP USER
# exec sudo -u $APP_USER /bin/sh - << EOF
sudo -u $APP_USER bash << EOF
# -------[script begins]-------
echo "----- LOGINED AS ----"
whoami

# Create user group and assign home directory
echo "----- Provision: Create Virtual Environment..."
cd $APP_PATH
pwd
pyvenv-3.4 --without-pip . # because of Ubuntu 14.04 PIP3 issue we create venv without pip
source bin/activate
python --version

echo "----- VEnv: Install PIP..."
wget https://bootstrap.pypa.io/ez_setup.py -O - | python
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

echo "----- PIP: Install Requirements for APP..."
pip install django psycopg2 gunicorn setproctitle

# create django app
django-admin startproject $APP_NAME

# Create log folder for logs
mkdir -p $APP_PATH/logs/
touch $APP_PATH/logs/gunicorn_supervisor.log 



# -------[script ends]-------
EOF






# ------------------------------------------------------------------------------
# Set up gunicorn_start file
echo "----- Gunicorn: Set up gunicorn_start file..."
sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/gunicorn_start.sh > $VAGRANT_TMP_PATH/gunicorn_start.bak
sed -i -e  's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' -e 's|#{APP_USER_GROUP}|'$APP_USER_GROUP'|g' $VAGRANT_TMP_PATH/gunicorn_start.bak
sudo mv -i $VAGRANT_TMP_PATH/gunicorn_start.bak  $APP_PATH/bin/gunicorn_start
sudo chmod u+x $APP_PATH/bin/gunicorn_start
sudo chown -R $APP_USER:$APP_USER_GROUP $APP_PATH/bin/gunicorn_start



# Setup of Supervisor
echo "----- Supervisor: Starting and monitoring..."
sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/supervisor.conf > $VAGRANT_TMP_PATH/supervisor.conf.bak
sed -i -e  's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/supervisor.conf.bak
sudo mv -i $VAGRANT_TMP_PATH/supervisor.conf.bak  /etc/supervisor/conf.d/$APP_NAME.conf
# operate
sudo supervisorctl reread
sudo supervisorctl update


# Setup of Nginx
echo "----- Nginx: Create an Nginx virtual server configuration..."
sed 's|#{APP_NAME}|'$APP_NAME'|g' $VAGRANT_TMP_PATH/nginx.server > $VAGRANT_TMP_PATH/nginx.server.bak
sed -i -e  's|#{APP_SERVER}|'$APP_SERVER'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/nginx.server.bak
sudo mv -i $VAGRANT_TMP_PATH/nginx.server.bak  /etc/nginx/sites-available/$APP_NAME
sudo ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/$APP_NAME
sudo service nginx restart 


# Setup of Fabric
echo "----- Fabric: Create Fabfile.py ..."
sudo cp $VAGRANT_TMP_PATH/fabfile.py  $DJANGO_PATH/fabfile.py


echo "----- Backup: get backup for django app for after provision folder mount"
# mkdir -p $VAGRANT_SETUP_PATH/django-app/
# sudo cp -i -r $DJANGO_PATH/* $VAGRANT_SETUP_PATH/django-app/
sudo cp -i -r -n $DJANGO_PATH/  $VAGRANT_APP_BACKUP_PATH/
sudo chmod u+x $VAGRANT_SCRIPT_PATH/after.sh

echo "---"
echo "---"
echo "Box provisioned! Now log into vagrant, intialize the virtual environment, \
start the dev server and you'll be able to see the django-app!"
echo "---"
echo "---"

exit 0



# CREDITS:
#  - http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/
#  - https://gist.github.com/damienstanton/f63c8aed8f4a432cfcf2
#  - https://gist.github.com/sspross/330b5b1f08ada7b70c24
#  - https://pypi.python.org/pypi/setuptools
#  - http://stackoverflow.com/a/17517654/968751
#  - https://pip.pypa.io/en/latest/installing.html
#  - https://confluence.atlassian.com/pages/viewpage.action?pageId=270827678
#  - http://stackoverflow.com/a/22947716/968751
#  - http://superuser.com/a/468163
#  - http://stackoverflow.com/a/8998789/968751
#  - http://stackoverflow.com/a/24696790/968751
#  - http://stackoverflow.com/a/11603385/968751