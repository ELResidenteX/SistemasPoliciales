from core.models import ConfiguracionSistema, UnidadPolicial

def unidad_policial_context(request):
    try:
        config = ConfiguracionSistema.objects.first()
        unidad_id = config.unidad_activa.id if config and config.unidad_activa else None
        unidad_nombre = config.unidad_activa.nombre if config and config.unidad_activa else "No asignada"
    except:
        unidad_id = None
        unidad_nombre = "No asignada"

    return {
        "unidad_actual_id": unidad_id,
        "unidad_actual_nombre": unidad_nombre,
        "unidades": UnidadPolicial.objects.all()
    }
