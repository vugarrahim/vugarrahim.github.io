#!/bin/bash
# installation of WeasyPrint
# - http://weasyprint.org/docs/install/
# - http://lxml.de/installation.html
# - http://stackoverflow.com/a/6504860/968751
. /vagrant/vagrant_setup/config.txt

echo "----- WeasyPrint: install apt-get packages"
sudo apt-get update
sudo apt-get install -y python3-lxml python-dev python-pip libxml2-dev libxslt1-dev libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

sudo -u $APP_USER bash << EOF
# -------[script begins]-------

echo "----- WeasyPrint: install pip packages"
cd $APP_PATH && source bin/activate
pip install --no-cache-dir WeasyPrint

# -------[script ends]-------
EOF