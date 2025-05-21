from django.db import models

# Modelo Infracción al tránsito
class InfraccionTransito(models.Model):
    funcionario_codigo = models.CharField(max_length=50, blank=True, null=True)
    fecha_denuncia = models.DateField(blank=True, null=True)
    hora_denuncia = models.TimeField(blank=True, null=True)
    boleta = models.CharField(max_length=100, blank=True, null=True)

    tipo_infraccion = models.CharField(max_length=500)
    fecha = models.DateField()
    hora = models.TimeField()
    region = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    numero = models.CharField(max_length=20, blank=True, null=True)
    block = models.CharField(max_length=20, blank=True, null=True)
    villa = models.CharField(max_length=100, blank=True, null=True)
    depto = models.CharField(max_length=20, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Infracción {self.id} - {self.tipo_infraccion}"

# Participante de la infracción
class ParticipanteInfraccion(models.Model):
    TIPO_VEHICULO = [
        ('Station Wagon', 'Station Wagon'),
        ('Hatchback', 'Hatchback'),
        ('Sedán', 'Sedán'),
        ('Coupé', 'Coupé'),
        ('Camioneta', 'Camioneta'),
        ('SUV', 'SUV'),
        ('Van', 'Van'),
        ('Minivan', 'Minivan'),
        ('City Car', 'City Car'),
        ('Eléctrico/Híbrido', 'Eléctrico/Híbrido'),
    ]

    COLOR_CHOICES = [
        ('Rojo', 'Rojo'), ('Azul', 'Azul'), ('Negro', 'Negro'), ('Blanco', 'Blanco'),
        ('Gris', 'Gris'), ('Plateado', 'Plateado'), ('Verde', 'Verde'), ('Amarillo', 'Amarillo'),
        ('Naranja', 'Naranja'), ('Café', 'Café'), ('Burdeo', 'Burdeo'), ('Beige', 'Beige'),
        ('Celeste', 'Celeste'), ('Dorado', 'Dorado'), ('Otro', 'Otro'),
    ]

    infraccion = models.ForeignKey('InfraccionTransito', on_delete=models.CASCADE, related_name='participantes')

    tipo_vehiculo = models.CharField(max_length=30, choices=TIPO_VEHICULO)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    placa_patente = models.CharField(max_length=10)
    chasis = models.CharField(max_length=50)
    anio = models.IntegerField()

    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    calidad = models.CharField(max_length=100, blank=True, null=True)

    region = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    comuna = models.CharField(max_length=100, blank=True, null=True)

    nombres = models.CharField(max_length=100, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    rut = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.placa_patente}"

# Parte de infracción con juzgado
class ParteInfraccion(models.Model):
    infraccion = models.OneToOneField(InfraccionTransito, on_delete=models.CASCADE, related_name='parte')
    numero_parte = models.CharField(max_length=20, unique=True)
    juzgado = models.CharField(max_length=255)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Parte {self.numero_parte} - {self.juzgado}"

    def save(self, *args, **kwargs):
        if not self.numero_parte:
            ultimo = ParteInfraccion.objects.order_by('-id').first()
            siguiente_id = (ultimo.id + 1) if ultimo else 1
            self.numero_parte = f"PI-{siguiente_id:06d}"
        super().save(*args, **kwargs)
