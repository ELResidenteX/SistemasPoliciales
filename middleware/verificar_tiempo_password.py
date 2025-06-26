# middleware/verificar_tiempo_password.py

from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from datetime import timedelta

class ExpulsarSiNoCambioPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            perfil = getattr(request.user, 'perfilusuario', None)

            # 🔐 1. Si debe cambiar contraseña (forzado), dar máximo 5 minutos
            forzar_cambio = perfil.cambio_password_obligado if perfil else False
            inicio_str = request.session.get('inicio_temporal')

            if forzar_cambio and inicio_str:
                try:
                    inicio = timezone.datetime.fromisoformat(inicio_str)
                    if timezone.now() - inicio > timedelta(minutes=5):
                        logout(request)
                        request.session.flush()
                        return redirect('login')
                except Exception:
                    pass  # No interrumpe la app si hay error con formato

            # 🕒 2. Si ya no está obligado, verificar vencimiento de 30 días
            if perfil and not perfil.cambio_password_obligado and perfil.fecha_ultimo_cambio:
                if timezone.now() - perfil.fecha_ultimo_cambio > timedelta(days=30):
                    perfil.cambio_password_obligado = True
                    perfil.save()
                    request.session['inicio_temporal'] = timezone.now().isoformat()
                    return redirect('forzar_cambio_password')

            # 🔁 3. Redirigir si debe cambiar contraseña y está fuera de la ruta correcta
            if forzar_cambio and not request.path.startswith('/funcionarios/forzar-cambio-password/'):
                return redirect('forzar_cambio_password')

        return self.get_response(request)


