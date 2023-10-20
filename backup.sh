#!/bin/bash

echo "Start script to backup data to S3"
date

DATE=$(date '+%Y-%m-%d_%H-%M:%S')

cd /home/www/deploy/wordtrack
tar -czvf db.sqlite3.tar.gz data/db.sqlite3 
mv db.sqlite3.tar.gz db.sqlite3_$DATE.tar.gz
s3cmd put db.sqlite3_$DATE.tar.gz s3://ts-wordpress/

rm db.sqlite3_$DATE.tar.gz
