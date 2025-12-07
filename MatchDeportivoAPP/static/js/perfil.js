// Funciones para la página de perfil

// Selector de iconos de perfil
document.addEventListener('DOMContentLoaded', () => {
    // Selector de iconos
    document.querySelectorAll('.icon-img').forEach(img => {
        img.addEventListener('click', () => {
            document.querySelectorAll('.icon-option').forEach(opt =>
                opt.classList.remove('selected')
            );
            img.parentElement.classList.add('selected');
            document.getElementById('icono_perfil').value = img.dataset.icon;
        });
    });
});

// Google Maps Autocomplete - se llama automáticamente por callback
function initAutocomplete() {
    const input = document.getElementById("autocomplete");

    if (!input) {
        console.warn('Input de autocomplete no encontrado');
        return;
    }

    const autocomplete = new google.maps.places.Autocomplete(input, {
        types: ["geocode"],
        componentRestrictions: { country: "cl" }
    });

    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();

        if (!place.geometry) {
            alert("No se encontró la ubicación.");
            return;
        }

        document.getElementById("latitud").value = place.geometry.location.lat();
        document.getElementById("longitud").value = place.geometry.location.lng();
    });
}
