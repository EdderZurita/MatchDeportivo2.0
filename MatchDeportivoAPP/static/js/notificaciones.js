// ========================================
// NOTIFICACIONES.JS - Sistema de notificaciones
// ========================================

// Marcar notificación como leída
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
                const notifElement = document.getElementById(`notif-${notificacionId}`);
                if (notifElement) {
                    notifElement.classList.remove('no-leida');
                    notifElement.classList.add('leida');
                }
                actualizarContadorNotificaciones();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Marcar todas como leídas
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
                document.querySelectorAll('.notificacion-item.no-leida').forEach(item => {
                    item.classList.remove('no-leida');
                    item.classList.add('leida');
                });
                actualizarContadorNotificaciones();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Actualizar contador de notificaciones
function actualizarContadorNotificaciones() {
    const contador = document.getElementById('contador-notificaciones');
    if (!contador) return;

    fetch('/notificaciones/contador/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                contador.textContent = data.count;
                contador.style.display = 'inline-block';
            } else {
                contador.style.display = 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}

// Mostrar notificación toast
function mostrarNotificacionToast(mensaje, tipo = 'info') {
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

    document.body.appendChild(toast);

    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Obtener icono según tipo
function getIconoTipo(tipo) {
    const iconos = {
        'success': 'check-circle-fill',
        'error': 'x-circle-fill',
        'warning': 'exclamation-triangle-fill',
        'info': 'info-circle-fill'
    };
    return iconos[tipo] || 'info-circle-fill';
}

// Obtener cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    actualizarContadorNotificaciones();

    // Actualizar cada 30 segundos
    setInterval(actualizarContadorNotificaciones, 30000);
});
