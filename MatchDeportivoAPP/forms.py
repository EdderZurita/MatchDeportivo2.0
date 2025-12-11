"""Formularios de Django para MatchDeportivo."""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import Perfil, Actividad, Valoracion
from .constants import DEPORTES, NIVELES


class RegistroForm(forms.ModelForm):
    """Formulario de registro de nuevos usuarios."""
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]


class ActividadForm(forms.ModelForm):
    """Formulario para crear y editar actividades deportivas."""
    
    class Meta:
        model = Actividad
        fields = ['titulo', 'deporte', 'descripcion', 'lugar', 'fecha', 
                  'hora_inicio', 'hora_fin', 'nivel', 'cupos']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Partido de fútbol 5'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe la actividad...'
            }),
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estadio Nacional'
            }),
            'cupos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'deporte': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        """Validación personalizada del formulario."""
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        # Validar que la fecha no sea en el pasado
        if fecha and fecha < date.today():
            raise ValidationError("La fecha no puede ser en el pasado.")
        
        # Validar que hora_fin sea después de hora_inicio
        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        
        return cleaned_data


class ValoracionForm(forms.ModelForm):
    """Formulario para valorar a un usuario."""
    
    class Meta:
        model = Valoracion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.RadioSelect(choices=[
                (1, '⭐'),
                (2, '⭐⭐'),
                (3, '⭐⭐⭐'),
                (4, '⭐⭐⭐⭐'),
                (5, '⭐⭐⭐⭐⭐')
            ]),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comparte tu experiencia (opcional)',
                'maxlength': 500
            })
        }
    
    def clean_comentario(self):
        """Validar longitud del comentario."""
        comentario = self.cleaned_data.get('comentario', '')
        if len(comentario) > 500:
            raise ValidationError("El comentario no puede exceder 500 caracteres.")
        return comentario


class PerfilForm(forms.ModelForm):
    """Formulario mejorado para edición de perfil."""
    
    class Meta:
        model = Perfil
        fields = ['nombre_completo', 'nickname', 'icono_perfil', 'disciplina_preferida',
                  'ubicacion', 'latitud', 'longitud', 'nivel', 'horarios', 'radio']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'horarios': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'radio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
            'icono_perfil': forms.HiddenInput(),
            'disciplina_preferida': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_radio(self):
        """Validar rango del radio de búsqueda."""
        radio = self.cleaned_data.get('radio')
        if radio and (radio < 1 or radio > 50):
            raise ValidationError("El radio debe estar entre 1 y 50 km.")
        return radio

