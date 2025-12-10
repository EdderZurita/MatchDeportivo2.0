from django.shortcuts import render

def sobre_nosotros(request):
    """Vista para la página Sobre Nosotros con misión, visión y valores."""
    return render(request, 'sobre_nosotros.html')
