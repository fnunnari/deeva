#!/usr/bin/env bash
#
# This sample script dumps a database into a file, composing the filename with the date
# Intended to be used on the server to backup the DB.

dd=`date +%y%m%d-%H%M`
filename=DeevaDevDB-Backup-$dd.sql
echo "Dumping main virtual_characters DB to '$filename' ..."
mysqldump -u deeva -p123 deeva_dev >$filename
echo "Compressing..."
gzip $filename
echo "Done."
