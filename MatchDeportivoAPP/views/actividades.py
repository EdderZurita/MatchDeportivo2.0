"""Vistas de gestión de actividades deportivas."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

from ..models import Actividad, Perfil, Notificacion
from ..constants import RADIO_BUSQUEDA_DEFAULT, RADIO_TIERRA_KM, DEPORTES
from ..forms import ActividadForm
from .notificaciones import crear_notificacion_simple


def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia entre dos puntos usando Haversine. Retorna km."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return RADIO_TIERRA_KM * c


@login_required
def actividades(request):
    """Muestra actividades de otros usuarios filtradas por deporte con paginación."""
    user = request.user
    
    filtro_deporte = request.GET.get('deporte')
    
    # Solo mostrar actividades de otros usuarios (no las propias)
    actividades_query = Actividad.objects.exclude(organizador=user).select_related('organizador').prefetch_related('participantes')
    
    if filtro_deporte and filtro_deporte != '':
        actividades_query = actividades_query.filter(deporte=filtro_deporte)
    
    # Ordenar por fecha de creación (más recientes primero)
    actividades_query = actividades_query.order_by('-creada_en')

    # Paginación
    paginator = Paginator(actividades_query, 10)  # 10 actividades por página
    page = request.GET.get('page')
    
    try:
        actividades_paginadas = paginator.page(page)
    except PageNotAnInteger:
        actividades_paginadas = paginator.page(1)
    except EmptyPage:
        actividades_paginadas = paginator.page(paginator.num_pages)

    context = {
        'actividades': actividades_paginadas,
        'active_page': 'actividades',
        'deporte_seleccionado': filtro_deporte, 
    }
    return render(request, 'actividades/actividades.html', context)


@login_required
def detalle_actividad(request, pk):
    """Muestra el detalle de una actividad."""
    actividad = get_object_or_404(Actividad, pk=pk)
    context = {
        'actividad': actividad,
        'active_page': 'actividades',
    }
    return render(request, 'actividades/detalle_actividad.html', context)


@login_required
def crear_actividad(request):
    """Crea una nueva actividad y notifica a usuarios cercanos."""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == "POST":
        form = ActividadForm(request.POST)
        if form.is_valid():
            try:
                actividad = form.save(commit=False)
                actividad.organizador = request.user
                actividad.save()
                
                logger.info(f"Actividad creada: {actividad.titulo} por {request.user.username}")
                messages.success(request, f"✅ ¡La actividad '{actividad.titulo}' se ha creado con éxito!")
                
                # Notificación de actividad cercana deshabilitada temporalmente
                # (requiere coordenadas geográficas)
                # try:
                #     crear_notificacion_actividad_cercana(actividad)
                # except Exception as e:
                #     logger.warning(f"Error al notificar usuarios cercanos: {e}")
                    
                return redirect('actividades')
                
            except Exception as e:
                logger.error(f"Error al crear actividad: {e}", exc_info=True)
                messages.error(request, f"❌ Ocurrió un error inesperado: {str(e)}")
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ActividadForm()
    
    context = {
        'form': form,
        'deportes': DEPORTES,
        'active_page': 'crear_actividad'
    }
    return render(request, "actividades/crear_actividad.html", context)



def crear_notificacion_actividad_cercana(actividad):
    """Notifica a usuarios cercanos sobre una nueva actividad."""
    try:
        act_lat = float(actividad.latitud)
        act_lng = float(actividad.longitud)
    except (TypeError, ValueError):
        return

    perfiles_a_notificar = Perfil.objects.filter(
        disciplina_preferida__iexact=actividad.deporte
    ).exclude(usuario=actividad.organizador)

    usuarios_cercanos = []
    
    for perfil in perfiles_a_notificar:
        if perfil.latitud is not None and perfil.longitud is not None and perfil.radio is not None:
            try:
                user_lat = float(perfil.latitud)
                user_lng = float(perfil.longitud)
                radio = perfil.radio
                
                distancia = calcular_distancia_haversine(user_lat, user_lng, act_lat, act_lng)
                
                if distancia <= radio:
                    usuarios_cercanos.append({
                        'usuario': perfil.usuario,
                        'distancia': round(distancia, 1)
                    })
                    
            except Exception as e:
                pass
        else:
            pass

    if usuarios_cercanos:
        deporte_formateado = actividad.deporte.capitalize()
        
        for item in usuarios_cercanos:
            usuario = item['usuario']
            distancia = item['distancia']
            
            try:
                Notificacion.objects.create(
                    usuario=usuario,
                    actividad=actividad,
                    tipo='NUEVA_ACTIVIDAD',
                    mensaje=f"¡Nueva actividad de {deporte_formateado} cerca de ti! {actividad.titulo} a {distancia} km."
                )
            except Exception as e:
                pass


@login_required
def editar_actividad(request, pk):
    """Edita una actividad existente. Solo el organizador puede editar."""
    import logging
    logger = logging.getLogger(__name__)
    
    actividad = get_object_or_404(Actividad, pk=pk)
    
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para editar esta actividad.")
        raise PermissionDenied("Acceso denegado: No eres el organizador.")

    if request.method == "POST":
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            try:
                # Validación adicional: cupos no pueden ser menores a participantes actuales
                participantes_actuales = actividad.participantes.count()
                cupos_nuevos = form.cleaned_data['cupos']
                
                if cupos_nuevos < participantes_actuales:
                    messages.error(request, f"❌ Los cupos no pueden ser menores a los participantes actuales ({participantes_actuales})")
                    return redirect('editar_actividad', pk=pk)
                
                actividad = form.save()
                logger.info(f"Actividad editada: {actividad.titulo} por {request.user.username}")
                messages.success(request, f"✅ Actividad '{actividad.titulo}' actualizada con éxito")
                return redirect('mis_actividades')
                
            except Exception as e:
                logger.error(f"Error al editar actividad: {e}", exc_info=True)
                messages.error(request, f"❌ Error al guardar: {str(e)}")
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ActividadForm(instance=actividad)
            
    context = {
        'actividad': actividad,
        'form': form,
        'deportes': DEPORTES,
    }
    return render(request, 'actividades/editar_actividad.html', context)



@login_required
def cerrar_actividad(request, pk):
    """Cierra una actividad. Solo el organizador puede cerrar."""
    from django.utils import timezone
    
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # Verificar permisos
    if actividad.organizador != request.user:
        messages.error(request, "❌ Solo el organizador puede cerrar la actividad")
        raise PermissionDenied("No eres el organizador")
    
    # Verificar que no esté ya cerrada
    if actividad.cerrada:
        messages.warning(request, "⚠️ Esta actividad ya está cerrada")
        return redirect('detalle_actividad', pk=pk)
    
    if request.method == "POST":
        actividad.cerrada = True
        actividad.fecha_cierre = timezone.now()
        actividad.save()
        
        messages.success(request, "✅ Actividad cerrada. Ahora los participantes pueden valorarse mutuamente")
        return redirect('detalle_actividad', pk=pk)
    
    # Mostrar confirmación
    context = {
        'actividad': actividad,
        'participantes_count': actividad.participantes.count()
    }
    return render(request, 'actividades/confirmar_cierre.html', context)


@login_required
def valorar_participantes(request, pk):
    """Muestra lista de participantes de una actividad cerrada para valorar."""
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # Verificar que la actividad esté cerrada
    if not actividad.cerrada:
        messages.error(request, "❌ Solo puedes valorar participantes de actividades cerradas")
        return redirect('detalle_actividad', pk=pk)
    
    # Verificar que el usuario participó o es el organizador
    es_organizador = request.user == actividad.organizador
    es_participante = request.user in actividad.participantes.all()
    
    if not es_organizador and not es_participante:
        messages.error(request, "❌ Solo los participantes pueden valorar")
        return redirect('detalle_actividad', pk=pk)
    
    # Obtener todos los usuarios a valorar (participantes + organizador, excluyendo al usuario actual)
    from django.db.models import Q
    usuarios_a_valorar = []
    
    # Si el usuario es participante (no organizador), puede valorar al organizador
    if es_participante and not es_organizador:
        usuarios_a_valorar.append(actividad.organizador)
    
    # Agregar participantes (excluyendo al usuario actual)
    for participante in actividad.participantes.exclude(pk=request.user.pk):
        usuarios_a_valorar.append(participante)
    
    # Marcar quiénes ya fueron valorados
    from ..models import Valoracion
    participantes_data = []
    for usuario in usuarios_a_valorar:
        ya_valorado = Valoracion.objects.filter(
            evaluador=request.user,
            evaluado=usuario,
            actividad=actividad
        ).exists()
        
        valoracion_existente = None
        if ya_valorado:
            valoracion_existente = Valoracion.objects.get(
                evaluador=request.user,
                evaluado=usuario,
                actividad=actividad
            )
        
        participantes_data.append({
            'usuario': usuario,
            'ya_valorado': ya_valorado,
            'valoracion': valoracion_existente
        })
    
    context = {
        'actividad': actividad,
        'participantes': participantes_data
    }
    return render(request, 'actividades/valorar_participantes.html', context)


@login_required
def eliminar_actividad(request, pk):
    """Elimina una actividad. Solo el organizador puede eliminar."""
    actividad = get_object_or_404(Actividad, pk=pk)
    
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para eliminar esta actividad.")
        return redirect('detalle_actividad', pk=pk)

    try:
        actividad.delete()
        messages.success(request, f"La actividad '{actividad.titulo}' ha sido eliminada permanentemente.")
        return redirect('actividades')
    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar la actividad: {e}")
        return redirect('detalle_actividad', pk=pk)


@login_required
def mis_actividades(request):
    """Muestra actividades organizadas y en las que participa el usuario."""
    usuario = request.user
    
    actividades_organizadas = Actividad.objects.filter(
        organizador=usuario
    ).order_by('fecha', 'hora_inicio')
    
    actividades_participando = (
        usuario.actividades_participando.all()
        .exclude(organizador=usuario)
        .order_by('fecha', 'hora_inicio')
    )
    
    context = {
        'organizadas': actividades_organizadas,
        'participando': actividades_participando, 
        'active_page': 'mis_actividades',
    }
    
    return render(request, 'actividades/mis_actividades.html', context)


@login_required
def unirse_actividad(request, pk):
    """Permite unirse a una actividad si hay cupos disponibles."""
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user
    
    try:
        with transaction.atomic():
            if actividad.participantes.filter(id=usuario.id).exists():
                messages.warning(request, "Ya estás inscrito en esta actividad.")
                return redirect('detalle_actividad', pk=pk)
            
            if actividad.cupos > 0:
                actividad.participantes.add(usuario)
                actividad.cupos -= 1
                actividad.save()
                
                messages.success(request, f"¡Te has unido a {actividad.titulo} con éxito!")
                
                crear_notificacion_simple(
                    usuario, 
                    actividad, 
                    'CONFIRMACION_UNION', 
                    f"¡Confirmado! Estás inscrito en {actividad.titulo} el {actividad.fecha}."
                )
            else:
                messages.error(request, "No hay cupos disponibles.")

    except Exception as e:
        messages.error(request, f"Ocurrió un error al unirse: {e}")
        
    return redirect('detalle_actividad', pk=pk)


@login_required
def salir_actividad(request, pk):
    """Permite salir de una actividad y libera un cupo."""
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user

    try:
        with transaction.atomic():
            if actividad.participantes.filter(id=usuario.id).exists():
                actividad.participantes.remove(usuario)
                actividad.cupos += 1
                actividad.save()
                messages.success(request, f"Has cancelado tu asistencia a {actividad.titulo}. ¡Cupo liberado!")
            else:
                messages.warning(request, "No estabas unido a esta actividad.")

    except Exception as e:
        messages.error(request, f"Ocurrió un error al intentar salir de la actividad: {e}")
        
    return redirect('detalle_actividad', pk=pk)


@login_required
def gestionar_participantes(request, pk):
    """Gestiona participantes de una actividad. Solo el organizador puede acceder."""
    actividad = get_object_or_404(Actividad, pk=pk)
    
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para administrar esta actividad.")
        return redirect('detalle_actividad', pk=pk)

    participantes = []
    for usuario in actividad.participantes.all():
        participantes.append({
            'user': usuario,
            'perfil': getattr(usuario, 'perfil', None),
        })

    context = {
        'actividad': actividad,
        'participantes': participantes,
    }
    return render(request, 'actividades/gestionar_participantes.html', context)


@login_required
def quitar_participante(request, actividad_pk, user_id):
    """Quita un participante de una actividad. Solo el organizador puede hacerlo."""
    actividad = get_object_or_404(Actividad, pk=actividad_pk)
    usuario_a_quitar = get_object_or_404(User, pk=user_id)
    
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('gestionar_participantes', pk=actividad_pk)

    try:
        with transaction.atomic():
            actividad.participantes.remove(usuario_a_quitar)
            actividad.cupos += 1
            actividad.save()
            messages.success(request, f"Se ha quitado a {usuario_a_quitar.username} de la actividad y se liberó un cupo.")
    except Exception as e:
        messages.error(request, f"Error al quitar participante: {e}")

    return redirect('gestionar_participantes', pk=actividad_pk)


@login_required
def reseña_actividad(request):
    """Vista de reseña de actividad (funcionalidad futura)."""
    return render(request, "actividades/reseña_actividad.html")

@login_required
def valorar_usuario(request, actividad_pk, usuario_pk):
    """Permite valorar a un usuario después de participar juntos en una actividad."""
    from ..models import Valoracion
    
    actividad = get_object_or_404(Actividad, pk=actividad_pk)
    usuario_a_valorar = get_object_or_404(User, pk=usuario_pk)
    evaluador = request.user
    
    # Validación 0: La actividad debe estar cerrada
    if not actividad.cerrada:
        messages.error(request, "❌ Solo puedes valorar después de que la actividad esté cerrada")
        return redirect('detalle_actividad', pk=actividad_pk)
    
    # Validación 1: No puedes valorarte a ti mismo
    if evaluador == usuario_a_valorar:
        messages.error(request, "No puedes valorarte a ti mismo.")
        return redirect('detalle_actividad', pk=actividad_pk)
    
    # Validación 2: Ambos deben haber participado en la actividad
    participantes = list(actividad.participantes.all()) + [actividad.organizador]
    if evaluador not in participantes or usuario_a_valorar not in participantes:
        messages.error(request, "Solo los participantes de la actividad pueden valorarse entre sí.")
        return redirect('detalle_actividad', pk=actividad_pk)
    
    # Validación 3: Verificar si ya existe una valoración
    valoracion_existente = Valoracion.objects.filter(
        evaluador=evaluador,
        evaluado=usuario_a_valorar,
        actividad=actividad
    ).first()
    
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario', '').strip()
        
        # Validar puntuación
        try:
            puntuacion = int(puntuacion)
            if puntuacion < 1 or puntuacion > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "La puntuación debe ser un número entre 1 y 5.")
            return redirect('valorar_usuario', actividad_pk=actividad_pk, usuario_pk=usuario_pk)
        
        # Crear o actualizar valoración
        if valoracion_existente:
            valoracion_existente.puntuacion = puntuacion
            valoracion_existente.comentario = comentario
            valoracion_existente.save()
            messages.success(request, f"Has actualizado tu valoración de {usuario_a_valorar.username}.")
        else:
            Valoracion.objects.create(
                evaluador=evaluador,
                evaluado=usuario_a_valorar,
                actividad=actividad,
                puntuacion=puntuacion,
                comentario=comentario
            )
            messages.success(request, f"Has valorado exitosamente a {usuario_a_valorar.username}.")
        
        return redirect('detalle_actividad', pk=actividad_pk)
    
    # GET: Mostrar formulario
    context = {
        'actividad': actividad,
        'usuario_a_valorar': usuario_a_valorar,
        'valoracion_existente': valoracion_existente,
    }
    return render(request, 'actividades/valorar_usuario.html', context)