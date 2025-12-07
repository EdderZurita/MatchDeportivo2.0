"""
Vista general de inicio.
"""
from django.shortcuts import render


def inicio(request):
    """
    Vista de la página de inicio/landing page.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse con el template index.html
    """
    return render(request, "index.html")
