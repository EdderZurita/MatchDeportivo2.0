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
