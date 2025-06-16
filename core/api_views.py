from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from core.models import EventoPolicial
from core.serializers import EventoPolicialAppSerializer, ParticipanteAppSerializer
from rest_framework.permissions import IsAuthenticated

#vista crear evento app
class CrearEventoDesdeAppAPIView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("✅ API activa: método POST recibido")  # Verifica entrada en consola
        serializer = EventoPolicialAppSerializer(data=request.data)

        if serializer.is_valid():
            evento = serializer.save()
            return Response({
                "message": "Evento creado correctamente",
                "evento_id": evento.id,
                "numero_evento": evento.numero_evento
            }, status=status.HTTP_201_CREATED)

        print("❌ Errores en evento:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response(
            {"detail": "Método GET no soportado. Usa POST para crear eventos."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

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
