from django.db import models

# 🔹 Modelo de Delito
class Delito(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre
    
#modelo select regiones para app movil

class Region(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='provincias')

    class Meta:
        unique_together = ('nombre', 'region')

    def __str__(self):
        return f"{self.nombre} ({self.region.nombre})"

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='comunas')

    class Meta:
        unique_together = ('nombre', 'provincia')

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"
    
#modelo unidades policiales por comuna

class UnidadPolicial(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, related_name='unidades_policiales')

    def __str__(self):
        return self.nombre


# 🔹 Modelo de EventoPolicial
class EventoPolicial(models.Model):
    OPCIONES_LUGAR = [
        ('via_publica', 'Vía pública'),
        ('cuartel_policial', 'Cuartel policial'),
        ('domicilio', 'Domicilio particular'),
        ('empresa', 'Empresa'),
        ('otro', 'Otro'),
    ]

    numero_evento = models.CharField(max_length=20, unique=True, blank=True, null=True)

    lugar_procedimiento = models.CharField(max_length=50, choices=OPCIONES_LUGAR)
    fecha_ocurrencia = models.DateField()
    hora_ocurrencia = models.TimeField()
    fecha_denuncia = models.DateField()
    hora_denuncia = models.TimeField()
    funcionaria_codigo = models.CharField("Funcionario código", max_length=50)
    funcionaria_rut = models.CharField("Funcionario rut", max_length=20)

    modo_operandi = models.TextField(blank=True, null=True)

    delito_tipificado = models.ForeignKey('Delito', on_delete=models.SET_NULL, null=True, blank=True)
    otros_delitos_observados = models.TextField(blank=True, null=True)
    es_violencia_intrafamiliar = models.BooleanField(default=False)
    victima_mujer_presente_guardia = models.BooleanField(default=False)
    es_accidente_transito = models.BooleanField(default=False)

    tipo_lugar = models.CharField(max_length=50, choices=OPCIONES_LUGAR)

    region = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)

    direccion = models.CharField(max_length=255)
    numero = models.CharField(max_length=10, blank=True)
    block = models.CharField(max_length=10, blank=True)
    villa = models.CharField(max_length=100, blank=True)
    depto = models.CharField(max_length=10, blank=True)
    km = models.CharField(max_length=10, blank=True)
    interseccion = models.CharField(max_length=255, blank=True)

    narracion_hechos = models.TextField()

    # 🔹 NUEVOS CAMPOS PARA INTEGRAR APP MÓVIL
    firma_funcionario = models.ImageField(upload_to="firmas/", null=True, blank=True)
    firma_denunciante = models.ImageField(upload_to="firmas/", null=True, blank=True)

    origen = models.CharField(
        max_length=10,
        choices=[('web', 'Web'), ('app', 'App')],
        default='web'
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    estado_validacion = models.CharField(
        max_length=50,
        choices=[
            ('en_edicion', 'En edición'),
            ('en_validacion', 'En validación'),
            ('parte_generado', 'Parte generado'),
            ('enviado_fiscalia', 'Enviado a Fiscalía')
        ],
        default='en_edicion'
    )

    def __str__(self):
        return f"Evento #{self.numero_evento or self.id} - {self.fecha_ocurrencia}"

    def save(self, *args, **kwargs):
        if not self.numero_evento:
            last_id = EventoPolicial.objects.count() + 1
            self.numero_evento = f"EVT-{last_id:06d}"
        super().save(*args, **kwargs)

# 🔹 Modelo de Participante
class Participante(models.Model):
    evento = models.ForeignKey(EventoPolicial, on_delete=models.CASCADE, related_name='participantes')
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    rut = models.CharField(max_length=12)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    edad = models.PositiveIntegerField()
    sexo = models.CharField(max_length=10, choices=[
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro')
    ])
    nacionalidad = models.CharField(max_length=50)
    calidad = models.CharField(max_length=50, choices=[
        ('victima', 'Víctima'),
        ('imputado', 'Imputado'),
        ('testigo', 'Testigo'),
        ('denunciante_victima', 'Denunciante/Víctima'), 
        ('otro', 'Otro')
    ])
    region = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    numero_calle = models.CharField(max_length=10, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.calidad})"

# 🔹 Modelo de Especie
class Especie(models.Model):
    evento = models.ForeignKey(EventoPolicial, on_delete=models.CASCADE, related_name='especies')
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    avaluo_estimado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} (x{self.cantidad})"

# 🔹 Modelo de Parte Policial
class PartePolicial(models.Model):
    evento = models.OneToOneField('EventoPolicial', on_delete=models.CASCADE, related_name='parte_policial')
    numero_parte = models.CharField(max_length=20, unique=True, blank=True, null=True)
    fiscalia = models.CharField(max_length=150, blank=True, null=True)  # Nueva fiscalía seleccionada
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Parte #{self.numero_parte} (Evento: {self.evento.numero_evento})"

    def save(self, *args, **kwargs):
        if not self.numero_parte:
            last_id = PartePolicial.objects.count() + 1
            self.numero_parte = f"PAR-{last_id:06d}"
        super().save(*args, **kwargs)



# Modelo para la app movil

#Lugar de procedimiento

class LugarProcedimiento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
#tipo Lugar delito o suceso

class TipoLugar(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre






