"""Vistas de gestión de perfiles de usuario."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from ..models import Perfil
from ..constants import ICONOS_PERFIL


@login_required
def perfil(request):
    """Muestra y edita el perfil del usuario: info personal, ubicación y preferencias."""
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        icono = request.POST.get("icono_perfil")
        ubicacion = request.POST.get("ubicacion", "").strip()
        lat = request.POST.get("latitud", "").strip()
        lng = request.POST.get("longitud", "").strip()
        nivel = request.POST.get("nivel", "").strip()
        horarios = request.POST.get("horarios", "").strip()
        radio = request.POST.get("radio", "").strip()
        nickname = request.POST.get("nickname", "").strip()

        if nickname:
            perfil.nickname = nickname

        if nombre:
            perfil.nombre_completo = nombre

        perfil.icono_perfil = icono or perfil.icono_perfil
        perfil.ubicacion = ubicacion or perfil.ubicacion
        perfil.nivel = nivel or perfil.nivel
        perfil.horarios = horarios or perfil.horarios

        try:
            if lat != "":
                perfil.latitud = float(lat)
        except (ValueError, TypeError):
            messages.warning(request, "Latitud inválida.")

        try:
            if lng != "":
                perfil.longitud = float(lng)
        except (ValueError, TypeError):
            messages.warning(request, "Longitud inválida.")

        try:
            if radio != "":
                perfil.radio = int(radio)
        except (ValueError, TypeError):
            messages.warning(request, "Radio inválido.")

        perfil.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("perfil")

    context = {
        "perfil": perfil,
        "iconos": ICONOS_PERFIL,
        "active_page": "perfil",
    }
    return render(request, "usuarios/perfil.html", context)


@login_required
def perfil_jugador(request):
    """Vista de perfil de jugador (funcionalidad futura)."""
    return render(request, "usuarios/perfil_jugador.html")


@login_required
def perfil_participante(request, user_id):
    """Muestra la información pública de un participante."""
    usuario = get_object_or_404(User, pk=user_id)
    
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        perfil = None
        
    context = {
        'usuario': usuario,
        'perfil': perfil,
    }
    return render(request, 'actividades/perfil_participante.html', context)


@login_required
def eliminar_cuenta(request):
    """
    Elimina permanentemente la cuenta del usuario y todos sus datos relacionados.
    
    Seguridad:
    - Requiere autenticación (@login_required)
    - Requiere confirmación de contraseña
    - Requiere escribir "ELIMINAR" para confirmar
    - Eliminación en cascada automática de Django
    
    Datos eliminados:
    - Usuario (User)
    - Perfil (Perfil)
    - Actividades creadas (Actividad)
    - Participaciones (relación many-to-many)
    - Valoraciones dadas y recibidas (Valoracion)
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Redirige a home después de eliminar
        
    Método POST:
        - password: Contraseña del usuario para confirmar
        - confirmacion: Debe ser exactamente "ELIMINAR"
    """
    if request.method == "POST":
        password = request.POST.get('password', '')
        confirmacion = request.POST.get('confirmacion', '').strip()
        
        # Validación 1: Contraseña correcta
        from django.contrib.auth import authenticate, logout
        user = authenticate(
            request, 
            username=request.user.username, 
            password=password
        )
        
        if user is None:
            messages.error(request, "Contraseña incorrecta. No se puede eliminar la cuenta.")
            return redirect('perfil')
        
        # Validación 2: Confirmación explícita
        if confirmacion != 'ELIMINAR':
            messages.error(request, f'Debes escribir "ELIMINAR" exactamente para confirmar.')
            return redirect('perfil')
        
        # Guardar username para el mensaje
        username = request.user.username
        
        # Eliminar cuenta (Django elimina en cascada automáticamente)
        request.user.delete()
        
        # Cerrar sesión
        logout(request)
        
        # Mensaje de confirmación
        messages.success(
            request, 
            f"La cuenta de {username} ha sido eliminada permanentemente. "
            f"Todos tus datos han sido borrados."
        )
        return redirect('home')
    
    # Si no es POST, redirigir a perfil
    return redirect('perfil')
