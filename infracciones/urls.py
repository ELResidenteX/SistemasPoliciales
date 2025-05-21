from django.urls import path
from . import views

urlpatterns = [
    path('nueva/', views.nueva_infraccion, name='nueva_infraccion'),
    # path('<int:infraccion_id>/editar/', views.editar_infraccion, name='editar_infraccion'),  # Reservado para futuras etapas
    path('participante/agregar/<int:infraccion_id>/', views.agregar_participante_infraccion, name='agregar_participante_infraccion'),

    # Vista previa del acta de infracción
    path('infraccion/<int:infraccion_id>/vista-previa/', views.vista_previa_acta_infraccion, name='vista_previa_acta_infraccion'),

    # Generar parte
    path('parte/generar/<int:infraccion_id>/', views.generar_parte_infraccion, name='generar_parte_infraccion'),

    # Búsqueda de partes (nombre cambiado para evitar colisiones)
    path('partes/', views.vista_busqueda_partes, name='vista_busqueda_partes_infracciones'),
]

