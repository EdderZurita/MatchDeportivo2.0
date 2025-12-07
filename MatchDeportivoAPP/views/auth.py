"""Vistas de autenticación."""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from ..models import Perfil


def inicioSesion(request):
    """Login con email. Redirige al perfil si es exitoso."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return render(request, "sesion/inicioSesion.html", {
                "error": "Correo incorrecto"
            })

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
    """Registro de nuevos usuarios. Valida que username y email sean únicos."""
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if User.objects.filter(username=username).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El nombre de usuario ya está en uso',
                'request': request
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El correo ya está registrado',
                'request': request
            })

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        return redirect('inicioSesion')

    return render(request, 'sesion/registroSesion.html')


def olvidoContraseña(request):
    """Recuperación de contraseña usando el email."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if password1 != password2:
            return render(request, "sesion/olvidoContraseña.html", {
                "error": "Las contraseñas no coinciden."
            })

        try:
            usuario = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "sesion/olvidoContraseña.html", {
                "error": "Este correo no está registrado."
            })

        usuario.password = make_password(password1)
        usuario.save()

        return render(request, "sesion/olvidoContraseña.html", {
            "success": "Tu contraseña ha sido cambiada con éxito."
        })

    return render(request, "sesion/olvidoContraseña.html")


@login_required
def cerrarSesion(request):
    """Cierra la sesión del usuario y redirige a la página principal."""
    logout(request)
    return redirect("home")
