"""Vistas de administración."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from ..models import Log


@login_required
def ver_logs(request):
    """Muestra los logs del sistema para administradores."""
    logs = Log.objects.all().order_by('-fecha')[:100]
    context = {
        'logs': logs,
        'active_page': 'admin',
    }
    return render(request, 'administracion/logs.html', context)


@login_required
def gestionar_usuarios(request):
    """Gestiona usuarios del sistema."""
    usuarios = User.objects.all().order_by('-date_joined')
    context = {
        'usuarios': usuarios,
        'active_page': 'admin',
    }
    return render(request, 'administracion/gestionar_usuarios.html', context)
