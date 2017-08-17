#!/bin/bash

. /vagrant/vagrant_setup/config.txt

# https://github.com/arut/nginx-rtmp-module/wiki/Installing-on-Ubuntu-using-PPAs

<<COMMENT1
sudo apt-get remove nginx # Removes all but config files.

sudo apt-get purge nginx # Removes everything.

sudo apt-get autoremove # After using any of the above commands, use this in order to remove dependencies used by nginx which are no longer required.

sudo apt-get purge nginx-common
COMMENT1

# Remove old nginx
sudo apt-get purge -y nginx
sudo apt-get purge -y nginx-common


mkdir ~/working && cd ~/working && pwd

sudo apt-get install dpkg-dev
sudo apt-get source nginx

# sudo nano debian/rules
# --add-module=/root/working/nginx-rtmp-module \
# --add-module=/home/azureuser/working/nginx-rtmp-module \

# -- get folder name (alternative: ls -d -- */ )
ng_folder=$(ls -tr | tail -n 1)
ng_version=${ng_folder#*-}
sudo git clone https://github.com/arut/nginx-rtmp-module.git
cd $ng_folder



# sudo ./configure --add-module=${PWD%/*}/nginx-rtmp-module # not working with this method :'(
sudo sed -i '/ngx_http_substitutions_filter_module \\/a\\t--add-module='${PWD%/*}'/nginx-rtmp-module \\' debian/rules

sudo apt-get build-dep -y nginx
sudo dpkg-buildpackage -b


cd ~/working

# sudo dpkg --install nginx-common_1.4.6-1ubuntu3.2_all.deb nginx-full_1.4.6-1ubuntu3.2_amd64.deb
echo "----- Installing the Nginx";
sudo dpkg --install $(find . -type f -name '*nginx-common_*.deb') $(find . -type f -name '*nginx-full_*.deb')


sudo service nginx status
sudo service nginx start  # if nginx isn't running.

echo "--- Clean tmp files"
sudo rm -rfv  ~/working

# Setup of Nginx
echo "----- Nginx: Create an Nginx virtual server configuration..."
sed 's|#{APP_NAME}|'$APP_NAME'|g' $VAGRANT_TMP_PATH/nginx_capture.server > $VAGRANT_TMP_PATH/nginx_capture.server.bak
sed -i -e  's|#{APP_SERVER}|'$APP_SERVER'|g' -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/nginx_capture.server.bak
sudo mv -i $VAGRANT_TMP_PATH/nginx_capture.server.bak  /etc/nginx/sites-available/$APP_NAME
sudo ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/$APP_NAME
sudo service nginx restart


echo "----- Nginx: configure an RMTP server"
# cat /etc/nginx/nginx.conf
[ -d /etc/nginx/rtmp-enabled ] || sudo mkdir /etc/nginx/rtmp-enabled
printf '\n\nrtmp {\n\t%s\n\t%s\n}' '# include rtmp parameters' 'include /etc/nginx/rtmp-enabled/*;' | sudo tee -a /etc/nginx/nginx.conf
sed 's|#{APP_SERVER}|'$APP_SERVER'|g' $VAGRANT_TMP_PATH/nginx_rmtp.server > $VAGRANT_TMP_PATH/nginx_rmtp.server.bak
sed -i -e 's|#{APP_PATH}|'$APP_PATH'|g' $VAGRANT_TMP_PATH/nginx_rmtp.server.bak
sudo mv -i $VAGRANT_TMP_PATH/nginx_rmtp.server.bak  /etc/nginx/rtmp-enabled/$APP_NAME

sudo mkdir -p $APP_PATH/capture

sudo usermod -a -G $APP_USER_GROUP www-data
sudo chown www-data:$APP_USER_GROUP $APP_PATH/capture

sudo service nginx restart







