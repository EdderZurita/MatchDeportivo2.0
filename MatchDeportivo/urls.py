"""URL configuration for MatchDeportivo project."""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from MatchDeportivoAPP import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='home'),
    
    # Autenticación
    path('inicioSesion/', views.inicioSesion, name='inicioSesion'),
    path('olvidoContraseña/', views.olvidoContraseña, name='olvidoContraseña'),
    path('registroSesion/', views.registroSesion, name='registroSesion'),
    path('cerrarSesion/', views.cerrarSesion, name="cerrarSesion"),

    # Usuarios
    path('perfil/', views.perfil, name='perfil'),
    path('perfil_jugador/', views.perfil_jugador, name='perfil_jugador'),
    path('participante/<int:user_id>/', views.perfil_participante, name='perfil_participante'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),

    # Actividades
    path('actividades/', views.actividades, name='actividades'),
    path('detalle_actividad/<int:pk>/', views.detalle_actividad, name='detalle_actividad'),
    path('crear_actividad/', views.crear_actividad, name='crear_actividad'),
    path('editar_actividad/<int:pk>/', views.editar_actividad, name='editar_actividad'),
    path('cancelar_actividad/<int:pk>/', views.eliminar_actividad, name='cancelar_actividad'),
    path('mis_actividades/', views.mis_actividades, name='mis_actividades'),
    path('reseña_actividad/', views.reseña_actividad, name='reseña_actividad'),
    
    # Participantes
    path('unirse/<int:pk>/', views.unirse_actividad, name='unirse_actividad'),
    path('salir/<int:pk>/', views.salir_actividad, name='salir_actividad'),
    path('gestionar/<int:pk>/', views.gestionar_participantes, name='gestionar_participantes'),
    path('quitar/<int:actividad_pk>/<int:user_id>/', views.quitar_participante, name='quitar_participante'),
    
    # Valoraciones
    path('valorar/<int:actividad_pk>/<int:usuario_pk>/', views.valorar_usuario, name='valorar_usuario'),

    # Administración
    path('administracion/logs/', views.ver_logs, name='ver_logs'),
    path('administracion/usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
