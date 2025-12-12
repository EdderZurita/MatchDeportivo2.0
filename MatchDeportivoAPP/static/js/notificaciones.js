/**
 * NOTIFICACIONES.JS
 * Sistema de notificaciones en tiempo real para MatchDeportivo
 * Gestiona la visualización, marcado y actualización de notificaciones
 * 
 * @author Equipo MatchDeportivo
 * @version 1.0.0
 * @since 2025-12-12
 */

/* ================================================================================
   GESTIÓN DE NOTIFICACIONES
   Funciones para marcar notificaciones como leídas
   ================================================================================ */

/**
 * Marca una notificación específica como leída
 * Actualiza el estado en el servidor y la UI
 * 
 * @param {number} notificacionId - ID de la notificación a marcar
 */
function marcarComoLeida(notificacionId) {
    fetch(`/notificaciones/${notificacionId}/marcar-leida/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar UI: cambiar clases de la notificación
                const notifElement = document.getElementById(`notif-${notificacionId}`);
                if (notifElement) {
                    notifElement.classList.remove('no-leida');
                    notifElement.classList.add('leida');
                }
                // Actualizar contador de notificaciones no leídas
                actualizarContadorNotificaciones();
            }
        })
        .catch(error => console.error('Error:', error));
}

/**
 * Marca todas las notificaciones del usuario como leídas
 * Útil para limpiar todas las notificaciones de una vez
 */
function marcarTodasLeidas() {
    fetch('/notificaciones/marcar-todas-leidas/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar UI: marcar todas como leídas
                document.querySelectorAll('.notificacion-item.no-leida').forEach(item => {
                    item.classList.remove('no-leida');
                    item.classList.add('leida');
                });
                // Actualizar contador
                actualizarContadorNotificaciones();
            }
        })
        .catch(error => console.error('Error:', error));
}

/* ================================================================================
   ACTUALIZACIÓN DE CONTADOR
   Funciones para mantener actualizado el contador de notificaciones
   ================================================================================ */

/**
 * Actualiza el contador de notificaciones no leídas
 * Consulta al servidor y actualiza el badge en el navbar
 */
function actualizarContadorNotificaciones() {
    const contador = document.getElementById('contador-notificaciones');
    if (!contador) return;

    // Consultar cantidad de notificaciones no leídas
    fetch('/notificaciones/contador/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                // Mostrar contador con la cantidad
                contador.textContent = data.count;
                contador.style.display = 'inline-block';
            } else {
                // Ocultar contador si no hay notificaciones
                contador.style.display = 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}

/* ================================================================================
   NOTIFICACIONES TOAST
   Sistema de notificaciones emergentes tipo toast
   ================================================================================ */

/**
 * Muestra una notificación toast temporal
 * Se auto-cierra después de 5 segundos
 * 
 * @param {string} mensaje - Mensaje a mostrar en el toast
 * @param {string} [tipo='info'] - Tipo de notificación: 'success', 'error', 'warning', 'info'
 */
function mostrarNotificacionToast(mensaje, tipo = 'info') {
    // Crear elemento toast
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${tipo}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi bi-${getIconoTipo(tipo)}"></i>
            <span>${mensaje}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="bi bi-x"></i>
        </button>
    `;

    // Agregar al DOM
    document.body.appendChild(toast);

    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Obtiene el icono de Bootstrap Icons según el tipo de notificación
 * 
 * @param {string} tipo - Tipo de notificación
 * @returns {string} - Nombre del icono de Bootstrap Icons
 */
function getIconoTipo(tipo) {
    const iconos = {
        'success': 'check-circle-fill',
        'error': 'x-circle-fill',
        'warning': 'exclamation-triangle-fill',
        'info': 'info-circle-fill'
    };
    return iconos[tipo] || 'info-circle-fill';
}

/* ================================================================================
   UTILIDADES
   Funciones auxiliares para el sistema de notificaciones
   ================================================================================ */

/**
 * Obtiene el valor de una cookie por su nombre
 * Necesario para obtener el token CSRF de Django
 * 
 * @param {string} name - Nombre de la cookie
 * @returns {string|null} - Valor de la cookie o null si no existe
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Verificar si esta cookie es la que buscamos
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* ================================================================================
   INICIALIZACIÓN
   Configuración inicial del sistema de notificaciones
   ================================================================================ */

/**
 * Inicializa el sistema de notificaciones
 * Se ejecuta automáticamente cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function () {
    // Actualizar contador al cargar la página
    actualizarContadorNotificaciones();

    // Actualizar contador cada 30 segundos para mantenerlo sincronizado
    setInterval(actualizarContadorNotificaciones, 30000);
});
