
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from .forms import EventoPolicialForm, ParticipanteForm, EspecieForm
from .models import EventoPolicial, Participante, Especie, PartePolicial
from datetime import datetime, time
from django.db.models import Q
from django.utils.timezone import now
from django.utils.timezone import make_aware, localtime
from django.contrib import messages
from core.serializers import EventoPolicialAppSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from core.models import Delito 


# ✅ Home
def home(request):
    return render(request, 'core/home.html')

# ✅ Crear nuevo evento policial
def nuevo_evento(request):
    evento = None
    participante_form = None
    especie_form = None
    especie_editando = None
    participante_editando = None

    if request.method == 'POST':
        form = EventoPolicialForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.region = request.POST.get('region', '')
            evento.provincia = request.POST.get('provincia', '')
            evento.comuna = request.POST.get('comuna', '')
            evento.narracion_hechos = request.POST.get('narracion_hechos', '')
            evento.save()
            return HttpResponseRedirect(reverse('nuevo_evento') + f'?evento={evento.numero_evento}')
    else:
        form = EventoPolicialForm()

    numero_evento = request.GET.get('evento')
    especie_id = request.GET.get('especie_id')
    participante_id = request.GET.get('participante_id')

    if numero_evento:
        evento = EventoPolicial.objects.filter(numero_evento=numero_evento).first()
        if evento:
            if participante_id:
                participante_editando = get_object_or_404(Participante, id=participante_id)
                participante_form = ParticipanteForm(instance=participante_editando)
            else:
                participante_form = ParticipanteForm()

            if especie_id:
                especie_editando = get_object_or_404(Especie, id=especie_id)
                especie_form = EspecieForm(instance=especie_editando)
            else:
                especie_form = EspecieForm()

    return render(request, 'core/nuevo_evento.html', {
        'form': form,
        'evento': evento,
        'form_participante': participante_form,
        'form_especie': especie_form,
        'participante_editando': participante_editando,
        'especie_editando': especie_editando,
    })

# ✅ Agregar o actualizar participante
def agregar_participante(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)
    participante_id = request.POST.get('participante_id')
    participante = Participante.objects.filter(id=participante_id).first() if participante_id else None

    if request.method == 'POST':
        form = ParticipanteForm(request.POST, instance=participante)
        if form.is_valid():
            nuevo_participante = form.save(commit=False)
            nuevo_participante.evento = evento

            # 🔽 Verificamos si los campos vinieron vacíos en el POST y usamos los antiguos
            if not request.POST.get('region') and participante:
                nuevo_participante.region = participante.region
            else:
                nuevo_participante.region = request.POST.get('region', '')

            if not request.POST.get('provincia') and participante:
                nuevo_participante.provincia = participante.provincia
            else:
                nuevo_participante.provincia = request.POST.get('provincia', '')

            if not request.POST.get('comuna') and participante:
                nuevo_participante.comuna = participante.comuna
            else:
                nuevo_participante.comuna = request.POST.get('comuna', '')

            nuevo_participante.save()
            return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=participante")

    return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=participante")



# ✅ Editar participante
def editar_participante(request, participante_id):
    participante = get_object_or_404(Participante, id=participante_id)
    evento = participante.evento
    return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=participante&participante_id={participante.id}")

# ✅ Eliminar participante
def eliminar_participante(request, participante_id):
    participante = get_object_or_404(Participante, id=participante_id)
    numero_evento = participante.evento.numero_evento
    participante.delete()
    return redirect(f"{reverse('nuevo_evento')}?evento={numero_evento}&tab=participante")

# ✅ Agregar o actualizar especie
def agregar_especie(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)
    especie_id = request.POST.get('especie_id')
    especie = Especie.objects.filter(id=especie_id).first() if especie_id else None

    if request.method == 'POST':
        form = EspecieForm(request.POST, instance=especie)
        if form.is_valid():
            nueva_especie = form.save(commit=False)
            nueva_especie.evento = evento
            nueva_especie.save()
            return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=especie")
    return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=especie")

# ✅ Editar especie
def editar_especie(request, especie_id):
    especie = get_object_or_404(Especie, id=especie_id)
    evento = especie.evento
    return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=especie&especie_id={especie.id}")

# ✅ Eliminar especie
def eliminar_especie(request, especie_id):
    especie = get_object_or_404(Especie, id=especie_id)
    evento = especie.evento
    especie.delete()
    return redirect(f"{reverse('nuevo_evento')}?evento={evento.numero_evento}&tab=especie")

# ✅ Buscar evento
def buscar_evento(request):
    query = request.GET.get('numero_evento')
    fecha_creacion = request.GET.get('fecha_creacion')
    eventos = EventoPolicial.objects.all()
    no_encontrado = False

    if query:
        eventos = eventos.filter(numero_evento=query)

    if fecha_creacion:
        try:
            fecha_dt = datetime.strptime(fecha_creacion, '%Y-%m-%d').date()
            inicio_dia = datetime.combine(fecha_dt, time.min)
            fin_dia = datetime.combine(fecha_dt, time.max)
            eventos = eventos.filter(creado_en__range=(inicio_dia, fin_dia))
        except ValueError:
            eventos = EventoPolicial.objects.none()
            no_encontrado = True

    if not query and not fecha_creacion:
        eventos = EventoPolicial.objects.none()

    if not eventos.exists():
        no_encontrado = True

    return render(request, 'core/buscar_evento.html', {
        'eventos': eventos,
        'query_num': query or '',
        'query_fecha': fecha_creacion or '',
        'no_encontrado': no_encontrado
    })

