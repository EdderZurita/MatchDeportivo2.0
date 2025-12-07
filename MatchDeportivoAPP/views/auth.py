"""
Vistas de autenticación: login, registro, recuperación de contraseña y logout.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from ..models import Perfil


def inicioSesion(request):
    """
    Vista de inicio de sesión.
    Permite login con email en lugar de username.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de login o redirección al perfil
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return render(request, "sesion/inicioSesion.html", {
                "error": "Correo incorrecto"
            })

        # Autenticar con username y password
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("perfil")
        else:
            return render(request, "sesion/inicioSesion.html", {
                "error": "Contraseña incorrecta"
            })

    return render(request, "sesion/inicioSesion.html")


def registroSesion(request):
    """
    Vista de registro de nuevos usuarios.
    Valida que username y email sean únicos.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de registro o redirección al login
    """
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Validación de username duplicado
        if User.objects.filter(username=username).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El nombre de usuario ya está en uso',
                'request': request
            })

        # Validación de email duplicado
        if User.objects.filter(email=email).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El correo ya está registrado',
                'request': request
            })

        # Crear usuario
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        # Redirigir al login
        return redirect('inicioSesion')

    return render(request, 'sesion/registroSesion.html')


def olvidoContraseña(request):
    """
    Vista de recuperación de contraseña.
    Permite cambiar la contraseña usando el email.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de recuperación
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # Validar contraseñas iguales
        if password1 != password2:
            return render(request, "sesion/olvidoContraseña.html", {
                "error": "Las contraseñas no coinciden."
            })

        # Buscar usuario
        try:
            usuario = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "sesion/olvidoContraseña.html", {
                "error": "Este correo no está registrado."
            })

        # Cambiar contraseña de forma segura
        usuario.password = make_password(password1)
        usuario.save()

        return render(request, "sesion/olvidoContraseña.html", {
            "success": "Tu contraseña ha sido cambiada con éxito."
        })

    return render(request, "sesion/olvidoContraseña.html")


@login_required
def cerrarSesion(request):
    """
    Vista de cierre de sesión.
    Requiere autenticación.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con redirección al login
    """
    logout(request)
    return redirect("inicioSesion")
