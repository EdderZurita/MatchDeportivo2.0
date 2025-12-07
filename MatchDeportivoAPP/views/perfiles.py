"""
Vistas de gestión de perfiles de usuario.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from ..models import Perfil


@login_required
def perfil(request):
    """
    Vista de perfil del usuario autenticado.
    Permite ver y editar información personal, ubicación, preferencias deportivas.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de perfil
    """
    # Obtener o crear perfil del usuario
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

        # Convertir y validar números
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

    # Lista de iconos disponibles
    iconos = [
        ("futbol", "img/futbol.png"),
        ("basketball", "img/basketball.png"),
        ("skate", "img/skate.png"),
        ("voleibol", "img/voleibol.png"),
        ("running", "img/running.png"),
        ("tenis", "img/tenis.png"),
    ]

    context = {
        "perfil": perfil,
        "iconos": iconos,
        "active_page": "perfil",
    }
    return render(request, "usuarios/perfil.html", context)


@login_required
def perfil_jugador(request):
    """
    Vista de perfil de jugador (funcionalidad futura).
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de perfil de jugador
    """
    return render(request, "usuarios/perfil_jugador.html")


@login_required
def perfil_participante(request, user_id):
    """
    Muestra la información pública de un participante.
    
    Args:
        request: HttpRequest object
        user_id: ID del usuario a mostrar
        
    Returns:
        HttpResponse con el template de perfil del participante
    """
    # Obtener usuario
    usuario = get_object_or_404(User, pk=user_id)
    
    # Intentar obtener el perfil asociado
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        perfil = None
        
    context = {
        'usuario': usuario,
        'perfil': perfil,
    }
    return render(request, 'actividades/perfil_participante.html', context)
