"""Modelos de datos de MatchDeportivoAPP."""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, time

from .constants import NIVELES

class Log(models.Model):
    """Registro de acciones del sistema para auditoría."""
    
    ACCION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('create_activity', 'Creación de actividad'),
        ('join_activity', 'Unirse a actividad'),
        ('error', 'Error del sistema'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    accion = models.CharField(max_length=50, choices=ACCION_CHOICES)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
class Perfil(models.Model):
    """Perfil extendido del usuario con preferencias deportivas y ubicación."""
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=150)
    nickname = models.CharField(max_length=50, blank=True)
    
    # Personalización
    icono_perfil = models.CharField(max_length=50, null=True, blank=True)
    disciplina_preferida = models.CharField(max_length=50, null=True, blank=True)
    
    # Ubicación
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Preferencias deportivas
    nivel = models.CharField(max_length=20, null=True, blank=True)
    horarios = models.CharField(max_length=200, null=True, blank=True)
    radio = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])  # Radio de búsqueda en km

    def __str__(self):
        return self.usuario.username
    
    def rating_promedio(self):
        """Calcula el rating promedio del usuario basado en sus valoraciones recibidas."""
        valoraciones = self.usuario.valoraciones_recibidas.all()
        if not valoraciones.exists():
            return None
        
        total = sum(v.puntuacion for v in valoraciones)
        return round(total / valoraciones.count(), 1)
    
    def total_valoraciones(self):
        """Retorna el número total de valoraciones recibidas."""
        return self.usuario.valoraciones_recibidas.count()

class Actividad(models.Model):
    """Actividad deportiva organizada por un usuario."""
    
    # Organizador
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actividades_creadas')
    
    # Info básica
    titulo = models.CharField(max_length=150)
    deporte = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    # Ubicación
    lugar = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Horario
    fecha = models.DateField(default=date.today)
    hora_inicio = models.TimeField(default=time(18, 0))
    hora_fin = models.TimeField(blank=True, null=True)
    
    # Nivel y cupos
    nivel = models.CharField(max_length=20, choices=NIVELES)
    cupos = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Participantes
    participantes = models.ManyToManyField(
        User,
        related_name='actividades_participando',
        blank=True
    )
    
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.deporte} el {self.fecha})"
    
class Notificacion(models.Model):
    """Notificaciones para los usuarios sobre actividades y eventos."""
    
    TIPO_NOTIFICACION = (
        ('NUEVA_ACTIVIDAD', 'Nueva Actividad Cercana'),
        ('CONFIRMACION_UNION', 'Confirmación de Unión'),
        ('NUEVA_CALIFICACION', 'Nueva Calificación'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACION)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.tipo} para {self.usuario.username}'

class Valoracion(models.Model):
    """Valoración de un usuario a otro después de participar en una actividad."""
    
    # Usuarios involucrados
    evaluador = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='valoraciones_dadas',
        help_text='Usuario que realiza la valoración'
    )
    evaluado = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='valoraciones_recibidas',
        help_text='Usuario que recibe la valoración'
    )
    
    # Actividad donde participaron juntos
    actividad = models.ForeignKey(
        'Actividad', 
        on_delete=models.CASCADE,
        related_name='valoraciones',
        help_text='Actividad en la que participaron'
    )
    
    # Valoración
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Puntuación de 1 a 5 estrellas'
    )
    comentario = models.TextField(
        blank=True,
        max_length=500,
        help_text='Comentario opcional sobre la experiencia'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        unique_together = ('evaluador', 'evaluado', 'actividad')
        verbose_name = 'Valoración'
        verbose_name_plural = 'Valoraciones'
    
    def __str__(self):
        return f'{self.evaluador.username} valoró a {self.evaluado.username} ({self.puntuacion}★)'