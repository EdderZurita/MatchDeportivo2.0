/**
 * ACTIVIDADES.JS
 * Funcionalidades específicas para la gestión de actividades deportivas
 * 
 * @author Equipo MatchDeportivo
 * @version 1.0.0
 * @since 2025-12-12
 */

/* ----------------
   GESTIÓN DE PARTICIPANTES
   Funciones para agregar/quitar participantes de actividades
   ---------------- */

/**
 * Inicializa los event listeners para gestión de participantes
 * Se ejecuta automáticamente al cargar la página
 */
function initGestionParticipantes() {
    // Confirmar quitar participante
    const botonesQuitar = document.querySelectorAll('.btn-quitar-participante');
    
    botonesQuitar.forEach(btn => {
        btn.addEventListener('click', confirmarQuitarParticipante);
    });
}

/**
 * Confirma la acción de quitar un participante de la actividad
 * Muestra un diálogo de confirmación antes de proceder
 * 
 * @param {Event} e - Evento del click en el botón
 * @returns {boolean} - False si el usuario cancela, true si confirma
 */
function confirmarQuitarParticipante(e) {
    const username = this.dataset.username;
    const mensaje = `¿Estás seguro de que deseas quitar a ${username} de la actividad? Esto liberará su cupo.`;
    
    if (!confirm(mensaje)) {
        e.preventDefault();
        return false;
    }
    
    return true;
}

/* ----------------
   FILTROS DE ACTIVIDADES
   Funciones para filtrar y buscar actividades
   ---------------- */

/**
 * Inicializa los filtros de actividades
 * Configura event listeners para cambios en los filtros
 */
function initFiltros() {
    const filtroDeporte = document.querySelector('[name="deporte"]');
    
    if (filtroDeporte) {
        filtroDeporte.addEventListener('change', aplicarFiltros);
    }
}

/**
 * Aplica los filtros seleccionados
 * Envía el formulario automáticamente al cambiar el filtro
 */
function aplicarFiltros() {
    this.form.submit();
}

/* ----------------
   INICIALIZACIÓN
   Configuración inicial al cargar la página
   ---------------- */

/**
 * Inicializa todas las funcionalidades de actividades
 * Se ejecuta cuando el DOM está completamente cargado
 */
document.addEventListener('DOMContentLoaded', function() {
    initGestionParticipantes();
    initFiltros();
});
