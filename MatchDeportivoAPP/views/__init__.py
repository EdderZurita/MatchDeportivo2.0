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
    # olvidoContraseña,  # DESHABILITADO - Inseguro sin tokens
    cerrarSesion,
)

from .perfiles import (
    perfil,
    perfil_jugador,
    perfil_participante,
    eliminar_cuenta,
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
    valorar_usuario,
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
    # 'olvidoContraseña',  # DESHABILITADO - Inseguro sin tokens
    'cerrarSesion',
    'perfil',
    'perfil_jugador',
    'perfil_participante',
    'eliminar_cuenta',
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
    'valorar_usuario',
    'notificaciones',
    'lista_notificaciones',
    # Administración
    'ver_logs',
    'gestionar_usuarios',
    'inicio',
]
