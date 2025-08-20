from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_completo', 'user', 'rut', 'rol','unidad_policial']
    list_filter = ['rol', 'unidad_policial']

    def get_nombre_completo(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    get_nombre_completo.short_description = 'NOMBRE COMPLETO'