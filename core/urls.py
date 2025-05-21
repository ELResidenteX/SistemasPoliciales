from django.urls import path
from . import views

urlpatterns = [
    # ✅ Home
    path('', views.home, name='home'),

    # ✅ Eventos
    path('evento/nuevo/', views.nuevo_evento, name='nuevo_evento'),
    path('evento/buscar/', views.buscar_evento, name='buscar_evento'),

    # ✅ Participantes
    path('evento/<int:evento_id>/participante/nuevo/', views.agregar_participante, name='agregar_participante'),
    path('participante/<int:participante_id>/editar/', views.editar_participante, name='editar_participante'),
    path('participante/<int:participante_id>/eliminar/', views.eliminar_participante, name='eliminar_participante'),

    # ✅ Especies
    path('especie/agregar/<int:evento_id>/', views.agregar_especie, name='agregar_especie'),
    path('especie/editar/<int:especie_id>/', views.editar_especie, name='editar_especie'),
    path('especie/eliminar/<int:especie_id>/', views.eliminar_especie, name='eliminar_especie'),

    # ✅ Validación de partes
    path('validacion-partes/', views.validacion_partes, name='validacion_partes'),

    # ✅ Generación de parte policial
    path('parte/generar/<int:evento_id>/', views.generar_parte_policial, name='generar_parte_policial'),

    # ✅ Enviar evento a validación y vista de eventos en validación
    path('evento/<int:evento_id>/enviar-a-validacion/', views.enviar_a_validacion, name='enviar_a_validacion'),
    path('evento-en-validacion/', views.evento_en_validacion, name='evento_en_validacion'),

    # ✅ URL PARA LA VISTA PREVIA
    path('evento/<int:evento_id>/vista-previa/', views.vista_previa_evento, name='vista_previa_evento'),
    
    #EDITAR EVENTO

    path('evento/en-validacion/<int:evento_id>/editar/modal/', views.cargar_modal_edicion_evento, name='modal_editar_evento'),
    path('evento/en-validacion/<int:evento_id>/editar/guardar/', views.guardar_edicion_evento, name='guardar_edicion_evento'),
    path('evento/en-validacion/<int:evento_id>/editar/guardar/', views.guardar_edicion_evento, name='guardar_edicion_evento'),

    #ASIGNAR FISCALIA AL PARTE
    
    path('asignar-fiscalia/<int:parte_id>/', views.asignar_fiscalia_parte, name='asignar_fiscalia_parte'),

    #detalle parte policial

    path('parte/<int:parte_id>/detalle/', views.detalle_parte_policial, name='detalle_parte_policial'),

    # VER PARTE POLICIAL
path('parte/ver/<int:parte_id>/', views.ver_parte_policial, name='ver_parte_policial'),
path('parte/<int:parte_id>/vista-previa-modal/', views.vista_previa_parte_modal, name='vista_previa_parte_modal'),

   #busqueda de partes

   path('busqueda-partes/', views.vista_busqueda_partes, name='vista_busqueda_partes'),
   path('parte/<int:parte_id>/vista-previa-modal/', views.vista_previa_parte_modal, name='vista_previa_parte_modal'),

   #autocompletar fiscalia busqueda partes

   path('autocompletar-fiscalia/', views.autocompletar_fiscalia, name='autocompletar_fiscalia'),
   
   path('evento/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),

]


