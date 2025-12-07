from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Log(models.Model):
    ACCION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('create_activity', 'Creación de actividad'),
        ('join_activity', 'Unirse a actividad'),
        ('error', 'Error del sistema'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=50, choices=ACCION_CHOICES)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=150)
    nickname = models.CharField(max_length=50, blank=True)

    # NUEVO: icono seleccionado
    icono_perfil = models.CharField(max_length=50, null=True, blank=True)

    # NUEVO: disciplina preferida (necesario para el filtro)
    disciplina_preferida = models.CharField(max_length=50, null=True, blank=True)
    
    # NUEVO: ubicación de texto
    ubicacion = models.CharField(max_length=255, null=True, blank=True)

    # 🚨 CAMPOS FALTANTES (Latitud y Longitud) 🚨
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # NUEVO: nivel / horarios / radio
    nivel = models.CharField(max_length=20, null=True, blank=True)
    horarios = models.CharField(max_length=200, null=True, blank=True)
    radio = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.usuario.username




from django.db import models
from django.contrib.auth.models import User
from datetime import date, time

class Actividad(models.Model):
    # Relación con el usuario que organiza la actividad
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actividades_creadas')
    
    # Información básica
    titulo = models.CharField(max_length=150)
    deporte = models.CharField(max_length=50) # 'futbol', 'tenis', etc.
    descripcion = models.TextField(blank=True)
    
    # Ubicación (Texto y Coordenadas para el cálculo de distancia)
    lugar = models.CharField(max_length=255) # Dirección de texto ingresada por el usuario
    latitud = models.DecimalField(max_digits=9, decimal_places=6) # Coordenada geográfica
    longitud = models.DecimalField(max_digits=9, decimal_places=6) # Coordenada geográfica
    
    # Tiempo y cupos
    fecha = models.DateField(default=date.today)
    hora_inicio = models.TimeField(default=time(18, 0))
    hora_fin = models.TimeField(blank=True, null=True)
    nivel = models.CharField(max_length=20, choices=[
        ('Principiante', 'Principiante'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
    ])
    cupos = models.IntegerField(default=1)

    participantes = models.ManyToManyField(
        User,
        related_name='actividades_participando',
        blank=True # Permite que una actividad se cree sin participantes
    )
    
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.deporte} el {self.fecha})"
    



from django.db import models
from django.contrib.auth.models import User
# Asegúrate de que tus modelos Perfil y Actividad estén importados

class Notificacion(models.Model):
    TIPO_NOTIFICACION = (
        ('NUEVA_ACTIVIDAD', 'Nueva Actividad Cercana'),
        ('CONFIRMACION_UNION', 'Confirmación de Unión'),
        ('NUEVA_CALIFICACION', 'Nueva Calificación'),
    )

    # Quién debe ver la notificación
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    
    # De dónde proviene la notificación (opcional, para enlazar al objeto)
    actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE, null=True, blank=True)
    
    # Tipo de notificación
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACION)
    
    # Contenido del mensaje
    mensaje = models.CharField(max_length=255)
    
    # Metadatos
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.tipo} para {self.usuario.username}'