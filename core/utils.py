from .models import ConfiguracionSistema

def obtener_unidad_activa():
    config = ConfiguracionSistema.objects.first()
    return config.unidad_activa if config else None
