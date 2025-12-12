"""Vistas de gestión de perfiles de usuario."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator

from ..models import Perfil
from ..constants import ICONOS_PERFIL


@login_required
def completar_perfil(request):
    """
    Vista para completar el perfil por primera vez después del registro.
    
    Solo accesible si el perfil está incompleto (sin nombre_completo).
    Redirige a ver_perfil si el perfil ya está completo.
    """
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    
    # Si el perfil ya está completo, redirigir a ver_perfil
    if perfil.nombre_completo:
        return redirect('ver_perfil')
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        icono = request.POST.get("icono_perfil")
        nivel = request.POST.get("nivel", "").strip()
        disciplina = request.POST.get("disciplina_preferida", "").strip()
        radio = request.POST.get("radio", "").strip()
        
        # Validar que al menos tenga nombre
        if not nombre:
            messages.error(request, "El nombre completo es obligatorio.")
            return render(request, "usuarios/completar_perfil.html", {
                "perfil": perfil,
                "iconos": ICONOS_PERFIL,
            })
        
        # Guardar datos
        perfil.nombre_completo = nombre
        perfil.icono_perfil = icono or 'default'
        perfil.nivel = nivel
        perfil.disciplina_preferida = disciplina
        
        try:
            if radio:
                perfil.radio = int(radio)
        except (ValueError, TypeError):
            messages.warning(request, "Radio inválido, se usará valor por defecto.")
        
        perfil.save()
        messages.success(request, "¡Perfil completado! Bienvenido a MatchDeportivo.")
        return redirect("ver_perfil")
    
    context = {
        "perfil": perfil,
        "iconos": ICONOS_PERFIL,
    }
    return render(request, "usuarios/completar_perfil.html", context)


@login_required
def ver_perfil(request):
    """
    Vista de perfil del usuario (solo lectura).
    
    Muestra información del perfil, estadísticas, rating y últimas actividades.
    No permite edición directa, solo visualización.
    """
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    
    # Si el perfil está incompleto, redirigir a completar_perfil
    if not perfil.nombre_completo:
        return redirect('completar_perfil')
    
    # Obtener estadísticas
    actividades_creadas = request.user.actividades_creadas.count()
    actividades_participando = request.user.actividades_participando.count()
    
    # Obtener últimas 3 actividades
    ultimas_actividades = request.user.actividades_participando.order_by('-fecha')[:3]
    
    # Obtener rating
    rating_promedio = perfil.rating_promedio()
    total_valoraciones = perfil.total_valoraciones()
    
    context = {
        "perfil": perfil,
        "rating_promedio": rating_promedio,
        "total_valoraciones": total_valoraciones,
        "actividades_creadas": actividades_creadas,
        "actividades_participando": actividades_participando,
        "ultimas_actividades": ultimas_actividades,
        "active_page": "perfil",
    }
    return render(request, "usuarios/ver_perfil.html", context)


@login_required
def editar_perfil(request):
    """
    Vista para editar el perfil del usuario.
    
    Permite modificar todos los campos del perfil.
    Redirige a ver_perfil después de guardar.
    """
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
        disciplina = request.POST.get("disciplina_preferida", "").strip()

        if nickname:
            perfil.nickname = nickname

        if nombre:
            perfil.nombre_completo = nombre

        perfil.icono_perfil = icono or perfil.icono_perfil
        perfil.ubicacion = ubicacion or perfil.ubicacion
        perfil.nivel = nivel or perfil.nivel
        perfil.horarios = horarios or perfil.horarios
        perfil.disciplina_preferida = disciplina or perfil.disciplina_preferida

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
        return redirect("ver_perfil")

    context = {
        "perfil": perfil,
        "iconos": ICONOS_PERFIL,
        "active_page": "perfil",
    }
    return render(request, "usuarios/editar_perfil.html", context)


@login_required
def valoraciones_detalladas(request):
    """
    Vista de valoraciones detalladas del usuario.
    
    Muestra todas las valoraciones recibidas con paginación.
    Incluye información del evaluador, puntuación, comentario y actividad.
    """
    perfil = request.user.perfil
    
    # Obtener todas las valoraciones recibidas
    valoraciones = request.user.valoraciones_recibidas.select_related(
        'evaluador',
        'evaluador__perfil',
        'actividad'
    ).order_by('-fecha_creacion')
    
    # Paginación (10 por página)
    paginator = Paginator(valoraciones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Rating promedio
    rating_promedio = perfil.rating_promedio()
    total_valoraciones = perfil.total_valoraciones()
    
    context = {
        "valoraciones": page_obj,
        "rating_promedio": rating_promedio,
        "total_valoraciones": total_valoraciones,
        "active_page": "perfil",
    }
    return render(request, "usuarios/valoraciones_detalladas.html", context)


# ============================================
# VISTAS EXISTENTES (sin cambios)
# ============================================

@login_required
def perfil(request):
    """
    DEPRECATED: Usar ver_perfil en su lugar.
    Mantener por compatibilidad temporal.
    """
    return redirect('ver_perfil')


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
            return redirect('ver_perfil')
        
        # Validación 2: Confirmación explícita
        if confirmacion != 'ELIMINAR':
            messages.error(request, f'Debes escribir "ELIMINAR" exactamente para confirmar.')
            return redirect('ver_perfil')
        
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
    return redirect('ver_perfil')
