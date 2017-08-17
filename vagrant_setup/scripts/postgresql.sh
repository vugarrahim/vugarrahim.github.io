#!/bin/bash

. /vagrant/vagrant_setup/config.txt


# Installing to server
echo "----- PostgreSQL: Installing..."
apt-get --purge remove postgresql postgresql-contrib
sudo aptitude install -y postgresql postgresql-contrib


# Database creation
echo "----- PostgreSQL: Creating database and user..."
sudo su postgres << EOF
# -------[script begins]-------

# psql --help
psql -c "
CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASSWORD';
ALTER USER $APP_DB_USER CREATEDB;
"
createdb --owner $APP_DB_USER $APP_DB_NAME


# -------[script ends]-------
EOF


sudo -u $APP_USER bash << EOF
# -------[script begins]-------

echo "----- PostgreSQL: Configure PostgreSQL to work with Django "
cd $APP_PATH
source bin/activate
pip install --no-cache-dir psycopg2

# -------[script ends]-------
EOF



# http://dba.stackexchange.com/a/27034
# sudo su - postgres
# createuser --interactive -P
# createdb --owner socset db_socset
# psql -U postgres -l
# psql -U postgres -d db_socset
# \dt
# SELECT * FROM reports_data;
# \q
