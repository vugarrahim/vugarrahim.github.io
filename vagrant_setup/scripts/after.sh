#!/bin/bash

. /vagrant/vagrant_setup/config.txt


# sudo -u $APP_USER bash << EOF
# # -------[script begins]-------

# # Create SSH Keygen for fabric and other stuff
# ps -e  | grep [s]sh-agent
# ssh-keygen
# ls -a ~/.ssh

# # -------[script ends]-------
# EOF


sudo mv -i /vagrant/setup/django-app/* $DJANGO_PATH/
sudo rm -rm /vagrant/setup/django-app/