# ✅ Enviar evento a validación
def enviar_a_validacion(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)
    evento.estado_validacion = 'en_validacion'
    evento.save()
    return redirect('evento_en_validacion')

# ✅ Vista de evento en validación (corregida)
def evento_en_validacion(request):
    query = request.GET.get('query', '')
    fecha = request.GET.get('fecha', '')
    limpiar = request.GET.get('limpiar', '')

    if limpiar:
        eventos = EventoPolicial.objects.none()
    else:
        eventos = EventoPolicial.objects.filter(estado_validacion='en_validacion')

        if query:
            eventos = eventos.filter(numero_evento__icontains=query)

        if fecha:
            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                fecha_dt = make_aware(datetime.combine(fecha_dt, time.min))
                siguiente_dia = make_aware(datetime.combine(fecha_dt.date(), time.max))
                eventos = eventos.filter(creado_en__range=(fecha_dt, siguiente_dia))
            except ValueError:
                pass

    return render(request, 'core/evento_en_validacion.html', {
        'eventos': eventos,
        'query': query,
        'fecha': fecha,
    })

# ✅ Validación de partes
def validacion_partes(request):
    numero_parte = request.GET.get('parte')
    parte = get_object_or_404(PartePolicial, numero_parte=numero_parte)
    evento = parte.evento
    return render(request, 'core/validacion_partes.html', {
        'parte': parte,
        'evento': evento,
        'participantes': evento.participantes.all(),
        'especies': evento.especies.all()
    })

# ✅ Generar parte policial
def generar_parte_policial(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)

    # Bloqueo para rol funcionario
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'funcionario':
        messages.warning(request, "Opción no autorizada, comuníquese con jefe de unidad.")
        return redirect('evento_en_validacion')

    parte = PartePolicial.objects.filter(evento=evento).first()
    if not parte:
        ultimo_id = PartePolicial.objects.count() + 1
        numero_parte = f"PAR-{ultimo_id:06d}"
        parte = PartePolicial.objects.create(evento=evento, numero_parte=numero_parte)

    return redirect('detalle_parte_policial', parte_id=parte.id)


# VISTA PREVIA EVENTO EN VALIDACION
def vista_previa_evento(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)
    return render(request, 'core/vista_previa_evento.html', {
        'evento': evento,
        'participantes': evento.participantes.all(),
        'especies': evento.especies.all(),
    })

# CARGAR MODALS EDITAR EVENTO
def cargar_modal_edicion_evento(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)
    participantes = evento.participantes.all()
    especies = evento.especies.all()
    return render(request, 'core/modal_editar_evento.html', {
        'evento': evento,
        'participantes': participantes,
        'especies': especies,
    })

# GUARDAR EDICION EVENTO
def guardar_edicion_evento(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)

    if request.method == "POST":
        # Mantener valores previos si los campos vienen vacíos
        region = request.POST.get("region", "")
        provincia = request.POST.get("provincia", "")
        comuna = request.POST.get("comuna", "")

        evento.region = region if region else evento.region
        evento.provincia = provincia if provincia else evento.provincia
        evento.comuna = comuna if comuna else evento.comuna

        evento.direccion = request.POST.get("direccion", "")
        evento.numero = request.POST.get("numero", "")
        evento.fecha_ocurrencia = request.POST.get("fecha_ocurrencia")
        evento.hora_ocurrencia = request.POST.get("hora_ocurrencia")
        evento.save()

        for key in request.POST:
            if key.startswith("participante_id_"):
                pid = key.replace("participante_id_", "")
                participante = get_object_or_404(Participante, id=pid)

                participante.nombres = request.POST.get(f"participante_nombres_{pid}", "")
                participante.apellidos = request.POST.get(f"participante_apellidos_{pid}", "")
                participante.rut = request.POST.get(f"participante_rut_{pid}", "")
                participante.telefono = request.POST.get(f"participante_telefono_{pid}", "")

                # También conservar región/provincia/comuna si no se modifican
                p_region = request.POST.get(f"participante_region_{pid}", "")
                p_provincia = request.POST.get(f"participante_provincia_{pid}", "")
                p_comuna = request.POST.get(f"participante_comuna_{pid}", "")

                participante.region = p_region if p_region else participante.region
                participante.provincia = p_provincia if p_provincia else participante.provincia
                participante.comuna = p_comuna if p_comuna else participante.comuna

                participante.direccion = request.POST.get(f"participante_direccion_{pid}", "")
                participante.numero = request.POST.get(f"participante_numero_{pid}", "")
                participante.save()

        return redirect('evento_en_validacion')

    return redirect('evento_en_validacion')


