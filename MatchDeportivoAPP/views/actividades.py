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
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        deporte = request.POST.get("deporte", "").strip()
        lugar_texto = request.POST.get("lugar", "").strip()
        fecha_str = request.POST.get("fecha")
        hora_inicio_str = request.POST.get("hora_inicio")
        hora_fin_str = request.POST.get("hora_fin")
        nivel = request.POST.get("nivel", "").strip()
        cupos_str = request.POST.get("cupos", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not all([titulo, deporte, lugar_texto, fecha_str, hora_inicio_str, cupos_str]):
            messages.error(request, "Por favor, completa todos los campos obligatorios.")
            return render(request, "actividades/crear_actividad.html")

        try:
            from datetime import date, datetime, time as time_module
            
            # Validar y convertir cupos
            cupos = int(cupos_str)
            if cupos < 1 or cupos > 50:
                messages.error(request, "❌ Los cupos deben estar entre 1 y 50")
                return render(request, "actividades/crear_actividad.html")
            
            # Convertir fecha y horas
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time() if hora_fin_str else None
            
            # Validación 1: Fecha no puede ser pasada
            if fecha < date.today():
                messages.error(request, "❌ No puedes crear actividades en fechas pasadas")
                return render(request, "actividades/crear_actividad.html")
            
            # Validación 2: Si la fecha es hoy, la hora debe ser futura
            if fecha == date.today():
                hora_actual = datetime.now().time()
                if hora_inicio <= hora_actual:
                    messages.error(request, "❌ La hora de inicio debe ser futura (hora actual: {})".format(
                        hora_actual.strftime('%H:%M')
                    ))
                    return render(request, "actividades/crear_actividad.html")
            
            # Validación 3: Hora fin debe ser posterior a hora inicio
            if hora_fin and hora_fin <= hora_inicio:
                messages.error(request, "❌ La hora de fin debe ser posterior a la hora de inicio")
                return render(request, "actividades/crear_actividad.html")
            
            nueva_actividad = Actividad.objects.create(
                organizador=request.user, 
                titulo=titulo,
                deporte=deporte,
                lugar=lugar_texto,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                nivel=nivel,
                cupos=cupos,
                descripcion=descripcion,
            )

            messages.success(request, f"✅ ¡La actividad '{titulo}' se ha creado con éxito!")
            
            # Notificación de actividad cercana deshabilitada temporalmente
            # (requiere coordenadas geográficas)
            # try:
            #     crear_notificacion_actividad_cercana(nueva_actividad)
            # except Exception as e:
            #     pass
                
            return redirect('actividades')

        except ValueError as e:
            messages.error(request, f"❌ Error en el formato de los datos: {str(e)}")
            return render(request, "actividades/crear_actividad.html")
        except Exception as e:
            messages.error(request, f"❌ Ocurrió un error inesperado: {str(e)}")
            return render(request, "actividades/crear_actividad.html")
            
    return render(request, "actividades/crear_actividad.html")


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
    actividad = get_object_or_404(Actividad, pk=pk)
    
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para editar esta actividad.")
        raise PermissionDenied("Acceso denegado: No eres el organizador.")

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        deporte = request.POST.get("deporte", "").strip()
        lugar_texto = request.POST.get("lugar", "").strip()
        fecha_str = request.POST.get("fecha")
        hora_inicio_str = request.POST.get("hora_inicio")
        hora_fin_str = request.POST.get("hora_fin")
        nivel = request.POST.get("nivel", "").strip()
        cupos_str = request.POST.get("cupos", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not all([titulo, deporte, lugar_texto, fecha_str, hora_inicio_str, cupos_str]):
            messages.error(request, "Faltan campos obligatorios.")
            return redirect('editar_actividad', pk=pk)

        try:
            from datetime import date, datetime
            
            # Validar y convertir cupos
            cupos = int(cupos_str)
            participantes_actuales = actividad.participantes.count()
            
            if cupos < participantes_actuales:
                messages.error(request, f"❌ Los cupos no pueden ser menores a los participantes actuales ({participantes_actuales})")
                return redirect('editar_actividad', pk=pk)
            
            if cupos > 50:
                messages.error(request, "❌ Los cupos no pueden ser mayores a 50")
                return redirect('editar_actividad', pk=pk)
            
            # Convertir fecha y horas
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time() if hora_fin_str else None
            
            # Validación 1: Fecha no puede ser pasada
            if fecha < date.today():
                messages.error(request, "❌ No puedes programar actividades en fechas pasadas")
                return redirect('editar_actividad', pk=pk)
            
            # Validación 2: Si la fecha es hoy, la hora debe ser futura
            if fecha == date.today():
                hora_actual = datetime.now().time()
                if hora_inicio <= hora_actual:
                    messages.error(request, "❌ La hora de inicio debe ser futura (hora actual: {})".format(
                        hora_actual.strftime('%H:%M')
                    ))
                    return redirect('editar_actividad', pk=pk)
            
            # Validación 3: Hora fin debe ser posterior a hora inicio
            if hora_fin and hora_fin <= hora_inicio:
                messages.error(request, "❌ La hora de fin debe ser posterior a la hora de inicio")
                return redirect('editar_actividad', pk=pk)
            
            # Actualizar actividad
            actividad.titulo = titulo
            actividad.deporte = deporte
            actividad.lugar = lugar_texto
            actividad.fecha = fecha
            actividad.hora_inicio = hora_inicio
            actividad.hora_fin = hora_fin
            actividad.nivel = nivel
            actividad.cupos = cupos
            actividad.descripcion = descripcion
            
            actividad.save()
            messages.success(request, f"✅ Actividad '{actividad.titulo}' actualizada con éxito")
            return redirect('mis_actividades')

        except ValueError as e:
            messages.error(request, f"❌ Error en el formato de datos: {str(e)}")
        except Exception as e:
            messages.error(request, f"❌ Error al guardar: {str(e)}")
            
    context = {
        'actividad': actividad,
        'deportes': ['futbol', 'basketball', 'skate', 'volibol', 'running', 'tenis'],
    }
    return render(request, 'actividades/editar_actividad.html', context)


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