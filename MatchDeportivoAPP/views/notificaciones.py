"""Vistas de notificaciones."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import Notificacion


@login_required
def notificaciones(request):
    """Muestra todas las notificaciones del usuario."""
    usuario = request.user
    notificaciones_list = Notificacion.objects.filter(usuario=usuario)
    
    no_leidas = notificaciones_list.filter(leida=False)
    leidas = notificaciones_list.filter(leida=True)
    
    context = {
        'notificaciones': notificaciones_list,
        'no_leidas': no_leidas,
        'leidas': leidas,
        'active_page': 'notificaciones',
    }
    
    return render(request, 'usuarios/notificaciones.html', context)


@login_required
def lista_notificaciones(request):
    """Lista de notificaciones (funcionalidad futura)."""
    return render(request, 'notificaciones/lista_notificaciones.html')


@login_required
def marcar_todas_leidas(request):
    """Marca todas las notificaciones del usuario como leídas."""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Actualizar todas las notificaciones no leídas del usuario
    count = Notificacion.objects.filter(
        usuario=request.user, 
        leida=False
    ).update(leida=True)
    
    if count > 0:
        messages.success(request, f"✅ {count} notificación(es) marcada(s) como leída(s)")
    else:
        messages.info(request, "ℹ️ No tienes notificaciones sin leer")
    
    return redirect('notificaciones')


def crear_notificacion_simple(usuario, actividad, tipo, mensaje):
    """Crea una notificación simple para un usuario."""
    try:
        Notificacion.objects.create(
            usuario=usuario,
            actividad=actividad,
            tipo=tipo,
            mensaje=mensaje
        )
    except Exception as e:
        pass
