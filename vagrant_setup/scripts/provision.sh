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

# GET APP VARIABLES FROM CONFIG FILE
. /vagrant/vagrant_setup/config.txt



# login as root
sudo su
echo "Starting Provision as `whoami`"

echo "----- Provision: System Update & Upgrade..."
sudo aptitude -y update
sudo aptitude -y upgrade

# Development tools
echo "----- Provision: Installing BASIC Requirements..."
sudo aptitude install -y libpq-dev python-dev git python3-pip

# Note: in the new version of the Ubuntu pyvenv not preinstalled
if ! pyvenv_3="$(type -p pyvenv-3.4)" || [ -z "$pyvenv_3" ]; then
  # install pyvenv-3.4
  sudo apt-get install python3.4-venv # http://askubuntu.com/a/528625, http://stackoverflow.com/a/7522866/968751
fi


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



# SETTING UP DJANGO
source $VAGRANT_SCRIPT_PATH/django.sh

# SETTING UP DATABASE: PostgreSQL
source $VAGRANT_SCRIPT_PATH/postgresql.sh

# SETTING UP GUNICORN
source $VAGRANT_SCRIPT_PATH/gunicorn.sh

# SETTING UP SUPERVISOR
source $VAGRANT_SCRIPT_PATH/supervisor.sh

# SETTING UP NGINX
source $VAGRANT_SCRIPT_PATH/nginx.sh

# Setup of Fabric
source $VAGRANT_SCRIPT_PATH/fabric.sh

# Setup of Celery
source $VAGRANT_SCRIPT_PATH/celery_redis.sh

# Setup of Vagrant's synced folder parameters
source $VAGRANT_SCRIPT_PATH/vagrant_synced_folder.sh

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