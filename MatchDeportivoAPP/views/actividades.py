"""
Vistas de gestión de actividades deportivas.
Incluye CRUD completo, sistema de participantes y geolocalización.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

from ..models import Actividad, Perfil, Notificacion
from .notificaciones import crear_notificacion_simple


def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine.
    
    Args:
        lat1: Latitud del punto 1
        lon1: Longitud del punto 1
        lat2: Latitud del punto 2
        lon2: Longitud del punto 2
        
    Returns:
        float: Distancia en kilómetros
    """
    # Radio de la Tierra en kilómetros
    R = 6371 
    
    # Convertir grados a radianes
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Diferencia en coordenadas
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Fórmula de Haversine
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = R * c
    
    return km


@login_required
def actividades(request):
    """
    Vista principal de actividades deportivas.
    Muestra actividades filtradas por deporte y distancia.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de actividades
    """
    user = request.user
    perfil = user.perfil
    
    # Obtener filtro de deporte
    filtro_deporte = request.GET.get('deporte')
    
    # Obtener todas las actividades, potencialmente filtradas por deporte
    actividades_query = Actividad.objects.all()
    if filtro_deporte and filtro_deporte != '':
        actividades_query = actividades_query.filter(deporte=filtro_deporte)
        
    # Separar actividades: Propias vs. De otros
    mis_actividades = actividades_query.filter(organizador=user)
    actividades_de_otros = list(actividades_query.exclude(organizador=user))

    # La lista final comienza con las actividades propias (siempre visibles)
    actividades_finales = list(mis_actividades)
    
    # Obtener datos de ubicación del usuario
    user_lat = perfil.latitud
    user_lng = perfil.longitud
    search_radius = perfil.radio if perfil.radio is not None else 50 

    # Aplicar lógica de distancia (solo a actividades_de_otros)
    if user_lat is None or user_lng is None:
        # Si no hay ubicación, mostramos TODAS las actividades filtradas por deporte
        actividades_finales.extend(actividades_de_otros)
        messages.info(request, "Configura tu ubicación en tu perfil para ver actividades cercanas y ordenadas.")
    else:
        # Conversión de tipos para Haversine
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
                    
                    # Calcular la distancia
                    distancia = calcular_distancia_haversine(
                        user_lat_float, user_lng_float, act_lat, act_lng
                    )
                    
                    # Aplicar el filtro de radio
                    if distancia <= search_radius:
                        actividad.distancia_km = round(distancia, 1) 
                        actividades_cercanas_y_filtradas.append(actividad)
            
            # Ordenar las actividades cercanas de otros
            actividades_cercanas_y_filtradas = sorted(
                actividades_cercanas_y_filtradas, 
                key=lambda a: a.distancia_km
            )

            # Combinar: Mis actividades (siempre) + Actividades cercanas y ordenadas
            actividades_finales.extend(actividades_cercanas_y_filtradas)

    context = {
        'actividades': actividades_finales,
        'active_page': 'actividades',
        'deporte_seleccionado': filtro_deporte,
        'ubicacion_configurada': user_lat is not None, 
    }
    return render(request, 'actividades/actividades.html', context)


@login_required
def detalle_actividad(request, pk):
    """
    Vista de detalle de una actividad específica.
    
    Args:
        request: HttpRequest object
        pk: ID de la actividad
        
    Returns:
        HttpResponse con el template de detalle
    """
    actividad = get_object_or_404(Actividad, pk=pk)
    
    context = {
        'actividad': actividad,
        'active_page': 'actividades',
    }
    
    return render(request, 'actividades/detalle_actividad.html', context)


