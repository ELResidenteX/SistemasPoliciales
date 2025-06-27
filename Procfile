release: python manage.py migrate
web: python manage.py collectstatic --noinput && gunicorn SistemasPoliciales.wsgi --log-file -



