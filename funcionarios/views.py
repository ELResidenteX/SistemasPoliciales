from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from funcionarios.models import PerfilUsuario
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.middleware.csrf import rotate_token

# ✅ Crear evento con control de rol
@login_required
def vista_crear_evento(request):
    perfil = request.user.perfilusuario
    if perfil.rol not in ['super_admin', 'administrador']:
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    return render(request, 'core/nuevo_evento.html')


# ✅ Login general (por RUT)
def login_view(request):
    print("Método:", request.method)
    print("POST data:", request.POST)
    print("CSRF token:", request.META.get("CSRF_COOKIE"))
    if request.method == 'POST':
        rut = request.POST.get('rut')  # Este es el campo del formulario
        password = request.POST.get('password')

        user = authenticate(request, username=rut, password=password)

        if user is not None:
            login(request, user)
            rotate_token(request)  # 🔒 Esto renueva el token CSRF para prevenir errores al recargar
            return redirect('inicio')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'usuarios/login.html')



# ✅ Login para administrador
def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'perfilusuario') and user.perfilusuario.rol in ['super_admin', 'administrador']:
            login(request, user)

            # ✅ Forzar recarga del perfil luego del login
            request.user = user
            request.user.refresh_from_db()

            # ✅ Redirigir con recarga forzada (opcional)
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

        request.user.refresh_from_db()  # Actualiza perfil
        return redirect('crear_usuario')

    return render(request, 'usuarios/crear_usuario.html')


# ✅ Vista intermedia para asegurar que el perfil se cargue
@login_required
def post_login(request):
    request.user.refresh_from_db()  # 🔁 Asegura que request.user.perfilusuario esté disponible
    rol = getattr(request.user.perfilusuario, 'rol', None)
    return render(request, 'usuarios/post_login.html', {'rol': rol})


# (No es necesaria post_login_redirect en este flujo)
