from django.urls import path
from . import views
from core.api_views import CrearEventoDesdeAppAPIView, CrearParticipanteDesdeAppAPIView
from django.http import JsonResponse
from . import selectors_api 
from .selectors_api import api_delitos, listar_lugares_procedimiento, listar_tipos_lugar  # 👈 asegúrate de que api_delitos esté definida ahí
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static
from .views import cargar_unidades_policiales, reset_superadmin, cambiar_unidad_desde_login, crear_configuracion_temporal, vista_mapa_geolocalizacion, eventos_geolocalizados_json, vista_mapa_geolocalizacion, geojson_comuna_activa, api_eventos_tiempo, api_top_unidades, api_top_comunas, api_porcentaje_delitos_criticos, api_eventos_hora_dia



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
  

  #URLS RELACIONADAS A LA APP MOVOL DEL PROYECTO

  #Recibe los datos JSON (o multipart/form-data si hay imágenes) desde la app móvil. Los valida

  
path('api/eventos/crear/', CrearEventoDesdeAppAPIView.as_view(), name='crear_evento_api'),  
path('api/participantes/crear/', CrearParticipanteDesdeAppAPIView.as_view(), name='crear_participante_api'),

#URLS ENDPOINTS RESPECTO AL MODELO Y LINKEAR SELECT COMUNAS, REGIONES Y PROVINCIAS EN APP MOVIL PARA CREAR EVENTO

 path('api/regiones/', selectors_api.api_regiones, name='api_regiones'),
    path('api/provincias/', selectors_api.api_provincias, name='api_provincias'),
    path('api/comunas/', selectors_api.api_comunas, name='api_comunas'),

#urls endpoint delito

path('api/delitos/', api_delitos, name='api_delitos'),

#urls endpoint Lugar Procedimiento

path('api/lugares-procedimiento/', listar_lugares_procedimiento),

#Urls endpoint tipo lugar

path('api/tipos-lugar/', listar_tipos_lugar),

#Login desde app y endpoint

path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


path('cargar-delitos/', views.cargar_delitos_desde_json, name='cargar_delitos_json'),
path('ejecutar-cargar-regiones/', views.ejecutar_cargar_regiones, name='ejecutar_cargar_regiones'),

#manuales

path('manuales/', views.manuales_usuario, name='manuales_usuario'),

#Vista solo cargar cuarteeles

path("utilidades/cargar-unidades-policiales/", cargar_unidades_policiales, name="cargar_unidades_policiales"),



#vista solo para cambiar password sjuperadmin

path("reset-superadmin/", reset_superadmin, name="reset_superadmin"),
path('admin/cambiar-unidad/', views.cambiar_unidad_activa, name='cambiar_unidad'),

#cambiar unidad desde login

path("cambiar-unidad-login/", cambiar_unidad_desde_login, name="cambiar_unidad_desde_login"),

#vista temporal unidad asignacion

path('crear-config/', crear_configuracion_temporal, name='crear_configuracion_temporal'),

#vista geolocalizacion

 path("estadisticas/geolocalizacion/", vista_mapa_geolocalizacion, name="estadisticas_geolocalizacion"),

#coordenadas lat y long


path("api/eventos-geolocalizados/", eventos_geolocalizados_json, name="api_eventos_geolocalizados"),
path("api/comuna-activa/", geojson_comuna_activa, name="geojson_comuna_activa"),
path('api/comuna-poligono/', views.geojson_comuna_por_nombre, name='geojson_comuna_nombre'),
path('api/comunas/', views.lista_comunas_json, name='lista_comunas'),
path("api/eventos-por-comuna/", views.eventos_por_comuna_json, name="api_eventos_por_comuna"),
path("api/estadisticas-delitos/", views.api_estadisticas_por_delito, name="api_estadisticas_por_delito"),


#estadisticas mapaa

path('api_eventos_tiempo', api_eventos_tiempo, name='api_eventos_tiempo'),
path('api_top_unidades', api_top_unidades, name='api_top_unidades'),
path('api_top_comunas', api_top_comunas, name='api_top_comunas'),
path('api_porcentaje_delitos_criticos', api_porcentaje_delitos_criticos, name='api_porcentaje_delitos_criticos'),



]


