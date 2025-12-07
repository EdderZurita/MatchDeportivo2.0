from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["nombre_completo"]
