"""
URL configuration for MatchDeportivo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from MatchDeportivoAPP import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='home'),
    path('inicioSesion/', views.inicioSesion, name='inicioSesion'),
    path('olvidoContraseña/', views.olvidoContraseña, name='olvidoContraseña'),
    path('registroSesion/', views.registroSesion, name='registroSesion'),
    path('cerrarSesion/', views.cerrarSesion, name="cerrarSesion"),

    #usuarios
    path('perfil/', views.perfil, name='perfil'),
    path('perfil_jugador/', views.perfil_jugador, name='perfil_jugador'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),

    #Actividades
    path('actividades/', views.actividades, name='actividades'),
    path('detalle_actividad/<int:pk>/', views.detalle_actividad, name='detalle_actividad'),
    path('unirse/<int:pk>/', views.unirse_actividad, name='unirse_actividad'),
    path('salir/<int:pk>/', views.salir_actividad, name='salir_actividad'),
    path('cancelar_actividad/<int:pk>/', views.eliminar_actividad, name='cancelar_actividad'),
    path('mis_actividades/', views.mis_actividades, name='mis_actividades'),
    path('crear_actividad/', views.crear_actividad, name='crear_actividad'),
    path('reseña_actividad/', views.reseña_actividad, name='reseña_actividad'),
    path('gestionar_participantes/', views.gestionar_participantes, name='gestionar_participantes'),
    path('editar_actividad/<int:pk>/', views.editar_actividad, name='editar_actividad'),

    path('participante/<int:user_id>/', views.perfil_participante, name='perfil_participante'), 
    path('gestionar/<int:pk>/', views.gestionar_participantes, name='gestionar_participantes'),
    path('quitar/<int:actividad_pk>/<int:user_id>/', views.quitar_participante, name='quitar_participante'),


    #Administracion
    path('administracion/logs/', views.ver_logs, name='ver_logs'),
    path('administracion/usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),


]
