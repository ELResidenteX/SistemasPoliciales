import json
from django.core.management.base import BaseCommand
from core.models import Delito

class Command(BaseCommand):
    help = 'Carga los delitos desde un archivo JSON'

    def handle(self, *args, **kwargs):
        try:
            with open('delitos_chile.json', encoding='utf-8') as f:
                datos = json.load(f)
                count = 0
                for d in datos:
                    nombre = d.get("nombre")
                    if nombre and not Delito.objects.filter(nombre=nombre).exists():
                        Delito.objects.create(nombre=nombre)
                        count += 1
                self.stdout.write(self.style.SUCCESS(f'{count} delitos cargados exitosamente.'))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('⚠️ Archivo delitos_chile.json no encontrado en la raíz del proyecto.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Error al cargar delitos: {e}'))
