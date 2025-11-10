from core.models import ConfiguracionSistema, UnidadPolicial
from django.conf import settings

from core.models import ConfiguracionSistema, UnidadPolicial
from django.conf import settings

def unidad_policial_context(request):
    # 🔹 Datos del sistema (unidad activa general)
    try:
        config = ConfiguracionSistema.objects.first()
        unidad_id = config.unidad_activa.id if config and config.unidad_activa else None
        unidad_nombre = config.unidad_activa.nombre if config and config.unidad_activa else "No asignada"
    except:
        unidad_id = None
        unidad_nombre = "No asignada"

    # 🔹 Datos del usuario autenticado
    unidad_usuario = None
    nombre_usuario = None
    rol_usuario = None

    if request.user.is_authenticated and hasattr(request.user, "perfilusuario"):
        perfil = request.user.perfilusuario
        unidad_usuario = perfil.unidad_policial.nombre if perfil.unidad_policial else "Sin unidad asignada"
        nombre_usuario = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        rol_usuario = perfil.get_rol_display() if hasattr(perfil, "get_rol_display") else perfil.rol

    return {
        # Datos del sistema
        "unidad_actual_id": unidad_id,
        "unidad_actual_nombre": unidad_nombre,
        "unidades": UnidadPolicial.objects.all(),

        # Datos del usuario autenticado
        "nombre_usuario": nombre_usuario,
        "rol_usuario": rol_usuario,
        "unidad_usuario": unidad_usuario,
    }

def google_maps_key(request):
    return {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
    }


def google_maps_key(request):
    return {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }