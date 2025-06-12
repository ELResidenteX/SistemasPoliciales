web: gunicorn SistemasPoliciales.wsgi
web: python manage.py migrate && gunicorn SistemasPoliciales.wsgi --log-file -
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn SistemasPoliciales.wsgi --log-file -

