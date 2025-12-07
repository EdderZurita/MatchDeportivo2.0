"""Vista de inicio."""
from django.shortcuts import render, redirect


def inicio(request):
    """Página de inicio del sitio.
    
    Si el usuario está autenticado, redirige a actividades.
    Si no, muestra la landing page.
    """
    if request.user.is_authenticated:
        return redirect('actividades')
    return render(request, 'index.html')
