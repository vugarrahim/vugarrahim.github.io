#!/bin/bash

. /vagrant/vagrant_setup/config.txt


# ------------------------------------------------------------------------------
# RUN SCRIPTS AS APP USER
# exec sudo -u $APP_USER /bin/sh - << EOF
sudo -u $APP_USER bash << EOF
# -------[script begins]-------

echo "==========> LOGINED AS <=========="
whoami

# Create user group and assign home directory
echo "----- Django: Create Virtual Environment for Django w/ Python3 ..."
cd $APP_PATH
pwd
pyvenv-3.4 --without-pip . # because of Ubuntu 14.04 PIP3 issue we create venv without pip
source bin/activate
python --version

echo "----- Django venv: Install PIP..."
wget https://bootstrap.pypa.io/ez_setup.py -O - | python
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

echo "----- PIP: Install Django and Create APP..."
pip install django

# create django app
django-admin startproject $APP_NAME

# Create log folder for logs
mkdir -p $APP_PATH/logs/

# -------[script ends]-------
EOF
