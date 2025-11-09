from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.middleware.csrf import rotate_token
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from funcionarios.models import PerfilUsuario, UnidadPolicial


@login_required
def vista_crear_evento(request):
    perfil = request.user.perfilusuario
    if perfil.rol not in ['super_admin', 'administrador']:
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    return render(request, 'core/nuevo_evento.html')


def login_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        password = request.POST.get('password')

        user = authenticate(request, username=rut, password=password)

        if user is not None:
            login(request, user)
            rotate_token(request)
            perfil = user.perfilusuario

            # 🔐 Si nunca cambió su contraseña
            if perfil.cambio_password_obligado and perfil.rol != 'super_admin':
                request.session['inicio_temporal'] = timezone.now().isoformat()
                return redirect('forzar_cambio_password')

            return redirect('inicio')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'usuarios/login.html')


def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'perfilusuario'):
            login(request, user)
            rotate_token(request)
            perfil = user.perfilusuario

            if perfil.cambio_password_obligado and perfil.rol != 'super_admin':
                request.session['inicio_temporal'] = timezone.now().isoformat()
                return redirect('forzar_cambio_password')

            return HttpResponseRedirect(reverse('inicio'))

        else:
            return render(request, 'usuarios/admin_login.html', {
                'error': 'Credenciales inválidas o acceso no autorizado.'
            })

    return render(request, 'usuarios/admin_login.html')


@login_required
def forzar_cambio_password(request):
    perfil = request.user.perfilusuario

    if not perfil.cambio_password_obligado:
        return redirect('inicio')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

            # ✅ Marcamos que ya no está obligado (hasta el próximo ciclo)
            perfil.cambio_password_obligado = False
            perfil.fecha_ultimo_cambio = timezone.now()  # 🕒 Registramos el cambio real
            perfil.save()

            request.session.pop('inicio_temporal', None)

            messages.success(request, '✅ Contraseña actualizada correctamente. Recuerde que deberá cambiarla nuevamente en 30 días.')
            return redirect('inicio')
        else:
            messages.error(request, '❌ La contraseña no cumple con los requisitos. Intente nuevamente.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'usuarios/cambiar_password_obligado.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def vista_inicio(request):
    return render(request, 'base.html')


@login_required
def crear_usuario(request):
    # 🔒 Verificación de permisos
    if request.user.perfilusuario.rol not in ['super_admin', 'administrador']:
        return redirect('inicio')

    unidades = UnidadPolicial.objects.all().order_by("nombre")


    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        rol = request.POST.get('rol', '')
        unidad_id = request.POST.get('unidad_policial')

        # Validaciones básicas
        if not rut:
            return render(request, 'usuarios/crear_usuario.html', {
                'error': 'El campo RUT es obligatorio.',
                'unidades': unidades
            })

        if PerfilUsuario.objects.filter(rut=rut).exists() or User.objects.filter(username=rut).exists():
            return render(request, 'usuarios/crear_usuario.html', {
                'error': 'Ya existe un usuario con ese RUT.',
                'unidades': unidades
            })

        # Crear usuario base
        nuevo_usuario = User.objects.create_user(
            username=rut,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Asignar la unidad seleccionada
        unidad = UnidadPolicial.objects.filter(id=unidad_id).first()

        # Crear perfil asociado
        PerfilUsuario.objects.create(
            user=nuevo_usuario,
            rut=rut,
            rol=rol,
            unidad_policial=unidad,
            cambio_password_obligado=True
        )

        return redirect('crear_usuario')

    # GET → mostrar formulario
    return render(request, 'usuarios/crear_usuario.html', {'unidades': unidades})


@login_required
def post_login(request):
    request.user.refresh_from_db()
    rol = getattr(request.user.perfilusuario, 'rol', None)
    return render(request, 'usuarios/post_login.html', {'rol': rol})

#cambio de clave

class CambioClaveView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'usuarios/cambio_clave.html'
    success_url = reverse_lazy('cambio_clave_hecho')

    def form_valid(self, form):
        messages.success(self.request, '¡Contraseña actualizada correctamente!')
        return super().form_valid(form)

#pantalla de confirmacion


class CambioClaveHechoView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/cambio_clave_hecho.html'

@login_required
def lista_usuarios(request):
    # Solo super_admin o administrador pueden acceder
    if request.user.perfilusuario.rol not in ['super_admin', 'administrador']:
        return redirect('inicio')

    usuarios = PerfilUsuario.objects.select_related('user', 'unidad_policial').order_by('user__first_name')

    if request.method == "POST":
        # Eliminar usuario
        usuario_id = request.POST.get("usuario_id")
        perfil = PerfilUsuario.objects.filter(id=usuario_id).first()
        if perfil:
            perfil.user.delete()  # elimina también el User asociado
        return redirect('lista_usuarios')

    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

#EDITAR USUARIOS

@login_required
def editar_usuario(request, usuario_id):
    if request.user.perfilusuario.rol not in ['super_admin', 'administrador']:
        return redirect('inicio')

    perfil = PerfilUsuario.objects.select_related('user').filter(id=usuario_id).first()
    if not perfil:
        return redirect('lista_usuarios')

    unidades = UnidadPolicial.objects.all().order_by("nombre")

    if request.method == "POST":
        perfil.user.first_name = request.POST.get("first_name", "").strip()
        perfil.user.last_name = request.POST.get("last_name", "").strip()
        perfil.rol = request.POST.get("rol", perfil.rol)
        unidad_id = request.POST.get("unidad_policial")
        perfil.unidad_policial = UnidadPolicial.objects.filter(id=unidad_id).first()
        perfil.user.save()
        perfil.save()
        messages.success(request, "✅ Usuario actualizado correctamente.")
        return redirect("lista_usuarios")

    return render(request, "usuarios/editar_usuario.html", {
        "perfil": perfil,
        "unidades": unidades
    })

#cambio clave momentanea 

# 🚨 VISTA TEMPORAL PARA RESETEAR CONTRASEÑA DEL ADMIN
from django.contrib.auth.models import User
from django.http import HttpResponse

def reset_admin_temp(request):
    try:
        # Cambia este nombre al usuario real de tu admin
        admin = User.objects.get(username="Administrador2")  
        
        # Nueva contraseña que asignarás
        admin.set_password("Garra1991/")  
        admin.save()

        return HttpResponse("✅ Contraseña del admin restablecida correctamente. Ahora puedes entrar al /admin.")
    except User.DoesNotExist:
        return HttpResponse("❌ No se encontró el usuario 'AdminPrincipal'.")





