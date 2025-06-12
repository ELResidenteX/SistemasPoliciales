#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemasPoliciales.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

# En tu archivo manage.py agrega al final, temporalmente:
# Agrega este bloque al final de wsgi.py SOLO TEMPORALMENTE



if os.environ.get('CREATESUPERUSER_ON_STARTUP', 'False') == 'True':
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin_principal", "admin@email.com", "123456")
            print("Superusuario admin creado automáticamente.")
        else:
            print("Superusuario admin ya existe.")
    except Exception as e:
        print(f"Error creando superusuario: {e}")


