python manage.py collectstatic && gunicorn --workers 2 transync_server.wsgi