@login_required
def crear_actividad(request):
    """
    Vista para crear una nueva actividad deportiva.
    Incluye validación de datos y notificación a usuarios cercanos.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de creación o redirección
    """
    if request.method == "POST":
        # Capturar todos los datos del formulario
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

        # Validar datos críticos y ubicación
        if not all([titulo, deporte, lugar_texto, lat_str, lng_str, fecha_str, hora_inicio_str, cupos_str]):
            messages.error(request, "Por favor, completa todos los campos obligatorios y selecciona una ubicación válida con el autocompletado.")
            return render(request, "actividades/crear_actividad.html")

        try:
            # Convertir campos a sus tipos correctos
            cupos = int(cupos_str)
            latitud = float(lat_str)
            longitud = float(lng_str)
            
            # Crear el objeto Actividad y capturar la instancia
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
            
            # Llamada a la notificación
            try:
                crear_notificacion_actividad_cercana(nueva_actividad)
            except Exception as e:
                # Error al notificar, pero no afecta la creación de la actividad
                pass
                
            return redirect('actividades')

        except ValueError:
            messages.error(request, "Error en el formato de los datos (cupos, latitud o longitud son inválidos).")
            return render(request, "actividades/crear_actividad.html")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado al guardar la actividad: {e}")
            return render(request, "actividades/crear_actividad.html")
            
    # Retorno para solicitud GET (carga inicial del formulario)
    return render(request, "actividades/crear_actividad.html")


def crear_notificacion_actividad_cercana(actividad):
    """
    Crea notificaciones para usuarios cercanos cuando se crea una actividad.
    
    Args:
        actividad: Instancia de Actividad recién creada
        
    Returns:
        None
    """
    # Obtener coordenadas de la nueva actividad
    try:
        act_lat = float(actividad.latitud)
        act_lng = float(actividad.longitud)
    except (TypeError, ValueError):
        return 

    # Filtrar perfiles por deporte y excluir al organizador
    perfiles_a_notificar = Perfil.objects.filter(
        disciplina_preferida__iexact=actividad.deporte
    ).exclude(usuario=actividad.organizador)

    usuarios_cercanos = []
    
    # Iterar y aplicar el filtro de distancia
    for perfil in perfiles_a_notificar:
        
        # Verificación estricta de que todos los campos de ubicación no sean None
        if perfil.latitud is not None and perfil.longitud is not None and perfil.radio is not None:
            try:
                user_lat = float(perfil.latitud)
                user_lng = float(perfil.longitud)
                radio = perfil.radio
                
                # Calcular la distancia
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

    # Creación de las notificaciones
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
    """
    Vista para editar una actividad existente.
    Solo el organizador puede editar.
    
    Args:
        request: HttpRequest object
        pk: ID de la actividad
        
    Returns:
        HttpResponse con el template de edición o redirección
    """
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # Seguridad: Solo el organizador puede editar
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para editar esta actividad.")
        raise PermissionDenied("Acceso denegado: No eres el organizador.")

    if request.method == "POST":
        # Capturar y validar datos
        titulo = request.POST.get("titulo", "").strip() 
        deporte = request.POST.get("deporte", "").strip()
        lugar_texto = request.POST.get("lugar", "").strip()
        
        # Geocodificación
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
            # Actualizar el objeto con los nuevos valores
            actividad.titulo = titulo
            actividad.deporte = deporte
            actividad.lugar = lugar_texto
            actividad.fecha = fecha_str
            actividad.hora_inicio = hora_inicio_str
            actividad.hora_fin = hora_fin_str if hora_fin_str else None
            actividad.nivel = nivel
            actividad.cupos = int(cupos_str)
            actividad.descripcion = descripcion
            
            # Actualizar Coordenadas si fueron modificadas
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
            
    # Lógica de GET (Mostrar Formulario con datos precargados)
    context = {
        'actividad': actividad,
        'deportes': ['futbol', 'basketball', 'skate', 'volibol', 'running', 'tenis'],
    }
    return render(request, 'actividades/editar_actividad.html', context)


