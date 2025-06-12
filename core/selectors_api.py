from .serializers import LugarProcedimientoSerializer, TipoLugarSerializer
from rest_framework.decorators import api_view
from .models import Region, Provincia, Comuna, Delito, LugarProcedimiento, TipoLugar
from django.http import JsonResponse
from rest_framework.response import Response

#ENDPOINT SELECT REGIONES

# 🔹 Lista de regiones
def api_regiones(request):
    regiones = Region.objects.all().values('id', 'nombre')
    return JsonResponse(list(regiones), safe=False)

# 🔹 Lista de provincias por región
def api_provincias(request):
    region_id = request.GET.get('region_id')
    provincias = Provincia.objects.filter(region_id=region_id).values('id', 'nombre')
    return JsonResponse(list(provincias), safe=False)

# 🔹 Lista de comunas por provincia
def api_comunas(request):
    provincia_id = request.GET.get('provincia_id')
    comunas = Comuna.objects.filter(provincia_id=provincia_id).values('id', 'nombre')
    return JsonResponse(list(comunas), safe=False)

# Lista de delitos

def api_delitos(request):
    delitos = Delito.objects.all().values('id', 'nombre')
    return JsonResponse(list(delitos), safe=False)

#Lista Lugar procedimiento

@api_view(['GET'])
def listar_lugares_procedimiento(request):
    lugares = LugarProcedimiento.objects.filter(activo=True).order_by('nombre')
    serializer = LugarProcedimientoSerializer(lugares, many=True)
    return Response(serializer.data)

#Lista tipo lugar

@api_view(['GET'])
def listar_tipos_lugar(request):
    tipos = TipoLugar.objects.filter(activo=True).order_by('nombre')
    serializer = TipoLugarSerializer(tipos, many=True)
    return Response(serializer.data)
