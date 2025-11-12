
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from .forms import EventoPolicialForm, ParticipanteForm, EspecieForm
from .models import EventoPolicial, Participante, Especie, PartePolicial
from datetime import datetime, time
from django.db.models import Q, Count
from django.utils.timezone import now
from django.utils.timezone import make_aware, localtime
from django.contrib import messages
from core.serializers import EventoPolicialAppSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
from core.utils import obtener_unidad_activa
from core.geocoding import obtener_lat_lng  
from django.db.models.functions import TruncDate
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from core.models import Delito, UnidadPolicial, Comuna , ConfiguracionSistema
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import os, re
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from core.utils import obtener_unidad_activa
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
            evento.direccion = request.POST.get('direccion', '')
            evento.numero = request.POST.get('numero', '')
            evento.narracion_hechos = request.POST.get('narracion_hechos', '')

            # ✅ Asignar unidad policial activa desde configuración
            unidad = obtener_unidad_activa()
            evento.unidad_policial = unidad

            # ✅ Geocodificación (usando Google Maps)
            direccion_completa = f"{evento.direccion} {evento.numero}, {evento.comuna}, {evento.provincia}, {evento.region}"
            lat, lng = obtener_lat_lng(direccion_completa)

            evento.lat = lat
            evento.lng = lng
            
            # ⚠️ Opción: advertir si falló la geocodificación
            if lat is None or lng is None:
                from django.contrib import messages
                messages.warning(request, "⚠️ No se pudo obtener ubicación geográfica para esta dirección.")

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
            nuevo_participante.fecha_nacimiento = request.POST.get('fecha_nacimiento')


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
    unidad = obtener_unidad_activa()  # ✅ ahora filtramos por unidad
    eventos = EventoPolicial.objects.none()
    no_encontrado = False

    if unidad:
        eventos = EventoPolicial.objects.filter(unidad_policial=unidad)

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
@login_required
def evento_en_validacion(request):
    query = request.GET.get('query', '')
    fecha = request.GET.get('fecha', '')
    limpiar = request.GET.get('limpiar', '')

    perfil = getattr(request.user, "perfilusuario", None)

    # Si el usuario tiene perfil, usamos su unidad
    unidad_usuario = perfil.unidad_policial if perfil and perfil.unidad_policial else None

    # 🔹 Si el usuario no tiene unidad asignada, no mostramos nada
    if not unidad_usuario or limpiar:
        eventos = EventoPolicial.objects.none()
    else:
        eventos = EventoPolicial.objects.filter(
            estado_validacion='en_validacion',
            unidad_policial=unidad_usuario
        )

        # 🔍 Filtros opcionales
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

        # ✅ Solo geocodificar si dirección y número están presentes
        if evento.direccion and evento.numero:
            lat, lng = obtener_lat_lng(
                evento.region, evento.provincia, evento.comuna, evento.direccion, evento.numero
            )
            evento.lat = lat
            evento.lng = lng

        evento.save()

        # Participantes (si vienen en la edición)
        for key in request.POST:
            if key.startswith("participante_id_"):
                pid = key.replace("participante_id_", "")
                participante = get_object_or_404(Participante, id=pid)

                participante.nombres = request.POST.get(f"participante_nombres_{pid}", "")
                participante.apellidos = request.POST.get(f"participante_apellidos_{pid}", "")
                participante.rut = request.POST.get(f"participante_rut_{pid}", "")
                participante.telefono = request.POST.get(f"participante_telefono_{pid}", "")
                participante.fecha_nacimiento = request.POST.get(f"participante_fecha_nacimiento_{pid}", "")

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
    """
    Envía el parte policial a la fiscalía seleccionada,
    generando un PDF adjunto y enviándolo por correo Gmail SMTP.
    """
    parte = get_object_or_404(PartePolicial, id=parte_id)
    fiscalia_nombre = request.POST.get("fiscalia")

    if not fiscalia_nombre:
        messages.error(request, "Debe seleccionar una fiscalía antes de enviar.")
        return redirect('vista_busqueda_partes')

    # Cargar JSON de fiscalías con correos
    ruta_json = os.path.join(settings.BASE_DIR, "core", "static", "core", "json", "fiscalias.json")
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            fiscalias = json.load(f)
    except Exception as e:
        messages.error(request, f"Error al leer fiscalías: {e}")
        return redirect('vista_busqueda_partes')

    # Buscar correo correspondiente
    correo_fiscalia = None
    for f in fiscalias:
        if f.get("nombre") == fiscalia_nombre:
            correo_fiscalia = f.get("correo")
            break

    if not correo_fiscalia:
        messages.error(request, f"No se encontró correo para la fiscalía '{fiscalia_nombre}'.")
        return redirect('vista_busqueda_partes')

    # Generar PDF temporal del parte policial
    evento = parte.evento
    pdf_path = os.path.join(settings.BASE_DIR, f"parte_{parte.numero_parte}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setTitle(f"Parte Policial {parte.numero_parte}")

    c.drawString(100, 800, "PARTE POLICIAL – SISTEMA GEODEPOL")
    c.drawString(100, 780, f"N° Parte: {parte.numero_parte}")
    c.drawString(100, 760, f"N° Evento: {evento.numero_evento}")
    c.drawString(100, 740, f"Unidad Policial: {evento.unidad_policial.nombre if evento.unidad_policial else 'No asignada'}")
    c.drawString(100, 720, f"Delito: {evento.delito_tipificado.nombre if evento.delito_tipificado else 'No tipificado'}")
    c.drawString(100, 700, f"Fecha Ocurrencia: {evento.fecha_ocurrencia}")
    c.drawString(100, 680, f"Hora Ocurrencia: {evento.hora_ocurrencia}")
    c.drawString(100, 660, f"Funcionario Responsable: {evento.funcionaria_codigo or 'N/D'}")
    c.drawString(100, 640, f"RUT Funcionario: {evento.funcionaria_rut or 'N/D'}")
    c.drawString(100, 620, "Narración de los Hechos:")
    text_obj = c.beginText(100, 600)
    text_obj.textLines(evento.narracion_hechos or "Sin descripción disponible.")
    c.drawText(text_obj)
    c.showPage()
    c.save()

    # Enviar correo con PDF adjunto
    try:
        asunto = f"Parte Policial {parte.numero_parte} – {evento.unidad_policial.nombre if evento.unidad_policial else ''}"
        mensaje = f"""
Estimados:

Se remite el Parte Policial {parte.numero_parte}, correspondiente al evento {evento.numero_evento},
emitido por la unidad {evento.unidad_policial.nombre if evento.unidad_policial else 'No asignada'}.

Fiscalía de destino: {fiscalia_nombre}

Atentamente,
Sistema GEODEPOL
        """

        email = EmailMessage(
            subject=asunto,
            body=mensaje,
            from_email=settings.EMAIL_HOST_USER,
            to=[correo_fiscalia],
        )
        email.attach_file(pdf_path)
        email.send()

        # Eliminar PDF temporal
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Actualizar parte y evento
        parte.fiscalia = fiscalia_nombre
        parte.save()
        evento.estado_validacion = 'enviado_fiscalia'
        evento.save()

        messages.success(request, f"✅ Parte enviado correctamente a {fiscalia_nombre} ({correo_fiscalia}).")
        return redirect('vista_busqueda_partes')

    except Exception as e:
        messages.error(request, f"Error al enviar el correo: {e}")
        return redirect('vista_busqueda_partes')

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

from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def asignar_fiscalia_parte(request, parte_id):
    """
    Envía el parte policial a la fiscalía seleccionada,
    generando un PDF adjunto y enviándolo por correo Gmail SMTP.
    """
    parte = get_object_or_404(PartePolicial, id=parte_id)
    fiscalia_nombre = request.POST.get("fiscalia")

    if not fiscalia_nombre:
        messages.error(request, "Debe seleccionar una fiscalía antes de enviar.")
        return redirect('vista_busqueda_partes')

    # --- Leer JSON de fiscalías ---
    ruta_json = os.path.join(settings.BASE_DIR, "core", "static", "core", "json", "fiscalias.json")
    correo_fiscalia = None

    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Buscar fiscalía dentro de todas las regiones del JSON
        for region in data.get("Regiones", []):
            for f_item in region.get("Fiscalias", []):
                nombre = f_item.get("Nombre")
                if nombre == fiscalia_nombre:
                    # Crear correo dinámico (simulado)
                    nombre_simple = (
                        fiscalia_nombre.lower()
                        .replace("fiscalía local de", "")
                        .replace("fiscalía regional de", "")
                        .replace(" ", "")
                        .replace("í", "i")
                        .replace("á", "a")
                        .replace("é", "e")
                        .replace("ó", "o")
                        .replace("ú", "u")
                    )
                    correo_fiscalia = f"fiscalia.{nombre_simple}@gmail.com"
                    break
            if correo_fiscalia:
                break
    except Exception as e:
        messages.error(request, f"Error al procesar fiscalías: {e}")
        return redirect('vista_busqueda_partes')

    if not correo_fiscalia:
        messages.error(request, f"No se encontró correo para la fiscalía '{fiscalia_nombre}'.")
        return redirect('vista_busqueda_partes')

    # --- Generar PDF temporal del parte policial ---
    evento = parte.evento
    pdf_path = os.path.join(settings.BASE_DIR, f"parte_{parte.numero_parte}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setTitle(f"Parte Policial {parte.numero_parte}")

    c.drawString(100, 800, "PARTE POLICIAL – SISTEMA GEODEPOL")
    c.drawString(100, 780, f"N° Parte: {parte.numero_parte}")
    c.drawString(100, 760, f"N° Evento: {evento.numero_evento}")
    c.drawString(100, 740, f"Unidad Policial: {evento.unidad_policial.nombre if evento.unidad_policial else 'No asignada'}")
    c.drawString(100, 720, f"Delito: {evento.delito_tipificado.nombre if evento.delito_tipificado else 'No tipificado'}")
    c.drawString(100, 700, f"Fecha Ocurrencia: {evento.fecha_ocurrencia}")
    c.drawString(100, 680, f"Funcionario Responsable: {evento.funcionaria_codigo or 'N/D'}")
    c.drawString(100, 660, f"RUT Funcionario: {evento.funcionaria_rut or 'N/D'}")
    c.drawString(100, 640, "Narración de los Hechos:")
    text_obj = c.beginText(100, 620)
    text_obj.textLines(evento.narracion_hechos or "Sin descripción disponible.")
    c.drawText(text_obj)
    c.showPage()
    c.save()

    # --- Enviar correo con PDF adjunto ---
    try:
        asunto = f"Parte Policial {parte.numero_parte} – {evento.unidad_policial.nombre if evento.unidad_policial else ''}"
        mensaje = f"""
Estimados:

Se remite el Parte Policial {parte.numero_parte}, correspondiente al evento {evento.numero_evento},
emitido por la unidad {evento.unidad_policial.nombre if evento.unidad_policial else 'No asignada'}.

Fiscalía de destino: {fiscalia_nombre}

Atentamente,
Sistema GEODEPOL
"""

        email = EmailMessage(
            subject=asunto,
            body=mensaje,
            from_email=settings.EMAIL_HOST_USER,
            to=[correo_fiscalia],
        )
        email.attach_file(pdf_path)
        email.send()

        # Limpiar archivo temporal
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Actualizar estado y registrar fiscalía
        parte.fiscalia = fiscalia_nombre
        parte.save()
        evento.estado_validacion = 'enviado_fiscalia'
        evento.save()

        messages.success(request, f"✅ Parte enviado correctamente a {fiscalia_nombre} ({correo_fiscalia}).")
        return redirect('vista_busqueda_partes')

    except Exception as e:
        messages.error(request, f"Error al enviar el correo: {e}")
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

            # ✅ Asignar la unidad activa automáticamente
            unidad = obtener_unidad_activa()
            if unidad:
                evento.unidad_policial = unidad
                evento.save()

            return Response({
                "message": "Evento creado correctamente",
                "evento_id": evento.id,
                "numero_evento": evento.numero_evento,
                "unidad": unidad.nombre if unidad else "Sin unidad asignada"
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


#vista momentanea cargar regiones en app 

def ejecutar_cargar_regiones(request):
    # Opcional: puedes limitar esto SOLO a superusuarios si quieres seguridad
    if not request.user.is_superuser:
        return HttpResponse("No autorizado", status=403)
    call_command('cargar_regiones')
    return HttpResponse("✅ Regiones cargadas correctamente")

#manuales



@login_required
def manuales_usuario(request):
    return render(request, 'core/manuales.html')

@staff_member_required  # Solo superusuarios o staff pueden acceder
def cargar_unidades_policiales(request):
    ruta = os.path.join("data", "cuarteles_normalizados.json")

    if not os.path.exists(ruta):
        messages.error(request, "❌ Archivo JSON no encontrado.")
        return redirect("/admin/")

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
            errores.append(comuna_nombre)

    if errores:
        messages.warning(request, f"Algunas comunas no se encontraron: {', '.join(set(errores))}")
    messages.success(request, f"✅ {cargados} unidades policiales cargadas correctamente.")
    return redirect("/admin/")

#vista solo para cambiar contraseña superadmin

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# ✅ Cambia este valor por algo secreto
TOKEN_SEGURIDAD = "cambiar123"

@csrf_exempt  # Solo mientras se usa — luego elimínala o protégela con login
def reset_superadmin(request):
    if request.method == "POST":
        token = request.POST.get("token")
        username = request.POST.get("username")
        nueva_pass = request.POST.get("password")

        if token != TOKEN_SEGURIDAD:
            return HttpResponse("❌ Token inválido", status=403)

        try:
            usuario = User.objects.get(username=username, is_superuser=True)
            usuario.set_password(nueva_pass)
            usuario.save()
            return HttpResponse(f"✅ Contraseña actualizada para {username}")
        except User.DoesNotExist:
            return HttpResponse("❌ Usuario no encontrado", status=404)

    return HttpResponse("""
        <form method="post">
            <input name="token" placeholder="Token" /><br>
            <input name="username" placeholder="Username" /><br>
            <input name="password" placeholder="Nueva contraseña" type="password" /><br>
            <button type="submit">Resetear contraseña</button>
        </form>
    """)

#elegir unidad activa

@staff_member_required
def cambiar_unidad_activa(request):
    unidades = UnidadPolicial.objects.all()
    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)

    if request.method == 'POST':
        unidad_id = request.POST.get('unidad_policial')
        try:
            nueva_unidad = UnidadPolicial.objects.get(id=unidad_id)
            configuracion.unidad_activa = nueva_unidad
            configuracion.save()
            messages.success(request, f"✅ Unidad activa cambiada a: {nueva_unidad.nombre}")
            return redirect('/admin/')
        except UnidadPolicial.DoesNotExist:
            messages.error(request, "❌ Unidad no válida seleccionada.")

    return render(request, 'core/cambiar_unidad.html', {
        'unidades': unidades,
        'unidad_actual': configuracion.unidad_activa
    })

#vista cambiar unidad desde loginadmin

@csrf_exempt
@require_http_methods(["POST"])
def cambiar_unidad_desde_login(request):
    unidad_id = request.POST.get('unidad_id')
    try:
        unidad = UnidadPolicial.objects.get(id=unidad_id)
        configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
        configuracion.unidad_activa = unidad
        configuracion.save()
    except UnidadPolicial.DoesNotExist:
        pass
    # 🔄 Redirigir de nuevo al login personalizado, no al de Django
    return redirect(reverse('admin_login'))




# temporal


@staff_member_required  # Solo usuarios staff/superadmin
def crear_configuracion_temporal(request):
    if ConfiguracionSistema.objects.exists():
        config = ConfiguracionSistema.objects.first()
        return HttpResponse(f"⚠️ Ya existe una configuración con unidad activa: {config.unidad_activa.nombre}")
    
    unidad = UnidadPolicial.objects.first()
    if unidad:
        ConfiguracionSistema.objects.create(unidad_activa=unidad)
        return HttpResponse(f"✅ Unidad activa seteada a: {unidad.nombre}")
    return HttpResponse("❌ No hay unidades policiales disponibles para asignar")

#Mapa geolocalizacion

@login_required
def vista_mapa_geolocalizacion(request):
    unidad = obtener_unidad_activa()
    comuna_activa = unidad.comuna.nombre if unidad and unidad.comuna else ""
    comunas = Comuna.objects.all().order_by('nombre')
    delitos = Delito.objects.all().order_by('nombre')  # 🔽 para futuros filtros por delito

    context = {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        "comunas": comunas,
        "delitos": delitos,
        "comuna_activa": comuna_activa
    }
    return render(request, "core/estadisticas_geolocalizacion.html", context)


#Separacion por unidad policial, respecto a eventos por unidad policial

def eventos_geolocalizados_json(request):
    unidad = obtener_unidad_activa()

    delito_id = request.GET.get("delito", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "").strip()
    fecha_fin = request.GET.get("fecha_fin", "").strip()

    eventos = EventoPolicial.objects.filter(
        unidad_policial=unidad,
        lat__isnull=False,
        lng__isnull=False
    )

    if delito_id:
        eventos = eventos.filter(delito_tipificado_id=delito_id)

    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio_dt)
        except ValueError:
            pass

    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin_dt)
        except ValueError:
            pass

    # ✅ Enviar datos completos para InfoWindow
    data = [
        {
            "lat": e.lat,
            "lng": e.lng,
            "delito": e.delito_tipificado.nombre if e.delito_tipificado else "Sin tipificar",
            "lugar": e.get_tipo_lugar_display() if hasattr(e, "get_tipo_lugar_display") else "-",
            "direccion": f"{e.direccion or ''} {e.numero or ''}".strip() or "-",
            "unidad": e.unidad_policial.nombre if e.unidad_policial else "No asignada",
        }
        for e in eventos
    ]
    return JsonResponse(data, safe=False)



#Aparicion de linea divisora por comuna

def geojson_comuna_activa(request):
    unidad = obtener_unidad_activa()
    comuna_nombre = unidad.comuna.nombre if unidad and unidad.comuna else ""

    ruta_archivo = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'geojson', 'Comunas_de_Chile.geojson')

    with open(ruta_archivo, encoding="utf-8") as f:
        geojson_data = json.load(f)

              # Filtrar solo la comuna activa en el select
    comuna_filtrada = {
        "type": "FeatureCollection",
        "features": [
            f for f in geojson_data["features"]
            if f["properties"].get("comuna", "").lower() == comuna_nombre.lower()
        ]
    }

    return JsonResponse(comuna_filtrada)

