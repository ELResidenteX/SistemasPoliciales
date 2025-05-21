from django.shortcuts import render, redirect, get_object_or_404
from .models import InfraccionTransito, ParticipanteInfraccion, ParteInfraccion
from django.utils.timezone import now
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime
from django.db.models import Q
from django.utils.timezone import localtime

# Vista para crear una nueva infracción
def nueva_infraccion(request):
    if request.method == 'POST':
        tipos_infraccion = request.POST.getlist('tipos_infraccion[]')
        tipo_infraccion = ', '.join(tipos_infraccion) if tipos_infraccion else None

        if not tipo_infraccion:
            infraccion_id = request.GET.get('infraccion_id')
            infraccion = InfraccionTransito.objects.filter(id=infraccion_id).first() if infraccion_id else None
            return render(request, 'infracciones/nueva_infraccion.html', {
                'infraccion': infraccion,
                'error': 'Debe seleccionar al menos un tipo de infracción.'
            })

        funcionario_codigo = request.POST.get('funcionario_codigo')
        fecha_denuncia = request.POST.get('fecha_denuncia')
        hora_denuncia = request.POST.get('hora_denuncia')
        boleta = request.POST.get('boleta')

        fecha = request.POST.get('fecha_ocurrencia')
        hora = request.POST.get('hora_ocurrencia')
        region = request.POST.get('region')
        provincia = request.POST.get('provincia')
        comuna = request.POST.get('comuna')
        direccion = request.POST.get('direccion')
        numero = request.POST.get('numero')
        block = request.POST.get('block')
        villa = request.POST.get('villa')
        depto = request.POST.get('depto')
        observaciones = request.POST.get('narracion')

        infraccion = InfraccionTransito.objects.create(
            funcionario_codigo=funcionario_codigo,
            fecha_denuncia=fecha_denuncia,
            hora_denuncia=hora_denuncia,
            boleta=boleta,
            tipo_infraccion=tipo_infraccion,
            fecha=fecha,
            hora=hora,
            region=region,
            provincia=provincia,
            comuna=comuna,
            direccion=direccion,
            numero=numero,
            block=block,
            villa=villa,
            depto=depto,
            observaciones=observaciones,
            creado_en=now()
        )

        return redirect(f'/infracciones/nueva/?infraccion_id={infraccion.id}#contenido-participante')

    # GET
    infraccion_id = request.GET.get('infraccion_id')
    mostrar_modal = request.GET.get('mostrar_modal') == '1'
    infraccion = InfraccionTransito.objects.filter(id=infraccion_id).first() if infraccion_id else None
    tipos_infraccion_list = infraccion.tipo_infraccion.split(',') if infraccion and infraccion.tipo_infraccion else []

    return render(request, 'infracciones/nueva_infraccion.html', {
        'infraccion': infraccion,
        'mostrar_modal': mostrar_modal,
        'tipos_infraccion_list': tipos_infraccion_list
    })

# Vista para agregar participante
def agregar_participante_infraccion(request, infraccion_id):
    infraccion = get_object_or_404(InfraccionTransito, id=infraccion_id)

    if request.method == 'POST':
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        color = request.POST.get('color')
        placa_patente = request.POST.get('placa_patente')
        chasis = request.POST.get('chasis')
        anio = request.POST.get('anio')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        calidad = request.POST.get('calidad')
        empadronado = request.POST.get('empadronado') == 'on'

        nombres = request.POST.get('nombres') if not empadronado else ''
        apellidos = request.POST.get('apellidos') if not empadronado else ''
        rut = request.POST.get('rut') if not empadronado else ''
        fecha_nacimiento = request.POST.get('fecha_nacimiento') if not empadronado else None
        region = request.POST.get('region') if not empadronado else ''
        provincia = request.POST.get('provincia') if not empadronado else ''
        comuna = request.POST.get('comuna') if not empadronado else ''
        direccion = request.POST.get('direccion') if not empadronado else ''
        numero = request.POST.get('numero_direccion') if not empadronado else ''

        ParticipanteInfraccion.objects.create(
            infraccion=infraccion,
            tipo_vehiculo=tipo_vehiculo,
            color=color,
            placa_patente=placa_patente,
            chasis=chasis,
            anio=anio,
            marca=marca,
            modelo=modelo,
            calidad=calidad,
            nombres=nombres,
            apellidos=apellidos,
            rut=rut,
            fecha_nacimiento=fecha_nacimiento,
            region=region,
            provincia=provincia,
            comuna=comuna,
            direccion=direccion,
        )

        return redirect(f'/infracciones/nueva/?infraccion_id={infraccion.id}&mostrar_modal=1#contenido-participante')

    return redirect('nueva_infraccion')

# Vista previa
def vista_previa_acta_infraccion(request, infraccion_id):
    infraccion = get_object_or_404(InfraccionTransito, id=infraccion_id)
    participantes = infraccion.participantes.all()
    parte = ParteInfraccion.objects.filter(infraccion=infraccion).first()
    tipos_infraccion_list = infraccion.tipo_infraccion.split(',') if infraccion.tipo_infraccion else []

    return render(request, 'infracciones/vista_previa_actai.html', {
        'infraccion': infraccion,
        'participantes': participantes,
        'parte': parte,
        'tipos_infraccion_list': tipos_infraccion_list
    })

# Generar parte
def generar_parte_infraccion(request, infraccion_id):
    if request.method == 'POST':
        juzgado_nombre = request.POST.get('juzgado')
        if not juzgado_nombre:
            return JsonResponse({'error': 'Debe seleccionar un juzgado'}, status=400)

        infraccion = get_object_or_404(InfraccionTransito, id=infraccion_id)
        parte_existente = ParteInfraccion.objects.filter(infraccion=infraccion).first()
        if not parte_existente:
            ParteInfraccion.objects.create(
                infraccion=infraccion,
                juzgado=juzgado_nombre
            )

        return JsonResponse({'success': True, 'redirect_url': reverse('vista_busqueda_partes_infracciones')})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Búsqueda de partes con filtros corregidos
def vista_busqueda_partes(request):
    fecha = request.GET.get('fecha')
    numero_parte = request.GET.get('numero_parte')

    partes = []

    if fecha or numero_parte:
        todas_partes = ParteInfraccion.objects.select_related('infraccion')

        if fecha:
            partes = [
                parte for parte in todas_partes
                if localtime(parte.creado_en).date().isoformat() == fecha
            ]
        else:
            partes = list(todas_partes)

        if numero_parte:
            partes = [p for p in partes if numero_parte.lower() in p.numero_parte.lower()]

        for parte in partes:
            parte.tipos_infraccion_list = parte.infraccion.tipo_infraccion.split(',') if parte.infraccion.tipo_infraccion else []

    return render(request, 'infracciones/busqueda_partes.html', {
        'partes': partes,
        'fecha': fecha,
        'numero_parte': numero_parte
    })

