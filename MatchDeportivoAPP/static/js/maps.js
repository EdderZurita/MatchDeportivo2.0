// ========================================
// MAPS.JS - Funcionalidades de mapas y geolocalización
// ========================================

// Inicializar autocompletado de Google Places
function initAutocomplete(inputId, latInputId, lngInputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const autocomplete = new google.maps.places.Autocomplete(input, {
        types: ['geocode'],
        componentRestrictions: { country: 'cl' }
    });

    autocomplete.addListener('place_changed', function () {
        const place = autocomplete.getPlace();

        if (!place.geometry) {
            console.error('No se encontró la ubicación');
            return;
        }

        // Guardar coordenadas en campos ocultos
        document.getElementById(latInputId).value = place.geometry.location.lat();
        document.getElementById(lngInputId).value = place.geometry.location.lng();
    });
}

// Obtener ubicación actual del usuario
function obtenerUbicacionActual(latInputId, lngInputId, addressInputId) {
    if (!navigator.geolocation) {
        alert('Tu navegador no soporta geolocalización');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            // Guardar coordenadas
            document.getElementById(latInputId).value = lat;
            document.getElementById(lngInputId).value = lng;

            // Geocodificación inversa para obtener dirección
            const geocoder = new google.maps.Geocoder();
            const latlng = { lat: lat, lng: lng };

            geocoder.geocode({ location: latlng }, function (results, status) {
                if (status === 'OK' && results[0]) {
                    document.getElementById(addressInputId).value = results[0].formatted_address;
                }
            });
        },
        function (error) {
            console.error('Error al obtener ubicación:', error);
            alert('No se pudo obtener tu ubicación');
        }
    );
}

// Mostrar mapa con marcador
function mostrarMapa(mapId, lat, lng, titulo) {
    const mapElement = document.getElementById(mapId);
    if (!mapElement) return;

    const position = { lat: parseFloat(lat), lng: parseFloat(lng) };

    const map = new google.maps.Map(mapElement, {
        center: position,
        zoom: 15,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });

    new google.maps.Marker({
        position: position,
        map: map,
        title: titulo || 'Ubicación'
    });
}

// Calcular distancia entre dos puntos (Haversine)
function calcularDistancia(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radio de la Tierra en km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distancia = R * c;

    return distancia.toFixed(1);
}