# ASIGNAR FISCALIA AL PARTE
def asignar_fiscalia_parte(request, parte_id):
    parte = get_object_or_404(PartePolicial, id=parte_id)
    fiscalia = request.POST.get("fiscalia")

    if fiscalia:
        parte.fiscalia = fiscalia
        parte.save()

        evento = parte.evento
        evento.estado_validacion = 'enviado_fiscalia'
        evento.save()

    return redirect('evento_en_validacion')

####VER PARTE POLICIAL

def ver_parte_policial(request, parte_id):
    parte = get_object_or_404(PartePolicial, id=parte_id)
    evento = parte.evento

    return render(request, 'core/vista_previa_evento.html', {
        'parte': parte,
        'evento': evento,
        'participantes': evento.participantes.all(),
        'especies': evento.especies.all(),
    })


#detalle parte policial

def detalle_parte_policial(request, parte_id):
    parte = get_object_or_404(PartePolicial, id=parte_id)
    evento = parte.evento

    return render(request, 'core/detalle_parte_policial.html', {
        'parte': parte,
        'evento': evento,
        'participantes': evento.participantes.all(),
        'especies': evento.especies.all()
    })


#vista previa parte completo luego de generar

def vista_previa_parte_modal(request, parte_id):
    parte = get_object_or_404(PartePolicial, id=parte_id)
    evento = parte.evento
    return render(request, 'core/vistapreviapartecompleto.html', {

        'parte': parte,
        'evento': evento,
        'participantes': evento.participantes.all(),
        'especies': evento.especies.all(),
    })

#Asignar fiscalia al parte

def asignar_fiscalia_parte(request, parte_id):
    parte = get_object_or_404(PartePolicial, id=parte_id)
    fiscalia = request.POST.get("fiscalia")

    if fiscalia:
        parte.fiscalia = fiscalia
        parte.save()

        evento = parte.evento
        evento.estado_validacion = 'enviado_fiscalia'
        evento.save()

        # Mensaje de éxito
        messages.success(request, f"Parte enviado a la fiscalía: {fiscalia}")

    return redirect('vista_busqueda_partes')

#busqueda de partes

def vista_busqueda_partes(request):
    numero_parte = request.GET.get('numero_parte')
    fiscalia = request.GET.get('fiscalia')
    fecha = request.GET.get('fecha')
    limpiar = request.GET.get('limpiar')

    partes = PartePolicial.objects.select_related('evento').filter(evento__estado_validacion='enviado_fiscalia')

    if limpiar:
        partes = PartePolicial.objects.none()
        numero_parte = ''
        fiscalia = ''
        fecha = ''
    else:
        if numero_parte:
            partes = partes.filter(numero_parte__icontains=numero_parte)

        if fiscalia:
            partes = partes.filter(fiscalia__icontains=fiscalia)

        if fecha:
            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                fecha_inicio = make_aware(datetime.combine(fecha_dt, time.min))
                fecha_fin = make_aware(datetime.combine(fecha_dt, time.max))
                partes = partes.filter(creado_en__range=(fecha_inicio, fecha_fin))
            except ValueError:
                partes = PartePolicial.objects.none()

    return render(request, 'core/vista_busqueda_partes.html', {
        'partes': partes,
        'numero_parte': numero_parte or '',
        'fiscalia': fiscalia or '',
        'query_fecha': fecha or '',
    })

#vista autocompletar campos fiscalia busqueda partes


def autocompletar_fiscalia(request):
    query = request.GET.get('q', '').strip().lower()

    if not query:
        return JsonResponse([], safe=False)

    fiscalias = (
        PartePolicial.objects
        .filter(fiscalia__icontains=query)
        .values_list('fiscalia', flat=True)
        .distinct()[:10]
    )

    return JsonResponse(list(fiscalias), safe=False)

#vista redirige editar a evento nuevo

def editar_evento(request, evento_id):
    evento = get_object_or_404(EventoPolicial, id=evento_id)
    participantes = evento.participantes.all()
    especies = evento.especies.all()
    
    form = EventoPolicialForm(instance=evento)

    context = {
        'form': form,
        'evento': evento,
        'participantes': participantes,
        'especies': especies,
        'editando': True  # para mostrar "Actualizar" en botones, por ejemplo
    }
    return render(request, 'core/nuevo_evento.html', context)



#Aca comienzan las vistas relacionadas a la creacion de la app movil

class CrearEventoDesdeAppAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        serializer = EventoPolicialAppSerializer(data=data)

        if serializer.is_valid():
            evento = serializer.save()
            return Response({
                "message": "Evento creado correctamente",
                "evento_id": evento.id,
                "numero_evento": evento.numero_evento
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Vista delitos en hosting temporal para cargar




@staff_member_required  # Solo admin/staff
def cargar_delitos_desde_json(request):
    if request.method == 'POST':
        archivo = request.FILES.get('delitos_json')
        if archivo:
            data = json.load(archivo)
            for item in data:
                Delito.objects.get_or_create(nombre=item['nombre'])
            return render(request, 'core/cargar_delitos_ok.html', {'ok': True})
        else:
            return render(request, 'core/cargar_delitos.html', {'error': 'Archivo no seleccionado'})
    return render(request, 'core/cargar_delitos.html')