#filtro comunas


def lista_comunas_json(request):
    comunas = Comuna.objects.all().order_by('nombre')
    data = [{"id": c.id, "nombre": c.nombre} for c in comunas]
    return JsonResponse(data, safe=False)

#Filtro comunas desde mapa

def geojson_comuna_por_nombre(request):
    nombre_comuna = (
        request.GET.get("comuna")
        or request.GET.get("nombre")
        or ""
    ).strip().lower()

    ruta_geojson = os.path.join(
        settings.BASE_DIR, "core", "static", "core", "geojson", "Comunas_de_Chile.geojson"
    )

    if not os.path.exists(ruta_geojson):
        return HttpResponse("Archivo GeoJSON no encontrado", status=404)

    with open(ruta_geojson, encoding="utf-8") as f:
        geojson_data = json.load(f)

    # claves posibles
    posibles = ["comuna", "Comuna", "NOM_COM", "NOM_COMUNA", "name", "NOMBRE"]

    def nombre_prop(properties):
        for k in posibles:
            if k in properties and isinstance(properties[k], str):
                return properties[k].strip().lower()
        return ""

    features_filtradas = [
        f for f in geojson_data.get("features", [])
        if nombre_prop(f.get("properties", {})) == nombre_comuna
    ]

    if not features_filtradas:
        print(f"[DEBUG] ❌ No se encontró {nombre_comuna} en el GeoJSON")

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features_filtradas
    })


