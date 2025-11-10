from rest_framework import serializers
from .models import EventoPolicial, Participante, LugarProcedimiento, TipoLugar
from drf_extra_fields.fields import Base64ImageField
#crear evento policial desde app

class EventoPolicialAppSerializer(serializers.ModelSerializer):
    origen = serializers.CharField(default='app')  # Se fija automáticamente

    # Claves foráneas
    lugar_procedimiento = serializers.PrimaryKeyRelatedField(queryset=LugarProcedimiento.objects.all())
    tipo_lugar = serializers.PrimaryKeyRelatedField(queryset=TipoLugar.objects.all())

    # 🔹 Agregamos unidad_policial (clave foránea)
    unidad_policial = serializers.PrimaryKeyRelatedField(read_only=False, queryset=None)

    # Firmas base64
    firma_funcionario = Base64ImageField(required=False, allow_null=True)
    firma_denunciante = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = EventoPolicial
        fields = [
            'unidad_policial',              # ← agregado
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
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Evitamos errores circulares importando aquí
        from core.models import UnidadPolicial
        self.fields['unidad_policial'].queryset = UnidadPolicial.objects.all()

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
            'fecha_nacimiento', 
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
