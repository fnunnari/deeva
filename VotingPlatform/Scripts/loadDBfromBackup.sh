#!/bin/sh

#
# This script takes as parameters the filename of a database dump, and loads it into the local mysql
# To be used to load a DB backed up from the server into the localhost.

if [ $# -eq 0 ]
  then
    echo "Usage: loadDevDBfromBackup.sh <dbdump>.sql.gz"
    exit 10
fi

DBNAME=deeva_dev

echo "Importing database from '$1' ..."

echo "Cancelling the old DB $DBNAME..."
echo "drop schema $DBNAME" |  mysql -u root -p123

echo "Recreating the development DB $DBNAME..."
echo "create schema $DBNAME" |  mysql -u root -p123

echo "Importing the DB into mysql as '$DBNAME'..."
gunzip -c $1 | mysql -u deeva -p123 $DBNAME

echo "Done."
