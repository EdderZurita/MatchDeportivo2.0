"""
Módulo de vistas de MatchDeportivoAPP.

Este paquete organiza las vistas por funcionalidad:
- auth: Autenticación (login, registro, recuperación de contraseña)
- actividades: CRUD de actividades deportivas
- perfiles: Gestión de perfiles de usuario
- notificaciones: Sistema de notificaciones
- admin: Vistas de administración
"""

# Importar vistas de autenticación
from .auth import (
    inicioSesion,
    registroSesion,
    olvidoContraseña,
    cerrarSesion,
)

# Importar vistas de perfiles
from .perfiles import (
    perfil,
    perfil_jugador,
    perfil_participante,
)

# Importar vistas de actividades
from .actividades import (
    actividades,
    detalle_actividad,
    crear_actividad,
    editar_actividad,
    eliminar_actividad,
    mis_actividades,
    unirse_actividad,
    salir_actividad,
    gestionar_participantes,
    quitar_participante,
    reseña_actividad,
)

# Importar vistas de notificaciones
from .notificaciones import (
    notificaciones,
    lista_notificaciones,
)

# Importar vistas de administración
from .admin import (
    ver_logs,
    gestionar_usuarios,
)

# Importar vista de inicio
from .general import inicio

__all__ = [
    # Autenticación
    'inicioSesion',
    'registroSesion',
    'olvidoContraseña',
    'cerrarSesion',
    # Perfiles
    'perfil',
    'perfil_jugador',
    'perfil_participante',
    # Actividades
    'actividades',
    'detalle_actividad',
    'crear_actividad',
    'editar_actividad',
    'eliminar_actividad',
    'mis_actividades',
    'unirse_actividad',
    'salir_actividad',
    'gestionar_participantes',
    'quitar_participante',
    'reseña_actividad',
    # Notificaciones
    'notificaciones',
    'lista_notificaciones',
    # Administración
    'ver_logs',
    'gestionar_usuarios',
    # General
    'inicio',
]
