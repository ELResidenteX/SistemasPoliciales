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

# ✅ Crear evento con control de rol
@login_required
def vista_crear_evento(request):
    perfil = request.user.perfilusuario
    if perfil.rol not in ['super_admin', 'administrador']:
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    return render(request, 'core/nuevo_evento.html')


# ✅ Login general (por RUT)
def login_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        password = request.POST.get('password')

        user = authenticate(request, username=rut, password=password)

        if user is not None:
            # ⚠️ Verificamos si se marcó que debe cambiar la contraseña
            if user.username in request.session.get('usuarios_con_cambio_pendiente', []):
                request.session['forzar_cambio_password'] = True
                request.session['inicio_temporal'] = timezone.now().isoformat()
                # 🧼 Limpiamos la lista
                request.session['usuarios_con_cambio_pendiente'].remove(user.username)

            login(request, user)
            rotate_token(request)

            if request.session.get('forzar_cambio_password'):
                return redirect('forzar_cambio_password')

            return redirect('inicio')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'usuarios/login.html')


# ✅ Vista para cambio obligatorio de contraseña
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
            messages.success(request, 'Contraseña actualizada correctamente. Recuerde que deberá cambiarla nuevamente en 30 días.')
            return redirect('inicio')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'usuarios/cambiar_password_obligado.html', {'form': form})


# ✅ Login para administrador
def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'perfilusuario'):
            # ⚠️ Verificamos si se marcó que debe cambiar la contraseña
            if user.username in request.session.get('usuarios_con_cambio_pendiente', []):
                request.session['forzar_cambio_password'] = True
                request.session['inicio_temporal'] = timezone.now().isoformat()
                request.session['usuarios_con_cambio_pendiente'].remove(user.username)

            login(request, user)
            request.user = user
            request.user.refresh_from_db()

            if request.session.get('forzar_cambio_password') and user.perfilusuario.rol != 'super_admin':
                return redirect('forzar_cambio_password')

            return HttpResponseRedirect(reverse('inicio'))

        else:
            return render(request, 'usuarios/admin_login.html', {
                'error': 'Credenciales inválidas o acceso no autorizado.'
            })

    return render(request, 'usuarios/admin_login.html')


# ✅ Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# ✅ Página de inicio (protegida)
@login_required
def vista_inicio(request):
    return render(request, 'base.html')


# ✅ Crear usuario desde panel admin
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

        # ✅ Marcamos que el nuevo usuario debe cambiar su contraseña
        if 'usuarios_con_cambio_pendiente' not in request.session:
            request.session['usuarios_con_cambio_pendiente'] = []

        request.session['usuarios_con_cambio_pendiente'].append(rut)

        request.user.refresh_from_db()
        return redirect('crear_usuario')

    return render(request, 'usuarios/crear_usuario.html')


# ✅ Vista intermedia para asegurar que el perfil se cargue
@login_required
def post_login(request):
    request.user.refresh_from_db()
    rol = getattr(request.user.perfilusuario, 'rol', None)
    return render(request, 'usuarios/post_login.html', {'rol': rol})

