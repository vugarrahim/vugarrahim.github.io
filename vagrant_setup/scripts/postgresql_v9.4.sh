#!/bin/bash

. /vagrant/vagrant_setup/config.txt


echo "----- PostgreSQL: Dump"
# http://www.postgresql.org/docs/9.4/static/backup-dump.html
sudo su - postgres << EOF
# -------[script begins]-------
psql -U postgres -l
# pwd
mkdir -p ./backups
# now=$(date +"%d_%m_%Y")
pg_dumpall > ./backups/old_.db

# -------[script ends]-------
EOF



# Upgrade PostgreSQL 9.3 to 9.4 on Ubuntu 14.04
# ref: https://medium.com/@tk512/upgrading-postgresql-from-9-3-to-9-4-on-ubuntu-14-04-lts-2b4ddcd26535#.4i136rihe
echo "----- PostgreSQL: stop the current database..."
sudo /etc/init.d/postgresql stop

echo "----- PostgreSQL: Create a new list..."
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget -q -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

echo "----- PostgreSQL: download 9.4 "
sudo apt-get update
sudo apt-get install -y postgresql-9.4

sudo pg_lsclusters

sudo pg_dropcluster --stop 9.4 main
sudo /etc/init.d/postgresql start

echo "----- PostgreSQL: Upgrade to 9.4 "
sudo pg_upgradecluster 9.3 main
sudo pg_dropcluster 9.3 main
sudo pg_lsclusters



echo "----- PostgreSQL: Restore"
# http://www.postgresql.org/docs/9.4/static/backup-dump.html
sudo su - postgres << EOF
# -------[script begins]-------
psql -U postgres -l
# psql -f ./backups/old.db postgres
# -------[script ends]-------
EOF



# Backup database
# . /vagrant/vagrant_setup/config.txt
# now=$(date +"%d_%m_%Y")
# pg_dump -f ./backups/local_dump_$now.sql -Ox $APP_DB_NAME

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# *  Restoring Django database
#
#   1) Include project variables
#   2) Drop existing database if you want overwrite
#   3) Drop the User, database assosiated with
#   4) Create User
#   5) Create Database but dont `migrate` yet
#   6) Restore the database from dump file
#   7) Create proper rules for the restored tables
#
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


# 1) . /vagrant/vagrant_setup/config.txt
# 2) dropdb $APP_DB_NAME
# 3) psql -c " DROP USER $APP_DB_USER;"
# 4) psql -c " CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASSWORD'; "
# 5) createdb --owner $APP_DB_USER $APP_DB_NAME
# 6) psql $APP_DB_NAME -f ./backups/dump_24aug.sql
# 7) for tbl in `psql -qAt -c "select tablename from pg_tables where schemaname = 'public';" $APP_DB_NAME` ; do  psql -c "alter table \"$tbl\" owner to $APP_DB_USER" $APP_DB_NAME ; done
#    for tbl in `psql -qAt -c "select sequence_name from information_schema.sequences where sequence_schema = 'public';" $APP_DB_NAME` ; do  psql -c "alter table \"$tbl\" owner to $APP_DB_USER" $APP_DB_NAME ; done
#    for tbl in `psql -qAt -c "select table_name from information_schema.views where table_schema = 'public';" $APP_DB_NAME` ; do  psql -c "alter table \"$tbl\" owner to $APP_DB_USER" $APP_DB_NAME ; done
