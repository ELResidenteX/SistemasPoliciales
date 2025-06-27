from django import forms
from .models import EventoPolicial, Participante, Especie

# 🔷 FORMULARIO DE EVENTO POLICIAL
class EventoPolicialForm(forms.ModelForm):
    class Meta:
        model = EventoPolicial
        exclude = ['numero_evento']
        widgets = {
            'fecha_ocurrencia': forms.DateInput(attrs={'type': 'date'}),
            'hora_ocurrencia': forms.TimeInput(attrs={'type': 'time'}),
            'fecha_denuncia': forms.DateInput(attrs={'type': 'date'}),
            'hora_denuncia': forms.TimeInput(attrs={'type': 'time'}),
            'narracion_hechos': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Describa detalladamente los hechos...'
            }),
            'modo_operandi': forms.Textarea(attrs={'rows': 3}),
            'otros_delitos_observados': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        opcionales = [
            'modo_operandi',
            'otros_delitos_observados',
            'es_violencia_intrafamiliar',
            'victima_mujer_presente_guardia',
            'es_accidente_transito'
        ]
        for field in opcionales:
            self.fields[field].required = False


# 🔶 FORMULARIO DE PARTICIPANTES
class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        exclude = ['evento']  # Se asigna desde la vista
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion'].required = False
        self.fields['observaciones'].required = False
        self.fields['fecha_nacimiento'].required = False

# ✅ NUEVO FORMULARIO DE ESPECIES
class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        exclude = ['evento']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Descripción de la especie sustraída u objeto involucrado'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields:
            self.fields[campo].required = False  # 👈 Todos los campos opcionales


