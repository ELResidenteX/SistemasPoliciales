
from django import forms
from .models import ParticipanteInfraccion

#infracciones form participantes

class ParticipanteInfraccionForm(forms.ModelForm):
    class Meta:
        model = ParticipanteInfraccion
        fields = [
            'denunciado', 'tipo_automovil', 'color', 'placa_patente',
            'chasis', 'anio', 'nombres', 'apellidos', 'rut',
            'fecha_nacimiento', 'region', 'provincia', 'comuna', 'direccion'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
