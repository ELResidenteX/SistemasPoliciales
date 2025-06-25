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

from funcionarios.models import PerfilUsuario


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
            primer_login = user.last_login is None  # ✅ capturamos antes de login()

            login(request, user)
            rotate_token(request)
            request.user = user
            request.user.refresh_from_db()

            if primer_login and user.perfilusuario.rol != 'super_admin':
                request.session['forzar_cambio_password'] = True
                request.session['inicio_temporal'] = timezone.now().isoformat()

            if request.session.get('forzar_cambio_password'):
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
            primer_login = user.last_login is None  # ✅ antes del login()

            login(request, user)
            rotate_token(request)
            request.user = user
            request.user.refresh_from_db()

            if primer_login and user.perfilusuario.rol != 'super_admin':
                request.session['forzar_cambio_password'] = True
                request.session['inicio_temporal'] = timezone.now().isoformat()

            if request.session.get('forzar_cambio_password'):
                return redirect('forzar_cambio_password')

            return HttpResponseRedirect(reverse('inicio'))

        else:
            return render(request, 'usuarios/admin_login.html', {
                'error': 'Credenciales inválidas o acceso no autorizado.'
            })

    return render(request, 'usuarios/admin_login.html')


@login_required
def forzar_cambio_password(request):
    if not request.session.get('forzar_cambio_password'):
        return redirect('inicio')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

            request.session.pop('forzar_cambio_password', None)
            request.session.pop('inicio_temporal', None)
            request.session['ultima_password_cambio'] = timezone.now().isoformat()

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
    if request.user.perfilusuario.rol not in ['super_admin', 'administrador']:
        return redirect('inicio')

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        rol = request.POST.get('rol', '')

        if not rut:
            return render(request, 'usuarios/crear_usuario.html', {
                'error': 'El campo RUT es obligatorio.'
            })

        if PerfilUsuario.objects.filter(rut=rut).exists() or User.objects.filter(username=rut).exists():
            return render(request, 'usuarios/crear_usuario.html', {
                'error': 'Ya existe un usuario con ese RUT.'
            })

        nuevo_usuario = User.objects.create_user(
            username=rut,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        PerfilUsuario.objects.create(
            user=nuevo_usuario,
            rut=rut,
            rol=rol
        )

        return redirect('crear_usuario')

    return render(request, 'usuarios/crear_usuario.html')


@login_required
def post_login(request):
    request.user.refresh_from_db()
    rol = getattr(request.user.perfilusuario, 'rol', None)
    return render(request, 'usuarios/post_login.html', {'rol': rol})






