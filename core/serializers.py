from rest_framework import serializers
from .models import EventoPolicial, Participante, LugarProcedimiento, TipoLugar
from drf_extra_fields.fields import Base64ImageField
#crear evento policial desde app

class EventoPolicialAppSerializer(serializers.ModelSerializer):
    origen = serializers.CharField(default='app')  # Se fija automáticamente

    # Claves foráneas como ID
    lugar_procedimiento = serializers.PrimaryKeyRelatedField(queryset=LugarProcedimiento.objects.all())
    tipo_lugar = serializers.PrimaryKeyRelatedField(queryset=TipoLugar.objects.all())

    # Firmas como base64
    firma_funcionario = Base64ImageField(required=False, allow_null=True)
    firma_denunciante = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = EventoPolicial
        fields = [
            'lugar_procedimiento',
            'fecha_ocurrencia',
            'hora_ocurrencia',
            'fecha_denuncia',
            'hora_denuncia',
            'funcionaria_codigo',
            'funcionaria_rut',
            'modo_operandi',
            'delito_tipificado',
            'otros_delitos_observados',
            'es_violencia_intrafamiliar',
            'victima_mujer_presente_guardia',
            'es_accidente_transito',
            'tipo_lugar',
            'region',
            'provincia',
            'comuna',
            'direccion',
            'numero',
            'block',
            'villa',
            'depto',
            'km',
            'interseccion',
            'narracion_hechos',
            'firma_funcionario',
            'firma_denunciante',
            'origen',
            # NOTA: No incluyas 'estado_validacion' aquí, salvo que quieras devolverlo a la app.
        ]

    def create(self, validated_data):
        # Fuerza el estado a 'en_validacion' cada vez que se crea por la app
        validated_data['estado_validacion'] = 'en_validacion'
        return super().create(validated_data)

#participantes app

class ParticipanteAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participante
        fields = [
            'evento',
            'nombres',
            'apellidos',
            'rut',
            'edad',
            'sexo',
            'nacionalidad',
            'calidad',
            'region',
            'provincia',
            'comuna',
            'direccion',
            'numero_calle',
            'telefono',
            'observaciones',
        ]

#Lugar Procedimiento

class LugarProcedimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LugarProcedimiento
        fields = ['id', 'nombre']

#Tipo Lugar

class TipoLugarSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoLugar
        fields = ['id', 'nombre']
