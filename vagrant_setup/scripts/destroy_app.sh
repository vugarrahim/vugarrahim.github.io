#!/bin/bash

. /vagrant/vagrant_setup/config.txt

# Uninstalling the Django application

# Remove the virtual server from Nginx sites-enabled folder
sudo rm /etc/nginx/sites-enabled/$APP_NAME

# Restart Nginx:
sudo service nginx restart 

# If you never plan to use this application again, you can remove its config file also from the sites-available directory
sudo rm /etc/nginx/sites-available/$APP_NAME

# Stop the application with Supervisor:
sudo supervisorctl stop $APP_NAME

# Remove the application from Supervisor’s control scripts directory:
sudo rm /etc/supervisor/conf.d/$APP_NAME.conf

# If you never plan to use this application again, you can now remove its entire directory from webapps:
sudo rm -r $APP_PATH