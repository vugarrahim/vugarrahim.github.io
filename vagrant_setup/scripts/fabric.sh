#!/bin/bash

# Some tutorials:
#   - https://www.digitalocean.com/community/tutorials/how-to-use-fabric-to-automate-administration-tasks-and-deployments
#   - http://docs.fabfile.org/en/latest/tutorial.html
#   - https://confluence.atlassian.com/pages/viewpage.action?pageId=270827678

. /vagrant/vagrant_setup/config.txt


echo "----- Fabric: Installing ..."
sudo aptitude install -y fabric


# sudo -u $APP_USER bash << EOF
# # -------[script begins]-------

# # Create SSH Keygen for fabric and other stuff
# ps -e  | grep [s]sh-agent
# ssh-keygen
# ls -a ~/.ssh

# # -------[script ends]-------
# EOF


# copy Fabfile.py from template
sed 's|#{APP_USER}|'$APP_USER'|g' $VAGRANT_TMP_PATH/fabfile.py > $VAGRANT_TMP_PATH/fabfile.py.bak
sed -i -e 's|#{APP_NAME}|'$APP_NAME'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/fabfile.py.bak
sudo mv $VAGRANT_TMP_PATH/fabfile.py.bak $DJANGO_PATH/fabfile.py