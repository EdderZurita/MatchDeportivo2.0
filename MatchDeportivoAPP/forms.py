"""Formularios de Django para MatchDeportivo."""
from django import forms
from django.contrib.auth.models import User
from .models import Perfil, Actividad


class RegistroForm(forms.ModelForm):
    """Formulario de registro de nuevos usuarios."""
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]


class PerfilForm(forms.ModelForm):
    """Formulario de edición de perfil de usuario."""
    class Meta:
        model = Perfil
        fields = ["nombre_completo"]


class ActividadForm(forms.ModelForm):
    """Formulario para crear/editar actividades deportivas."""
    class Meta:
        model = Actividad
        fields = [
            'titulo', 'deporte', 'descripcion',
            'lugar', 'latitud', 'longitud',
            'fecha', 'hora_inicio', 'hora_fin',
            'nivel', 'cupos'
        ]
        widgets = {
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
