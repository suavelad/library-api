#!/bin/sh

#if [ "$DEBUG" = 1 ]
#then
#    echo "Waiting for database response..."
#
#    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
#        sleep 0.1
#    done
#
#    echo "Database Started!"
#
#fi

# python manage.py flush --no-input

python manage.py makemigrations \
    users \
    events \
    messaging_service \
    django_q \
    --no-input

python manage.py migrate --no-input

python manage.py collectstatic --no-input --clear

exec "$@"