#eventos filtrados por comuna

from datetime import datetime

def eventos_por_comuna_json(request):
    nombre = request.GET.get("comuna", "").strip()
    delito_id = request.GET.get("delito")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.filter(
        Q(comuna__iregex=rf'^{re.escape(nombre)}$'),
        lat__isnull=False,
        lng__isnull=False
    )

    if delito_id:
        eventos = eventos.filter(delito_tipificado__id=delito_id)

    if fecha_inicio:
        eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)

    if fecha_fin:
        eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    data = []
    for e in eventos:
        data.append({
            "lat": e.lat,
            "lng": e.lng,
            "delito": e.delito_tipificado.nombre if e.delito_tipificado else "Sin tipificar",
            "lugar": e.get_tipo_lugar_display(),
            "direccion": f"{e.direccion} {e.numero}",
            "unidad": str(e.unidad_policial) if e.unidad_policial else "N/D"
        })

    return JsonResponse(data, safe=False)


#graficos delitos   

# 🔹 1. Delitos por tipo
def api_estadisticas_por_delito(request):
    unidad = obtener_unidad_activa()
    comuna = request.GET.get("comuna", "").strip()
    delito_id = request.GET.get("delito", "")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.all()

    # 🔸 Filtrar por unidad activa si existe
    if unidad:
        eventos = eventos.filter(unidad_policial=unidad)
    if comuna:
        eventos = eventos.filter(comuna__iexact=comuna)
    if delito_id:
        eventos = eventos.filter(delito_tipificado__id=delito_id)
    if fecha_inicio:
        eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)
    if fecha_fin:
        eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    conteo = (
        eventos.values("delito_tipificado__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    data = [
        {"nombre": c["delito_tipificado__nombre"] or "Sin tipificar", "total": c["total"]}
        for c in conteo
    ]
    return JsonResponse(data, safe=False)


# 🔹 2. Evolución temporal (gráfico de línea)
def api_eventos_tiempo(request):
    unidad = obtener_unidad_activa()
    comuna = request.GET.get("comuna", "")
    delito_id = request.GET.get("delito", "")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.all()
    if unidad:
        eventos = eventos.filter(unidad_policial=unidad)
    if comuna:
        eventos = eventos.filter(comuna__iexact=comuna)
    if delito_id:
        eventos = eventos.filter(delito_tipificado_id=delito_id)
    if fecha_inicio:
        eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)
    if fecha_fin:
        eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    # 🔸 Agrupar por fecha (día)
    eventos = (
        eventos.annotate(fecha=TruncDate("fecha_ocurrencia"))
        .values("fecha")
        .annotate(total=Count("id"))
        .order_by("fecha")
    )

    data = {
        "fechas": [e["fecha"].strftime("%Y-%m-%d") for e in eventos if e["fecha"]],
        "valores": [e["total"] for e in eventos if e["fecha"]],
    }
    return JsonResponse(data)


