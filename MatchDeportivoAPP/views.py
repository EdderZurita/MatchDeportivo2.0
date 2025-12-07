from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .forms import RegistroForm, PerfilForm
from .models import Perfil

# Create your views here


def inicio(request):
    return render(request, "index.html")

def inicioSesion(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return render(request, "sesion/inicioSesion.html", {"error": "Correo incorrecto"})

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("perfil")  # Página principal del usuario
        else:
            return render(request, "sesion/inicioSesion.html", {"error": "Contraseña incorrecta"})

    return render(request, "sesion/inicioSesion.html")

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render

def olvidoContraseña(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validar contraseñas iguales
        if password1 != password2:
            return render(request, "sesion/olvidoContraseña.html", {
                "error": "Las contraseñas no coinciden."
            })

        # Buscar usuario
        try:
            usuario = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "sesion/olvidoContraseña.html", {
                "error": "Este correo no está registrado."
            })

        # Cambiar contraseña de forma segura
        usuario.password = make_password(password1)
        usuario.save()

        return render(request, "sesion/olvidoContraseña.html", {
            "success": "Tu contraseña ha sido cambiada con éxito."
        })

    return render(request, "sesion/olvidoContraseña.html")




def registroSesion(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')

        # Validación de username duplicado
        if User.objects.filter(username=username).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El nombre de usuario ya está en uso',
                'request': request
            })

        # Validación de email duplicado
        if User.objects.filter(email=email).exists():
            return render(request, 'sesion/registroSesion.html', {
                'error': 'El correo ya está registrado',
                'request': request
            })

        # Crear usuario
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        # Redirigir al login
        return redirect('inicioSesion')

    return render(request, 'sesion/registroSesion.html')





@login_required
def cerrarSesion(request):
    logout(request)
    return redirect("inicioSesion")


#Usuarios

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Perfil

@login_required
def perfil(request):
    # Obtener o crear perfil del usuario
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

        # Convertir números
        try:
            if lat != "":
                perfil.latitud = float(lat)
        except:
            messages.warning(request, "Latitud inválida.")

        try:
            if lng != "":
                perfil.longitud = float(lng)
        except:
            messages.warning(request, "Longitud inválida.")

        try:
            if radio != "":
                perfil.radio = int(radio)
        except:
            messages.warning(request, "Radio inválido.")

        perfil.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("perfil")

    # Lista de iconos (tu versión corregida)
    iconos = [
        ("futbol", "img/futbol.png"),
        ("basketball", "img/basketball.png"),
        ("skate", "img/skate.png"),
        ("voleibol", "img/voleibol.png"),
        ("running", "img/running.png"),
        ("tenis", "img/tenis.png"),
    ]

    context = {
        "perfil": perfil,
        "iconos": iconos,
        "active_page": "perfil",
    }
    return render(request, "usuarios/perfil.html", context)

@login_required
def perfil_jugador(request):
    return render(request, "usuarios/perfil_jugador.html")



@login_required
def notificaciones(request):
    context = {
        'active_page': 'notificaciones',
    }
    return render(request, "usuarios/notificaciones.html", context)


@login_required
def lista_notificaciones(request):
    # 🚨 CLAVE: Cargar las notificaciones del usuario logueado
    notificaciones_usuario = Notificacion.objects.filter(usuario=request.user)
    
    context = {
        # Ambas listas son necesarias para el template
        'notificaciones': notificaciones_usuario,
        'notificaciones_sin_leer': notificaciones_usuario.filter(leida=False),
        'active_page': 'notificaciones',
    }
    # 🚨 Asegúrate de que el template que usas es 'actividades/notificaciones.html'
    return render(request, "actividades/notificaciones.html", context)

from .models import Notificacion
def crear_notificacion_simple(usuario, actividad, tipo, mensaje):
    """Crea una notificación simple para un usuario."""
    # Intentamos crear la notificación, pero usamos un try/except general para
    # no romper la transacción si hay un error menor en el mensaje o tipo.
    try:
        Notificacion.objects.create(
            usuario=usuario,
            actividad=actividad,
            tipo=tipo, # Debe ser una de las opciones válidas definidas en el modelo
            mensaje=mensaje,
            leida=False 
        )
    except Exception as e:
        print(f"ERROR: No se pudo crear la notificación para {usuario.username}. Causa: {e}")
        # La transacción principal NO debe fallar por esto, por eso el try/except local
        pass


