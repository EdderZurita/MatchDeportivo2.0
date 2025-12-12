/**
 * Utilidades Generales de MatchDeportivo
 * 
 * Este archivo contiene funciones JavaScript reutilizables para toda la aplicación.
 * Incluye manejo de mensajes, validaciones, y otras utilidades comunes.
 * 
 * @author MatchDeportivo Team
 * @version 1.0
 */

// ============================================
// AUTO-DISMISS DE MENSAJES
// ============================================

/**
 * Inicializa el auto-dismiss de alertas de Bootstrap con efecto fade-out suave.
 * 
 * Los mensajes de éxito se cierran automáticamente después de 5 segundos.
 * Los mensajes de error/warning permanecen hasta que el usuario los cierre.
 * 
 * Configuración:
 * - success: 5 segundos con fade-out de 800ms
 * - info: 7 segundos con fade-out de 800ms
 * - warning: permanente (requiere cierre manual)
 * - danger/error: permanente (requiere cierre manual)
 */
function initAutoDissmissAlerts() {
    // Obtener todas las alertas
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Determinar el tiempo de auto-dismiss según el tipo
        let dismissTime = 0;
        
        if (alert.classList.contains('alert-success')) {
            dismissTime = 5000; // 5 segundos para éxito
        } else if (alert.classList.contains('alert-info')) {
            dismissTime = 7000; // 7 segundos para info
        }
        // warning y danger no se auto-cierran (dismissTime = 0)
        
        // Si tiene tiempo de auto-dismiss, programar cierre con animación
        if (dismissTime > 0) {
            setTimeout(() => {
                // Agregar transición CSS suave
                alert.style.transition = 'opacity 800ms ease-out, transform 800ms ease-out';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                
                // Esperar a que termine la animación antes de remover el elemento
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 800); // Duración de la animación
            }, dismissTime);
        }
    });
}

// ============================================
// INICIALIZACIÓN AL CARGAR LA PÁGINA
// ============================================

/**
 * Ejecuta funciones de inicialización cuando el DOM está listo.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar auto-dismiss de alertas
    initAutoDissmissAlerts();
    
    // Inicializar tooltips de Bootstrap (si existen)
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Inicializar popovers de Bootstrap (si existen)
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
});

// ============================================
// UTILIDADES ADICIONALES
// ============================================

/**
 * Muestra un mensaje temporal en la pantalla con efecto fade-out.
 * 
 * @param {string} message - El mensaje a mostrar
 * @param {string} type - Tipo de mensaje: 'success', 'danger', 'warning', 'info'
 * @param {number} duration - Duración en milisegundos (opcional, default: 5000)
 */
function showToast(message, type = 'info', duration = 5000) {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.setAttribute('role', 'alert');
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Agregar al body
    document.body.appendChild(alertDiv);
    
    // Auto-cerrar después de la duración especificada con fade-out
    setTimeout(() => {
        // Agregar transición CSS suave
        alertDiv.style.transition = 'opacity 800ms ease-out, transform 800ms ease-out';
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateY(-20px)';
        
        // Esperar a que termine la animación antes de remover
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 800);
    }, duration);
}

/**
 * Confirma una acción antes de ejecutarla.
 * 
 * @param {string} message - Mensaje de confirmación
 * @param {function} callback - Función a ejecutar si se confirma
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Valida un formulario antes de enviarlo.
 * 
 * @param {HTMLFormElement} form - El formulario a validar
 * @returns {boolean} - true si es válido, false si no
 */
function validateForm(form) {
    // Bootstrap 5 validation
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    return true;
}