# 🔹 3. Top 5 unidades policiales
def api_top_unidades(request):
    unidad = obtener_unidad_activa()
    comuna = request.GET.get("comuna", "")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.all()
    if unidad:
        eventos = eventos.filter(unidad_policial=unidad)
    if comuna:
        eventos = eventos.filter(comuna__iexact=comuna)
    if fecha_inicio:
        eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)
    if fecha_fin:
        eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    unidades = (
        eventos.values("unidad_policial__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    data = [
        {"nombre_unidad": u["unidad_policial__nombre"] or "No definida", "total": u["total"]}
        for u in unidades
    ]
    return JsonResponse(data, safe=False)


# 🔹 4. Ranking de comunas más conflictivas
def api_top_comunas(request):
    unidad = obtener_unidad_activa()
    delito_id = request.GET.get("delito", "")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.all()
    if unidad:
        eventos = eventos.filter(unidad_policial=unidad)
    if delito_id:
        eventos = eventos.filter(delito_tipificado_id=delito_id)
    if fecha_inicio:
        eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)
    if fecha_fin:
        eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    comunas = (
        eventos.values("comuna")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    data = [
        {"nombre_comuna": c["comuna"] or "No definida", "total": c["total"]}
        for c in comunas
    ]
    return JsonResponse(data, safe=False)


# 🔹 5. Porcentaje de delitos críticos
def api_porcentaje_delitos_criticos(request):
    unidad = obtener_unidad_activa()
    delitos_criticos = ["Robo con violencia", "Homicidio", "Violación", "Lesiones graves"]

    eventos = EventoPolicial.objects.all()
    if unidad:
        eventos = eventos.filter(unidad_policial=unidad)

    total = eventos.count()
    criticos = eventos.filter(delito_tipificado__nombre__in=delitos_criticos).count()
    porcentaje = round((criticos / total * 100), 2) if total else 0

    data = {
        "total_eventos": total,
        "delitos_criticos": criticos,
        "porcentaje": porcentaje,
    }
    return JsonResponse(data)

# 🔹 6. Eventos por hora del día (para gráfico de barras o radar)
def api_eventos_hora_dia(request):
    """
    Devuelve la cantidad de delitos agrupados por hora del día (0 a 23).
    Filtra por unidad activa, comuna, delito y rango de fechas.
    """
    unidad = obtener_unidad_activa()
    comuna = request.GET.get("comuna", "").strip()
    delito_id = request.GET.get("delito", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.all()

    # Filtros dinámicos
    if unidad:
        eventos = eventos.filter(unidad_policial=unidad)
    if comuna:
        eventos = eventos.filter(comuna__iexact=comuna)
    if delito_id:
        eventos = eventos.filter(delito_tipificado_id=delito_id)
    if fecha_inicio:
        eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)
    if fecha_fin:
        eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    # Agrupar por hora (campo hora_ocurrencia)
    conteo_por_hora = (
        eventos.values("hora_ocurrencia")
        .annotate(total=Count("id"))
        .order_by("hora_ocurrencia")
    )

    # Convertir a formato JSON (horas 00 a 23)
    horas = list(range(0, 24))
    totales = []
    for h in horas:
        count = next(
            (c["total"] for c in conteo_por_hora if c["hora_ocurrencia"] and c["hora_ocurrencia"].hour == h),
            0
        )
        totales.append(count)

    data = {
        "horas": [f"{h:02d}:00" for h in horas],
        "valores": totales,
    }
    return JsonResponse(data)


#estadisticas noche dia

def api_eventos_dia_vs_noche(request):
    unidad = obtener_unidad_activa()
    comuna = request.GET.get("comuna", "")
    delito_id = request.GET.get("delito", "")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    eventos = EventoPolicial.objects.all()
    if unidad: eventos = eventos.filter(unidad_policial=unidad)
    if comuna: eventos = eventos.filter(comuna__iexact=comuna)
    if delito_id: eventos = eventos.filter(delito_tipificado_id=delito_id)
    if fecha_inicio: eventos = eventos.filter(fecha_ocurrencia__gte=fecha_inicio)
    if fecha_fin: eventos = eventos.filter(fecha_ocurrencia__lte=fecha_fin)

    dia = eventos.filter(hora_ocurrencia__hour__gte=6, hora_ocurrencia__hour__lt=18).count()
    noche = eventos.exclude(hora_ocurrencia__hour__gte=6, hora_ocurrencia__hour__lt=18).count()

    return JsonResponse({"dia": dia, "noche": noche})

#tendencia ensual

def api_tendencia_mensual(request):
    unidad = obtener_unidad_activa()
    eventos = EventoPolicial.objects.all()
    if unidad: eventos = eventos.filter(unidad_policial=unidad)

    data = (
        eventos.annotate(mes=TruncMonth("fecha_ocurrencia"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )
    labels = [d["mes"].strftime("%b %Y") for d in data]
    valores = [d["total"] for d in data]
    return JsonResponse({"labels": labels, "valores": valores})

#estadisticas mes


def api_top_delitos_mes_actual(request):
    hoy = timezone.now()
    eventos = EventoPolicial.objects.filter(fecha_ocurrencia__month=hoy.month)
    data = (
        eventos.values("delito_tipificado__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    return JsonResponse({
        "labels": [d["delito_tipificado__nombre"] for d in data],
        "valores": [d["total"] for d in data]
    })

#OPCION DE ELIMINAR EVENTOS DESDE VALIDACION EVENTOS


@login_required
def eliminar_evento(request, evento_id):
    """
    Elimina un evento policial (solo roles: super_admin o administrador).
    """
    perfil = request.user.perfilusuario

    if perfil.rol not in ['super_admin', 'administrador']:
        return HttpResponseForbidden("No tienes permisos para eliminar eventos.")

    evento = EventoPolicial.objects.filter(id=evento_id).first()
    if not evento:
        messages.error(request, "❌ El evento no existe o ya fue eliminado.")
        return redirect('evento_en_validacion')

    # Eliminar
    evento.delete()
    messages.success(request, f"✅ Evento {evento.numero_evento} eliminado correctamente.")
    return redirect('evento_en_validacion')


