"""
Módulo de vistas de MatchDeportivoAPP.

Este paquete organiza las vistas por funcionalidad:
- auth: Autenticación (login, registro, recuperación de contraseña)
- actividades: CRUD de actividades deportivas
- perfiles: Gestión de perfiles de usuario
- notificaciones: Sistema de notificaciones
- admin: Vistas de administración
"""

from .auth import (
    inicioSesion,
    registroSesion,
    olvidoContraseña,
    cerrarSesion,
)

from .perfiles import (
    perfil,
    perfil_jugador,
    perfil_participante,
)

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

from .notificaciones import (
    notificaciones,
    lista_notificaciones,
)

from .admin import (
    ver_logs,
    gestionar_usuarios,
)

from .general import inicio

__all__ = [
    'inicioSesion',
    'registroSesion',
    'olvidoContraseña',
    'cerrarSesion',
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
    'notificaciones',
    'lista_notificaciones',
    # Administración
    'ver_logs',
    'gestionar_usuarios',
    'inicio',
]
