import json
import os
from django.core.management.base import BaseCommand
from core.models import UnidadPolicial, Comuna

class Command(BaseCommand):
    help = 'Carga unidades policiales desde un archivo JSON'

    def handle(self, *args, **kwargs):
        ruta = os.path.join("data", "cuarteles_normalizados.json")

        if not os.path.exists(ruta):
            self.stdout.write(self.style.ERROR("❌ Archivo JSON no encontrado en /data"))
            return

        with open(ruta, "r", encoding="utf-8") as f:
            cuarteles = json.load(f)

        cargados = 0
        errores = []

        for item in cuarteles:
            nombre = item["nombre"].strip()
            comuna_nombre = item["comuna"].strip()

            try:
                comuna = Comuna.objects.get(nombre__iexact=comuna_nombre)
                unidad, creado = UnidadPolicial.objects.get_or_create(
                    nombre=nombre,
                    comuna=comuna
                )
                if creado:
                    cargados += 1
            except Comuna.DoesNotExist:
                errores.append(f"❌ Comuna no encontrada: {comuna_nombre}")

        self.stdout.write(self.style.SUCCESS(f"✅ {cargados} unidades policiales cargadas."))

        if errores:
            self.stdout.write(self.style.WARNING(f"\n🚫 {len(errores)} errores encontrados:"))
            for e in errores:
                self.stdout.write(self.style.WARNING(f"- {e}"))

