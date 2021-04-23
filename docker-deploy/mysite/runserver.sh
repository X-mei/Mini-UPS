#!/bin/bash
sleep 5
# python3 manage.py makemigrations
# python3 manage.py migrate
while [ "1"=="1" ]
do
    python3 manage.py runserver 0.0.0.0:8000 --noreload
    sleep 1
done
