web: python manage.py migrate
gunicorn mysite.wsgi
celery: celery worker -A mysite -l info -c 4
