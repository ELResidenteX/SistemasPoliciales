from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from datetime import timedelta

class ExpulsarSiNoCambioPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            forzar_cambio = request.session.get('forzar_cambio_password')
            inicio_str = request.session.get('inicio_temporal')

            # ✅ Expulsar si han pasado más de 5 minutos sin cambiar
            if forzar_cambio and inicio_str:
                try:
                    inicio = timezone.datetime.fromisoformat(inicio_str)
                    if timezone.now() - inicio > timedelta(minutes=5):
                        logout(request)
                        request.session.flush()
                        return redirect('login')
                except Exception:
                    pass

            # ✅ Forzar cambio si han pasado más de 30 días desde el último
            ultima_str = request.session.get('ultima_password_cambio')
            if ultima_str and not forzar_cambio:
                try:
                    ultima = timezone.datetime.fromisoformat(ultima_str)
                    if timezone.now() - ultima > timedelta(days=30):
                        request.session['forzar_cambio_password'] = True
                        request.session['inicio_temporal'] = timezone.now().isoformat()
                        if not request.path.startswith('/funcionarios/forzar-cambio-password/'):
                            return redirect('forzar_cambio_password')
                except Exception:
                    pass

            # ✅ Redirigir si está pendiente de cambio y no está en esa ruta
            if forzar_cambio and not request.path.startswith('/funcionarios/forzar-cambio-password/'):
                return redirect('forzar_cambio_password')

        return self.get_response(request)

