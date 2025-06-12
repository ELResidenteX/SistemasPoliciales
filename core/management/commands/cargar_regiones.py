import json
from django.core.management.base import BaseCommand
from core.models import Region, Provincia, Comuna  # Ajusta el nombre de tu app si es distinto

# Aca cargo las regiones para que muestren en el spinner de la app movil
class Command(BaseCommand):
    help = 'Carga regiones, provincias y comunas desde archivo JSON'

    def handle(self, *args, **kwargs):
        with open('core/static/core/json/regiones_chile.json', encoding='utf-8') as f:

            data = json.load(f)

        for region_data in data:
            region, _ = Region.objects.get_or_create(nombre=region_data["region"])

            for provincia_data in region_data["provincias"]:
                provincia, _ = Provincia.objects.get_or_create(
                    nombre=provincia_data["name"],
                    region=region
                )

                for comuna_data in provincia_data["comunas"]:
                    Comuna.objects.get_or_create(
                        nombre=comuna_data["name"],
                        provincia=provincia
                    )

        self.stdout.write(self.style.SUCCESS('✅ Regiones, provincias y comunas cargadas correctamente.'))
