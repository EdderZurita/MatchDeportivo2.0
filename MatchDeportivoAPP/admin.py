"""Configuración del panel de administración de Django."""
from django.contrib import admin
from .models import Log, Perfil, Actividad, Notificacion


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    """Administración de logs del sistema."""
    list_display = ('usuario', 'accion', 'descripcion', 'fecha')
    list_filter = ('accion', 'fecha')
    search_fields = ('usuario__username', 'descripcion')
    ordering = ('-fecha',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Administración de perfiles de usuario."""
    list_display = ('usuario', 'nombre_completo', 'disciplina_preferida', 'nivel')
    list_filter = ('disciplina_preferida', 'nivel')
    search_fields = ('usuario__username', 'nombre_completo', 'nickname')


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    """Administración de actividades deportivas."""
    list_display = ('titulo', 'deporte', 'organizador', 'fecha', 'cupos', 'nivel')
    list_filter = ('deporte', 'nivel', 'fecha')
    search_fields = ('titulo', 'organizador__username', 'lugar')
    ordering = ('-fecha', '-hora_inicio')


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Administración de notificaciones."""
    list_display = ('usuario', 'tipo', 'mensaje', 'leida', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('usuario__username', 'mensaje')
    ordering = ('-fecha_creacion',)
