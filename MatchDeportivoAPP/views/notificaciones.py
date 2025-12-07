"""
Vistas de gestión de notificaciones.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import Notificacion


@login_required
def notificaciones(request):
    """
    Vista de notificaciones del usuario.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de notificaciones
    """
    context = {
        'active_page': 'notificaciones',
    }
    return render(request, "usuarios/notificaciones.html", context)


@login_required
def lista_notificaciones(request):
    """
    Vista de lista de notificaciones del usuario autenticado.
    Carga las notificaciones del usuario logueado.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de lista de notificaciones
    """
    # Cargar las notificaciones del usuario logueado
    notificaciones_usuario = Notificacion.objects.filter(usuario=request.user)
    
    context = {
        # Ambas listas son necesarias para el template
        'notificaciones': notificaciones_usuario,
        'notificaciones_sin_leer': notificaciones_usuario.filter(leida=False),
        'active_page': 'notificaciones',
    }
    return render(request, "actividades/notificaciones.html", context)


def crear_notificacion_simple(usuario, actividad, tipo, mensaje):
    """
    Crea una notificación simple para un usuario.
    
    Args:
        usuario: Usuario que recibirá la notificación
        actividad: Actividad relacionada (puede ser None)
        tipo: Tipo de notificación (debe ser una opción válida del modelo)
        mensaje: Mensaje de la notificación
        
    Returns:
        None
    """
    try:
        Notificacion.objects.create(
            usuario=usuario,
            actividad=actividad,
            tipo=tipo,
            mensaje=mensaje,
            leida=False 
        )
    except Exception as e:
        # No romper la transacción principal si falla la notificación
        print(f"ERROR: No se pudo crear la notificación para {usuario.username}. Causa: {e}")
        pass
