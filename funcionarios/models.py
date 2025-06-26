from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#modelo usuarios

#Usuarios proyecto

class PerfilUsuario(models.Model):
    ROLES = [
        ('super_admin', 'Super Admin'),
        ('administrador', 'Administrador'),
        ('oficial_guardia', 'oficial_guardia'),
        ('funcionario', 'Funcionario'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES)
    rut = models.CharField(max_length=12, unique=True)


    # ✅ Campo nuevo para controlar si debe cambiar su contraseña
    cambio_password_obligado = models.BooleanField(default=True)
    fecha_ultimo_cambio = models.DateTimeField(default=timezone.now)  # 🕒 Se inicializa con la fecha de creación

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"