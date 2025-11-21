from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from core.models import EventoPolicial
from core.serializers import EventoPolicialAppSerializer, ParticipanteAppSerializer
from rest_framework.permissions import IsAuthenticated
from core.utils import obtener_unidad_activa

#vista crear evento apP
class CrearEventoDesdeAppAPIView(APIView):
    
    def post(self, request):
        data = request.data.copy()
        serializer = EventoPolicialAppSerializer(data=data)

        if serializer.is_valid():
            # Crear evento y forzar campos base
            evento = serializer.save(
                estado_validacion='en_validacion',
                origen='app'
            )

            # Asignar unidad activa
            unidad = obtener_unidad_activa()
            if unidad:
                evento.unidad_policial = unidad
                evento.save(update_fields=["unidad_policial"])

            # Respuesta completa con los campos que la app necesita
            return Response({
                "message": " Evento creado correctamente",
                "evento_id": evento.id,
                "numero_evento": evento.numero_evento,
                "unidad": unidad.nombre if unidad else "Sin unidad asignada"
            }, status=status.HTTP_201_CREATED)

        # Si falla la validación
        return Response({
            "message": " Error al crear evento",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

#Vista crear participante app
class CrearParticipanteDesdeAppAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        serializer = ParticipanteAppSerializer(data=request.data)
        if serializer.is_valid():
            participante = serializer.save()
            return Response({
                "message": "Participante creado correctamente",
                "id": participante.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Vista protegida login solo vista a usuarios autenticados

class MiVistaProtegida(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Lógica para usuarios autenticados
        return Response({'mensaje': '¡Acceso permitido solo si estás autenticado!'})
