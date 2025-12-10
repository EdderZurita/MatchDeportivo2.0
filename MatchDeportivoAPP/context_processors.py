"""Context processors para variables globales en templates."""
from django.conf import settings

def google_maps_key(request):
    """Provee la API key de Google Maps a todos los templates."""
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
