# funcionarios/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # ⚠️ Desactivado porque ahora se requiere rut (obligatorio y único)
        # PerfilUsuario.objects.create(user=instance, rol='funcionario')
        pass  # El perfil se crea manualmente en la vista de registro de usuarios