@login_required
def eliminar_actividad(request, pk):
    """
    Vista para eliminar una actividad.
    Solo el organizador puede eliminar.
    
    Args:
        request: HttpRequest object
        pk: ID de la actividad
        
    Returns:
        HttpResponse con redirección
    """
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # Verificar si el usuario es el organizador
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para eliminar esta actividad.")
        return redirect('detalle_actividad', pk=pk)

    # Manejar la eliminación
    try:
        actividad.delete()
        messages.success(request, f"La actividad '{actividad.titulo}' ha sido eliminada permanentemente.")
        return redirect('actividades')

    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar la actividad: {e}")
        return redirect('detalle_actividad', pk=pk)


@login_required
def mis_actividades(request):
    """
    Vista de actividades del usuario autenticado.
    Muestra actividades organizadas y en las que participa.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de mis actividades
    """
    usuario = request.user
    
    # Actividades que el usuario CREÓ (Organizadas)
    actividades_organizadas = Actividad.objects.filter(
        organizador=usuario
    ).order_by('fecha', 'hora_inicio')
    
    # Actividades en las que el usuario PARTICIPA
    # Excluimos las que organiza, para que no se dupliquen
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
    """
    Vista para unirse a una actividad.
    Valida cupos disponibles y crea notificación.
    
    Args:
        request: HttpRequest object
        pk: ID de la actividad
        
    Returns:
        HttpResponse con redirección
    """
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user
    
    try:
        with transaction.atomic():
            # Verificar si ya es participante
            if actividad.participantes.filter(id=usuario.id).exists():
                messages.warning(request, "Ya estás inscrito en esta actividad.")
                return redirect('detalle_actividad', pk=pk)
            
            # Verificar cupos disponibles
            if actividad.cupos > 0:
                actividad.participantes.add(usuario)
                actividad.cupos -= 1
                actividad.save()
                
                messages.success(request, f"¡Te has unido a {actividad.titulo} con éxito!")
                
                # Crear notificación de confirmación
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
    """
    Vista para salir de una actividad.
    Libera un cupo.
    
    Args:
        request: HttpRequest object
        pk: ID de la actividad
        
    Returns:
        HttpResponse con redirección
    """
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user

    try:
        with transaction.atomic():
            # Verificar si el usuario es participante
            if actividad.participantes.filter(id=usuario.id).exists():
                # Remover el participante
                actividad.participantes.remove(usuario)
                
                # Aumentar el cupo
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
    """
    Vista para gestionar participantes de una actividad.
    Solo el organizador puede acceder.
    
    Args:
        request: HttpRequest object
        pk: ID de la actividad
        
    Returns:
        HttpResponse con el template de gestión
    """
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # Seguridad: Solo el organizador puede gestionar la lista
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para administrar esta actividad.")
        return redirect('detalle_actividad', pk=pk)

    # Obtener la lista de participantes con su perfil asociado
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
    """
    Vista para quitar a un participante de una actividad.
    Solo el organizador puede quitar participantes.
    
    Args:
        request: HttpRequest object
        actividad_pk: ID de la actividad
        user_id: ID del usuario a quitar
        
    Returns:
        HttpResponse con redirección
    """
    actividad = get_object_or_404(Actividad, pk=actividad_pk)
    usuario_a_quitar = get_object_or_404(User, pk=user_id)
    
    # Seguridad: Solo el organizador puede quitar participantes
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('gestionar_participantes', pk=actividad_pk)

    # Lógica de remoción
    try:
        with transaction.atomic():
            # Remover de la relación ManyToMany
            actividad.participantes.remove(usuario_a_quitar)
            
            # Devolver el cupo
            actividad.cupos += 1
            actividad.save()
            
            messages.success(request, f"Se ha quitado a {usuario_a_quitar.username} de la actividad y se liberó un cupo.")
    
    except Exception as e:
        messages.error(request, f"Error al quitar participante: {e}")

    return redirect('gestionar_participantes', pk=actividad_pk)


@login_required
def reseña_actividad(request):
    """
    Vista de reseña de actividad (funcionalidad futura).
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template de reseña
    """
    return render(request, "actividades/reseña_actividad.html")
