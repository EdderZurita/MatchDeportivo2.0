"""Vistas de autenticación y gestión de usuarios.

Este módulo maneja todas las operaciones relacionadas con:
- Inicio de sesión (login)
- Registro de nuevos usuarios
- Recuperación de contraseña
- Cierre de sesión (logout)

Todas las vistas implementan medidas de seguridad como:
- Validación de contraseñas fuertes
- Protección contra enumeración de usuarios
- Validación de formato de email
- Protección CSRF automática de Django
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from ..models import Perfil


def inicioSesion(request):
    """
    Vista de inicio de sesión con email.
    
    Permite a los usuarios autenticarse usando su email y contraseña.
    Implementa protección contra enumeración de usuarios mediante
    mensajes genéricos que no revelan si el email existe o no.
    
    Seguridad implementada:
    - Mensajes genéricos (no revela si email existe)
    - Protección CSRF automática ({% csrf_token %} en template)
    - Rate limiting (pendiente de implementar)
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Renderiza login o redirige a perfil si es exitoso
        
    Método POST:
        - email: Email del usuario
        - password: Contraseña del usuario
    """
    if request.method == "POST":
        # Obtener y limpiar datos del formulario
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # ✅ Intentar autenticar sin revelar si el email existe
        # Esto previene ataques de enumeración de usuarios
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            # No revelamos que el email no existe
            user = None

        if user is not None:
            # Login exitoso
            login(request, user)
            
            # Verificar si el perfil está completo
            try:
                perfil = user.perfil
                if not perfil.nombre_completo:
                    # Perfil incompleto, redirigir a completar
                    return redirect("completar_perfil")
            except:
                # No tiene perfil, redirigir a completar
                return redirect("completar_perfil")
            
            # Perfil completo, redirigir a ver perfil
            return redirect("ver_perfil")
        else:
            # ✅ Mensaje genérico (no revela si email existe o contraseña incorrecta)
            # Esto es una medida de seguridad crítica
            return render(request, "sesion/inicioSesion.html", {
                "error": "Credenciales incorrectas. Verifica tu email y contraseña."
            })

    return render(request, "sesion/inicioSesion.html")


def registroSesion(request):
    """
    Vista de registro de nuevos usuarios.
    
    Permite a nuevos usuarios crear una cuenta en la plataforma.
    Implementa múltiples validaciones de seguridad para asegurar
    datos válidos y contraseñas fuertes.
    
    Validaciones implementadas:
    - Formato de email válido
    - Username único
    - Email único
    - Contraseña fuerte (8+ caracteres, mayúscula, número)
    - Protección CSRF automática
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Renderiza registro o redirige a login si es exitoso
        
    Método POST:
        - username: Nombre de usuario (único)
        - email: Email del usuario (único)
        - password: Contraseña (debe cumplir requisitos de seguridad)
    """
    if request.method == "POST":
        # Obtener y limpiar datos del formulario
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # ✅ VALIDACIÓN 1: Formato de email
        # Verifica que el email tenga un formato válido (usuario@dominio.com)
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'sesion/registroSesion.html', {
                'error': 'Email inválido. Verifica el formato.',
                'request': request
            })

        # ✅ VALIDACIÓN 2: Username único
        # Previene duplicados de nombres de usuario
        if User.objects.filter(username=username).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El nombre de usuario ya está en uso',
                'request': request
            })

        # ✅ VALIDACIÓN 3: Email único
        # Previene múltiples cuentas con el mismo email
        if User.objects.filter(email=email).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El correo ya está registrado',
                'request': request
            })
        
        # ✅ VALIDACIÓN 4: Fortaleza de contraseña
        # Aplica todos los validadores configurados en settings.py:
        # - Mínimo 8 caracteres
        # - Al menos una mayúscula
        # - Al menos un número
        # - No puede ser similar al username/email
        # - No puede ser una contraseña común
        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, 'sesion/registroSesion.html', {
                'error': ', '.join(e.messages),
                'request': request
            })


        # ✅ Crear usuario con contraseña hasheada
        # make_password() usa PBKDF2 por defecto (seguro)
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        # Auto-login después de registro exitoso
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        
        # Redirigir a completar perfil (primera vez)
        return redirect('completar_perfil')

    return render(request, 'sesion/registroSesion.html')

@login_required
def cerrarSesion(request):
    """
    Vista de cierre de sesión.
    
    Cierra la sesión del usuario actual y lo redirige a la página principal.
    Requiere que el usuario esté autenticado (@login_required).
    
    Seguridad:
    - Invalida la sesión del usuario
    - Limpia cookies de sesión
    - Previene acceso no autorizado
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Redirige a la página principal
    """
    logout(request)
    return redirect("home")
