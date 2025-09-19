from django.contrib import admin
from .models import LugarProcedimiento, TipoLugar, ConfiguracionSistema
# Register your models here.
admin.site.register(LugarProcedimiento)
admin.site.register(TipoLugar)

class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['unidad_activa']