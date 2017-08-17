#!/bin/bash

. /vagrant/vagrant_setup/config.txt



# Development tools
echo "----- Nginx: Set up Nginx as a server..."
sudo aptitude install -y nginx
sudo service nginx start


# Setup of Nginx
echo "----- Nginx: Create an Nginx virtual server configuration..."
sed 's|#{APP_NAME}|'$APP_NAME'|g' $VAGRANT_TMP_PATH/nginx.server > $VAGRANT_TMP_PATH/nginx.server.bak
sed -i -e  's|#{APP_SERVER}|'$APP_SERVER'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/nginx.server.bak
sudo mv -i $VAGRANT_TMP_PATH/nginx.server.bak  /etc/nginx/sites-available/$APP_NAME
sudo ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/$APP_NAME
sudo service nginx restart 