#Actividades

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Actividad, Perfil 
from math import radians, cos, sin, asin, sqrt # Asegúrate de que Haversine esté disponible

from math import radians, cos, sin, asin, sqrt

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
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
    user = request.user
    perfil = user.perfil
    
    # 🚨 Inicializar variables para el contexto
    filtro_deporte = request.GET.get('deporte')
    
    # 1. Obtener todas las actividades, potencialmente filtradas por deporte
    actividades_query = Actividad.objects.all()
    if filtro_deporte and filtro_deporte != '':
        actividades_query = actividades_query.filter(deporte=filtro_deporte)
        
    # 2. Separar actividades: Propias vs. De otros
    mis_actividades = actividades_query.filter(organizador=user)
    actividades_de_otros = list(actividades_query.exclude(organizador=user))

    # La lista final comienza con las actividades propias (siempre visibles)
    actividades_finales = list(mis_actividades)
    
    # 3. Obtener datos de ubicación
    user_lat = perfil.latitud
    user_lng = perfil.longitud
    search_radius = perfil.radio if perfil.radio is not None else 50 

    # 4. Aplicar lógica de distancia (solo a actividades_de_otros)
    if user_lat is None or user_lng is None:
        
        # Si no hay ubicación, mostramos TODAS las actividades filtradas por deporte
        # Ya mis_actividades está en actividades_finales, solo agregamos las de otros
        actividades_finales.extend(actividades_de_otros)
        messages.info(request, "Configura tu ubicación en tu perfil para ver actividades cercanas y ordenadas.")
        
    else:
        # Conversión de tipos para Haversine ( DecimalField -> float )
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

            # 5. Combinar: Mis actividades (siempre) + Actividades cercanas y ordenadas
            actividades_finales.extend(actividades_cercanas_y_filtradas)

    context = {
        'actividades': actividades_finales, # Usamos la lista combinada y ordenada
        'active_page': 'actividades',
        'deporte_seleccionado': filtro_deporte,
        'ubicacion_configurada': user_lat is not None, 
    }
    return render(request, 'actividades/actividades.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Actividad # Asegúrate de importar tu modelo

@login_required
def detalle_actividad(request, pk): # 🚨 Debes incluir 'pk' aquí
    # 1. Obtener la actividad o mostrar 404
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # 2. Preparar el contexto
    context = {
        'actividad': actividad,
        'active_page': 'actividades',
    }
    
    # 3. Renderizar el template de detalles
    # 🚨 NOTA: Asegúrate de tener un template llamado 'detalle_actividad.html'
    return render(request, 'actividades/detalle_actividad.html', context)

from django.db import transaction
@login_required
def unirse_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user
    
    try:
        with transaction.atomic():
            
            # ... (código de verificación si ya es participante o cupos agotados) ...
            
            if actividad.cupos > 0:
                actividad.participantes.add(usuario)
                actividad.cupos -= 1
                actividad.save()
                
                messages.success(request, f"¡Te has unido a {actividad.titulo} con éxito!")
                
                # 🚨 LLAMADA A LA FUNCIÓN DE NOTIFICACIÓN 🚨
                crear_notificacion_simple(
                    usuario, 
                    actividad, 
                    'CONFIRMACION_UNION', 
                    f"¡Confirmado! Estás inscrito en {actividad.titulo} el {actividad.fecha}."
                )

    except Exception as e:
        # Aquí se imprimirá cualquier error que rompa la transacción, como un KeyError o un fallo de conexión
        print(f"ERROR CRÍTICO: {e}")
        messages.error(request, f"Ocurrió un error al unirse: {e}")
        
    return redirect('detalle_actividad', pk=pk)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Actividad # Asegúrate de importar tu modelo Actividad

@login_required
def mis_actividades(request):
    usuario = request.user
    
    # 1. Actividades que el usuario CREÓ (Organizadas)
    # Filtramos la tabla Actividad donde el campo 'organizador' es el usuario actual
    actividades_organizadas = Actividad.objects.filter(organizador=usuario).order_by('fecha', 'hora_inicio')
    
    # 2. Actividades en las que el usuario PARTICIPA
    # Excluimos las que organiza, para que no se dupliquen en las listas
    actividades_participando = (
        usuario.actividades_participando.all()
        .exclude(organizador=usuario)
        .order_by('fecha', 'hora_inicio')
    )
    
    context = {
        # 🚨 PASAMOS AMBAS LISTAS AL TEMPLATE
        'organizadas': actividades_organizadas,
        'participando': actividades_participando, 
        'active_page': 'mis_actividades',
    }
    
    return render(request, 'actividades/mis_actividades.html', context)

from django.db import transaction # Ya sabes que esto soluciona el error de importación

@login_required
def salir_actividad(request, pk):
    # 1. Obtener la actividad
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user

    # Usamos transaction.atomic para asegurar que el cupo y la remoción ocurran juntos.
    try:
        with transaction.atomic():
            
            # 2. Verificar si el usuario es participante
            if actividad.participantes.filter(id=usuario.id).exists():
                
                # 3. Remover el participante
                actividad.participantes.remove(usuario)
                
                # 4. Aumentar el cupo
                actividad.cupos += 1
                actividad.save()
                
                messages.success(request, f"Has cancelado tu asistencia a {actividad.titulo}. ¡Cupo liberado!")
                
            else:
                messages.warning(request, "No estabas unido a esta actividad.")

    except Exception as e:
        messages.error(request, f"Ocurrió un error al intentar salir de la actividad: {e}")
        
    # Redirigir a la página donde estaba el usuario (detalle o mis_actividades)
    # Aquí redirigiremos al detalle, pero puedes ajustarlo.
    return redirect('detalle_actividad', pk=pk)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# 🚨 Asegúrate de importar tu modelo
from .models import Actividad 

# views.py (Dentro de la función crear_actividad)

@login_required
def crear_actividad(request):
    if request.method == "POST":
        # 1. Capturar todos los datos del formulario (omitiendo código por brevedad)
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

        # 2. Validar datos críticos y ubicación
        if not all([titulo, deporte, lugar_texto, lat_str, lng_str, fecha_str, hora_inicio_str, cupos_str]):
            messages.error(request, "Por favor, completa todos los campos obligatorios y selecciona una ubicación válida con el autocompletado.")
            return render(request, "actividades/crear_actividad.html") # Retorna en fallo de validación

        try:
            # Convertir campos a sus tipos correctos
            cupos = int(cupos_str)
            latitud = float(lat_str)
            longitud = float(lng_str)
            
            # 3. Crear el objeto Actividad y capturar la instancia
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
                print(f"ERROR: No se pudo notificar a usuarios cercanos: {e}")
                
            return redirect('actividades') # Retorna en éxito (Redirección)

        except ValueError:
            messages.error(request, "Error en el formato de los datos (cupos, latitud o longitud son inválidos).")
            return render(request, "actividades/crear_actividad.html") # 🚨 Retorna en fallo
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado al guardar la actividad: {e}")
            return render(request, "actividades/crear_actividad.html") # 🚨 Retorna en fallo
            
    # 🚨 RETORNO FINAL: Este maneja la solicitud GET (carga inicial del formulario)
    return render(request, "actividades/crear_actividad.html")

  






from django.db.models import Q
from .models import Notificacion, User, Actividad, Perfil
from math import radians, cos, sin, asin, sqrt 
from django.contrib import messages

def crear_notificacion_actividad_cercana(actividad):
    
    # 1. Obtener coordenadas de la nueva actividad
    try:
        act_lat = float(actividad.latitud)
        act_lng = float(actividad.longitud)
    except (TypeError, ValueError):
        print("DEBUG NOTIF: Actividad sin coordenadas válidas. Saliendo.")
        return 

    # 2. Filtrar perfiles por deporte y excluir al organizador
    perfiles_a_notificar = Perfil.objects.filter(
        disciplina_preferida__iexact=actividad.deporte
    ).exclude(usuario=actividad.organizador)
    
    print(f"DEBUG NOTIF: {perfiles_a_notificar.count()} perfiles encontrados con deporte '{actividad.deporte}'.")

    usuarios_cercanos = []
    
    # 3. Iterar y aplicar el filtro de distancia
    for perfil in perfiles_a_notificar:
        
        # 🚨 DEBUG: Imprimir los valores clave del perfil 🚨
        print(f"\n--- Evaluando Perfil: {perfil.usuario.username} ---")
        print(f"Radio configurado: {perfil.radio}")
        
        # Verificación estricta de que todos los campos de ubicación no sean None
        if perfil.latitud is not None and perfil.longitud is not None and perfil.radio is not None:
            try:
                user_lat = float(perfil.latitud)
                user_lng = float(perfil.longitud)
                radio = perfil.radio
                
                # Calcular la distancia
                distancia = calcular_distancia_haversine(user_lat, user_lng, act_lat, act_lng)
                
                print(f"Distancia calculada: {distancia:.2f} km")
                
                if distancia <= radio:
                    usuarios_cercanos.append({
                        'usuario': perfil.usuario,
                        'distancia': round(distancia, 1)
                    })
                    print(f"✅ ÉXITO: {perfil.usuario.username} está DENTRO del radio ({radio} km).")
                else:
                    print(f"❌ FALLO FILTRO: {perfil.usuario.username} está FUERA del radio.")
                    
            except Exception as e:
                print(f"❌ ERROR CRÍTICO DE CONVERSIÓN para {perfil.usuario.username}: {e}")
        else:
            print(f"❌ FALLO DATOS: Ubicación/Radio nulos o inválidos para {perfil.usuario.username}. Saltado.")

    # 4. Creación de las notificaciones
    if usuarios_cercanos:
        print(f"\n--- Creando {len(usuarios_cercanos)} notificaciones ---")
        # ... (código de creación de notificaciones) ...
        # (Asegúrate de usar la lógica de .capitalize() aquí)
        
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
                print(f"ERROR: No se pudo guardar Notificacion para {usuario.username}. Causa: {e}")





@login_required
def reseña_actividad(request):
    return render(request, "actividades/reseña_actividad.html")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Actividad, Perfil, User # Asegúrate de importar User si no lo has hecho
from django.db import transaction 
from math import radians, cos, sin, asin, sqrt 
# ... (otras funciones como calcular_distancia_haversine, crear_actividad, etc.) ...


@login_required
def perfil_participante(request, user_id):
    """Muestra la información pública de un participante."""
    # Usamos User y no Perfil para asegurar que exista
    usuario = get_object_or_404(User, pk=user_id)
    
    # Intentamos obtener el perfil asociado (puede no existir si el registro es viejo)
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        perfil = None 
        
    context = {
        'usuario': usuario,
        'perfil': perfil,
        # Puedes añadir más seguridad aquí si solo quieres que se vean perfiles si son participantes
    }
    return render(request, 'actividades/perfil_participante.html', context)


@login_required
def gestionar_participantes(request, pk):
    """Muestra la lista de participantes de una actividad para su gestión."""
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # 1. Seguridad: Solo el organizador puede gestionar la lista
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para administrar esta actividad.")
        return redirect('detalle_actividad', pk=pk)

    # 2. Obtener la lista de participantes con su perfil asociado
    # El campo participantes es ManyToMany, por lo que retorna objetos User
    participantes = []
    for usuario in actividad.participantes.all():
        participantes.append({
            'user': usuario,
            # Intenta obtener el perfil; si no existe, usa valores por defecto
            'perfil': getattr(usuario, 'perfil', None),
        })

    context = {
        'actividad': actividad,
        'participantes': participantes,
    }
    return render(request, 'actividades/gestionar_participantes.html', context)


@login_required
def quitar_participante(request, actividad_pk, user_id):
    """Quita a un participante de una actividad y libera un cupo."""
    actividad = get_object_or_404(Actividad, pk=actividad_pk)
    usuario_a_quitar = get_object_or_404(User, pk=user_id)
    
    # 1. Seguridad: Solo el organizador puede quitar participantes
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('gestionar_participantes', pk=actividad_pk)

    # 2. Lógica de remoción
    try:
        with transaction.atomic():
            # Remover de la relación ManyToMany
            actividad.participantes.remove(usuario_a_quitar)
            
            # Devolver el cupo (Solo si la actividad no estaba ya llena, aunque remove() es seguro)
            actividad.cupos += 1
            actividad.save()
            
            messages.success(request, f"Se ha quitado a {usuario_a_quitar.username} de la actividad y se liberó un cupo.")
    
    except Exception as e:
        messages.error(request, f"Error al quitar participante: {e}")

    return redirect('gestionar_participantes', pk=actividad_pk)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Actividad 

@login_required
def editar_actividad(request, pk): # 🚨 CLAVE: Debe aceptar 'pk' aquí
    # 1. Obtener la actividad o devolver 404
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # 2. Seguridad: Solo el organizador puede editar
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para editar esta actividad.")
        raise PermissionDenied("Acceso denegado: No eres el organizador.")

    # ----------------------------------------------------
    # Lógica de POST (Guardar Cambios)
    # ----------------------------------------------------
    if request.method == "POST":
        # 3. Capturar y validar datos (usando los nombres del template)
        titulo = request.POST.get("titulo", "").strip() 
        deporte = request.POST.get("deporte", "").strip()
        lugar_texto = request.POST.get("lugar", "").strip()
        
        # Geocodificación (valores de los campos ocultos)
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
            # Si hay error, redirigimos para que no se pierdan los mensajes
            return redirect('editar_actividad', pk=pk) 

        try:
            # 4. Actualizar el objeto con los nuevos valores
            actividad.titulo = titulo
            actividad.deporte = deporte
            actividad.lugar = lugar_texto
            actividad.fecha = fecha_str
            actividad.hora_inicio = hora_inicio_str
            actividad.hora_fin = hora_fin_str if hora_fin_str else None
            actividad.nivel = nivel
            actividad.cupos = int(cupos_str)
            actividad.descripcion = descripcion
            
            # 5. Actualizar Coordenadas si fueron modificadas
            if lat_str and lng_str:
                actividad.latitud = float(lat_str)
                actividad.longitud = float(lng_str)
            
            actividad.save()
            messages.success(request, f"Actividad '{actividad.titulo}' actualizada con éxito.")
            return redirect('mis_actividades') # Volvemos a la lista de actividades propias

        except ValueError:
            messages.error(request, "Error en el formato de datos numéricos o fecha/hora.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
            
    # ----------------------------------------------------
    # Lógica de GET (Mostrar Formulario con datos precargados)
    # ----------------------------------------------------
    context = {
        'actividad': actividad, # Pasamos la actividad al template
        'deportes': ['futbol', 'basketball', 'skate', 'volibol', 'running', 'tenis'], # Lista para el select
    }
    return render(request, 'actividades/editar_actividad.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Actividad 

@login_required
def eliminar_actividad(request, pk):
    # Obtener la actividad o devolver 404
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # 1. Verificar si el usuario es el organizador (Seguridad)
    if actividad.organizador != request.user:
        messages.error(request, "No tienes permiso para eliminar esta actividad.")
        # Redirigir al detalle o lanzar PermissionDenied
        return redirect('detalle_actividad', pk=pk)

    # 2. Manejar la eliminación (POST, aunque por simplicidad, lo haremos directo)
    # En una aplicación real, se usaría un formulario POST.
    try:
        actividad.delete()
        messages.success(request, f"La actividad '{actividad.titulo}' ha sido eliminada permanentemente.")
        # 3. Redirigir a la lista principal de actividades
        return redirect('actividades')

    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar la actividad: {e}")
        return redirect('detalle_actividad', pk=pk)


#Administrador

from django.shortcuts import render
from django.utils import timezone

# Vista: Mostrar logs del sistema
from django.shortcuts import render
from .models import Log

def ver_logs(request):
    logs = Log.objects.all().order_by('-fecha')
    return render(request, 'administracion/ver_logs.html', {'logs': logs})


def gestionar_usuarios(request):
    usuarios = [
        {"id": 1, "nombre": "Carlos Gómez", "usuario": "carlosg", "estado": "Activo"},
        {"id": 2, "nombre": "María Torres", "usuario": "mariat", "estado": "Suspendido"},
        {"id": 3, "nombre": "Ana López", "usuario": "analopez", "estado": "Activo"},
    ]
    return render(request, "administracion/gestionar_usuarios.html", {"usuarios": usuarios})





