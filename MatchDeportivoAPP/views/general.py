"""Vista de inicio."""
from django.shortcuts import render


def inicio(request):
    """Página de inicio del sitio."""
    return render(request, 'index.html')
