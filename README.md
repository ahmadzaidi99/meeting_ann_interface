# meeting_ann_interface

To run interface, do the following:

create local copy of the repo

$pip install Flask

for windows, replace export with set, commands below are for linux

$export FLASK_APP=flaskr

$export FLASK_ENV=dev

Only do this the first time. It clears all usernames, passwords, and annotations from SQL database. It also initializes the database.

$flask init-db

To run

$flask run
