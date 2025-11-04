from django.urls import path
from .views import login_view, logout_view, vista_inicio, admin_login_view
from .views import crear_usuario,  post_login, forzar_cambio_password, CambioClaveView, CambioClaveHechoView, lista_usuarios

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', vista_inicio, name='inicio'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('admin-login/', admin_login_view, name='admin_login'),
    path('usuarios/post_login/', post_login, name='post_login'),
    path('forzar-cambio-password/', forzar_cambio_password, name='forzar_cambio_password'),

#cambio de clave

    path('cambiar-clave/', CambioClaveView.as_view(), name='cambio_clave'),
    path('cambiar-clave/hecho/', CambioClaveHechoView.as_view(), name='cambio_clave_hecho'),

#lista usuarios

path('usuarios/', lista_usuarios, name='lista_usuarios'),



]
