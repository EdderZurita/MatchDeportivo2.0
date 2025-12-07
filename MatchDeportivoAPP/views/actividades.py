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
    """Muestra actividades filtradas por deporte y distancia con paginación."""
    user = request.user
    perfil = user.perfil
    
    filtro_deporte = request.GET.get('deporte')
    
    actividades_query = Actividad.objects.all()
    if filtro_deporte and filtro_deporte != '':
        actividades_query = actividades_query.filter(deporte=filtro_deporte)
        
    mis_actividades = actividades_query.filter(organizador=user)
    actividades_de_otros = list(actividades_query.exclude(organizador=user))
    actividades_finales = list(mis_actividades)
    
    user_lat = perfil.latitud
    user_lng = perfil.longitud
    search_radius = perfil.radio if perfil.radio is not None else RADIO_BUSQUEDA_DEFAULT

    if user_lat is None or user_lng is None:
        actividades_finales.extend(actividades_de_otros)
        messages.info(request, "Configura tu ubicación en tu perfil para ver actividades cercanas y ordenadas.")
    else:
        try:
            user_lat_float = float(user_lat)
            user_lng_float = float(user_lng)
        except (TypeError, ValueError):
            messages.warning(request, "Las coordenadas de tu perfil no son válidas. Revisa tu ubicación.")
            user_lat_float = None

        actividades_cercanas_y_filtradas = []
        
        if user_lat_float is not None:
            for actividad in actividades_de_otros:
                if actividad.latitud and actividad.longitud:
                    act_lat = float(actividad.latitud)
                    act_lng = float(actividad.longitud)
                    
                    distancia = calcular_distancia_haversine(
                        user_lat_float, user_lng_float, act_lat, act_lng
                    )
                    
                    if distancia <= search_radius:
                        actividad.distancia_km = round(distancia, 1)
                        actividades_cercanas_y_filtradas.append(actividad)
            
            actividades_cercanas_y_filtradas = sorted(
                actividades_cercanas_y_filtradas, 
                key=lambda a: a.distancia_km
            )

            actividades_finales.extend(actividades_cercanas_y_filtradas)

    # Paginación
    paginator = Paginator(actividades_finales, 10)  # 10 actividades por página
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
        'ubicacion_configurada': user_lat is not None, 
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
        lat_str = request.POST.get("latitud_actividad", "").strip()
        lng_str = request.POST.get("longitud_actividad", "").strip()
        fecha_str = request.POST.get("fecha")
        hora_inicio_str = request.POST.get("hora_inicio")
        hora_fin_str = request.POST.get("hora_fin")
        nivel = request.POST.get("nivel", "").strip()
        cupos_str = request.POST.get("cupos", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not all([titulo, deporte, lugar_texto, lat_str, lng_str, fecha_str, hora_inicio_str, cupos_str]):
            messages.error(request, "Por favor, completa todos los campos obligatorios y selecciona una ubicación válida con el autocompletado.")
            return render(request, "actividades/crear_actividad.html")

        try:
            cupos = int(cupos_str)
            latitud = float(lat_str)
            longitud = float(lng_str)
            
            nueva_actividad = Actividad.objects.create(
                organizador=request.user, 
                titulo=titulo,
                deporte=deporte,
                lugar=lugar_texto,
                latitud=latitud,
                longitud=longitud,
                fecha=fecha_str,
                hora_inicio=hora_inicio_str,
                hora_fin=hora_fin_str if hora_fin_str else None,
                nivel=nivel,
                cupos=cupos,
                descripcion=descripcion,
            )

            messages.success(request, f"¡La actividad '{titulo}' se ha creado con éxito!")
            
            try:
                crear_notificacion_actividad_cercana(nueva_actividad)
            except Exception as e:
                pass
                
            return redirect('actividades')

        except ValueError:
            messages.error(request, "Error en el formato de los datos (cupos, latitud o longitud son inválidos).")
            return render(request, "actividades/crear_actividad.html")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado al guardar la actividad: {e}")
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
        lat_str = request.POST.get("latitud_actividad", "").strip()
        lng_str = request.POST.get("longitud_actividad", "").strip()
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
            actividad.titulo = titulo
            actividad.deporte = deporte
            actividad.lugar = lugar_texto
            actividad.fecha = fecha_str
            actividad.hora_inicio = hora_inicio_str
            actividad.hora_fin = hora_fin_str if hora_fin_str else None
            actividad.nivel = nivel
            actividad.cupos = int(cupos_str)
            actividad.descripcion = descripcion
            
            if lat_str and lng_str:
                actividad.latitud = float(lat_str)
                actividad.longitud = float(lng_str)
            
            actividad.save()
            messages.success(request, f"Actividad '{actividad.titulo}' actualizada con éxito.")
            return redirect('mis_actividades')

        except ValueError:
            messages.error(request, "Error en el formato de datos numéricos o fecha/hora.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
            
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
