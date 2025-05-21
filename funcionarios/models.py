from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"