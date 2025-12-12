/**
 * PERFIL.JS
 * Funcionalidades para la página de perfil de usuario
 * Incluye selector de iconos de perfil
 * 
 * @author Equipo MatchDeportivo
 * @version 1.0.0
 * @since 2025-12-12
 */

/* ================================================================================
   SELECTOR DE ICONOS DE PERFIL
   Permite al usuario elegir un icono para su perfil
   ================================================================================ */

/**
 * Inicializa el selector de iconos de perfil
 * Permite al usuario seleccionar un icono haciendo click en las opciones
 */
document.addEventListener('DOMContentLoaded', () => {
    // Verificar que existe el input hidden
    const iconoInput = document.getElementById('icono_perfil');
    
    if (!iconoInput) {
        console.warn('Input #icono_perfil no encontrado en la página');
        return;
    }
    
    // Agregar event listeners a todos los iconos disponibles
    const iconImages = document.querySelectorAll('.icon-img');
    
    if (iconImages.length === 0) {
        console.warn('No se encontraron iconos con clase .icon-img');
        return;
    }
    
    console.log(`Selector de iconos inicializado con ${iconImages.length} iconos`);
    
    iconImages.forEach(img => {
        img.addEventListener('click', function() {
            // Remover selección de todos los iconos
            document.querySelectorAll('.icon-option').forEach(opt =>
                opt.classList.remove('selected')
            );
            
            // Marcar el icono clickeado como seleccionado
            this.parentElement.classList.add('selected');
            
            // Obtener el valor del icono desde data-icon
            const iconValue = this.dataset.icon;
            
            if (iconValue) {
                // Guardar el valor del icono seleccionado en el input hidden
                iconoInput.value = iconValue;
                console.log(`Icono seleccionado: ${iconValue}`);
            } else {
                console.error('El icono no tiene atributo data-icon');
            }
        });
    });
});

/* ================================================================================
   GOOGLE MAPS AUTOCOMPLETE - DESHABILITADO
   Código comentado hasta implementación oficial de Google Maps
   ================================================================================ */

/*
⚠️ NOTA: Esta funcionalidad está temporalmente deshabilitada
Google Maps no está siendo utilizado actualmente en el proyecto
para evitar costos de API y simplificar el desarrollo.

TODO: Reactivar cuando se implemente Google Maps oficialmente

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
*/
