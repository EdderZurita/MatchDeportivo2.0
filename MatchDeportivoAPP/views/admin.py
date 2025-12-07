"""
Vistas de administración del sistema.
"""
from django.shortcuts import render
from django.contrib.auth.models import User

from ..models import Log


def ver_logs(request):
    """
    Vista para mostrar logs del sistema.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de logs
    """
    logs = Log.objects.all().order_by('-fecha')
    return render(request, 'administracion/ver_logs.html', {'logs': logs})


def gestionar_usuarios(request):
    """
    Vista para gestionar usuarios del sistema.
    Consulta la base de datos real en lugar de datos hardcodeados.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de gestión de usuarios
    """
    # Obtener todos los usuarios con su perfil asociado
    usuarios = User.objects.select_related('perfil').all()
    
    return render(request, "administracion/gestionar_usuarios.html", {
        "usuarios": usuarios
    })
