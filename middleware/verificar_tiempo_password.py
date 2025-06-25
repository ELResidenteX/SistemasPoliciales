from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from datetime import timedelta

class ExpulsarSiNoCambioPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.session.get('forzar_cambio_password'):
                inicio_str = request.session.get('inicio_temporal')
                if inicio_str:
                    try:
                        inicio = timezone.datetime.fromisoformat(inicio_str)
                        if timezone.now() - inicio > timedelta(minutes=5):
                            logout(request)
                            request.session.flush()
                            return redirect('login')
                    except Exception:
                        pass
        return self.get_response(request)
