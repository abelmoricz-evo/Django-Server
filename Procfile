web: python manage.py migrate
web: gunicorn mysite.wsgi
celery: celery worker -A mysite -l info -c 4
