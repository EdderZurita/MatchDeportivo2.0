/**
 * FORMS.JS
 * Validaciones y mejoras para formularios del proyecto MatchDeportivo
 * 
 * Este archivo contiene todas las funciones de validación de formularios,
 * confirmaciones de acciones, y utilidades para mejorar la experiencia del usuario.
 * 
 * @author Equipo MatchDeportivo
 * @version 1.0.0
 * @since 2025-12-12
 */

/* ================================================================================
   VALIDACIÓN DE FORMULARIOS DE ACTIVIDADES
   Funciones para validar formularios de crear y editar actividades deportivas
   ================================================================================ */

/**
 * Valida el formulario de crear/editar actividad
 * Verifica título, deporte, cupos y fecha antes de enviar
 * 
 * @param {Event} event - Evento de submit del formulario
 * @returns {boolean} - True si es válido, false si hay errores
 */
function validarFormularioActividad(event) {
    const form = event.target;
    let valido = true;
    const errores = [];

    // Validar título (mínimo 5 caracteres)
    const titulo = form.querySelector('[name="titulo"]');
    if (titulo && titulo.value.trim().length < 5) {
        errores.push('El título debe tener al menos 5 caracteres');
        valido = false;
    }

    // Validar que se haya seleccionado un deporte
    const deporte = form.querySelector('[name="deporte"]');
    if (deporte && !deporte.value) {
        errores.push('Debes seleccionar un deporte');
        valido = false;
    }

    /* ⚠️ NOTA: Validación de ubicación deshabilitada (Google Maps no está en uso)
    // Validar ubicación
    const latitud = form.querySelector('[name="latitud_actividad"]');
    const longitud = form.querySelector('[name="longitud_actividad"]');
    if (latitud && longitud && (!latitud.value || !longitud.value)) {
        errores.push('Debes seleccionar una ubicación válida del autocompletado');
        valido = false;
    }
    */

    // Validar cupos (entre 1 y 50)
    const cupos = form.querySelector('[name="cupos"]');
    if (cupos) {
        const cuposValue = parseInt(cupos.value);
        if (isNaN(cuposValue) || cuposValue < 1 || cuposValue > 50) {
            errores.push('Los cupos deben estar entre 1 y 50');
            valido = false;
        }
    }

    // Validar que la fecha no sea anterior a hoy
    const fecha = form.querySelector('[name="fecha"]');
    if (fecha && fecha.value) {
        const fechaSeleccionada = new Date(fecha.value);
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);

        if (fechaSeleccionada < hoy) {
            errores.push('La fecha no puede ser anterior a hoy');
            valido = false;
        }
    }

    // Si hay errores, prevenir envío y mostrarlos
    if (!valido) {
        event.preventDefault();
        mostrarErrores(errores);
    }

    return valido;
}

/* ================================================================================
   VALIDACIÓN DE FORMULARIOS DE PERFIL
   Funciones para validar formularios de perfil de usuario
   ================================================================================ */

/**
 * Valida el formulario de perfil de usuario
 * Verifica nombre completo y radio de búsqueda
 * 
 * @param {Event} event - Evento de submit del formulario
 * @returns {boolean} - True si es válido, false si hay errores
 */
function validarFormularioPerfil(event) {
    const form = event.target;
    let valido = true;
    const errores = [];

    // Validar nombre completo (mínimo 3 caracteres)
    const nombre = form.querySelector('[name="nombre"]');
    if (nombre && nombre.value.trim().length < 3) {
        errores.push('El nombre debe tener al menos 3 caracteres');
        valido = false;
    }

    // Validar radio de búsqueda (entre 1 y 100 km)
    const radio = form.querySelector('[name="radio"]');
    if (radio && radio.value) {
        const radioValue = parseInt(radio.value);
        if (isNaN(radioValue) || radioValue < 1 || radioValue > 100) {
            errores.push('El radio debe estar entre 1 y 100 km');
            valido = false;
        }
    }

    // Si hay errores, prevenir envío y mostrarlos
    if (!valido) {
        event.preventDefault();
        mostrarErrores(errores);
    }

    return valido;
}

/* ================================================================================
   UTILIDADES DE FORMULARIO
   Funciones auxiliares para mostrar errores y mejorar UX
   ================================================================================ */

/**
 * Muestra los errores de validación en el formulario
 * Crea un contenedor de alertas si no existe y muestra la lista de errores
 * 
 * @param {string[]} errores - Array de mensajes de error a mostrar
 */
function mostrarErrores(errores) {
    // Buscar o crear contenedor de errores
    const contenedor = document.getElementById('errores-formulario');
    if (!contenedor) {
        const div = document.createElement('div');
        div.id = 'errores-formulario';
        div.className = 'alert alert-danger';
        div.innerHTML = '<ul class="mb-0"></ul>';
        document.querySelector('form').prepend(div);
    }

    // Limpiar errores anteriores y agregar nuevos
    const lista = document.querySelector('#errores-formulario ul');
    lista.innerHTML = '';

    errores.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        lista.appendChild(li);
    });

    // Scroll suave al contenedor de errores
    document.querySelector('#errores-formulario').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

/* ================================================================================
   CONFIRMACIONES DE ACCIONES
   Funciones para confirmar acciones peligrosas o irreversibles
   ================================================================================ */

/**
 * Muestra un diálogo de confirmación para una acción
 * 
 * @param {string} [mensaje='¿Estás seguro de realizar esta acción?'] - Mensaje a mostrar
 * @returns {boolean} - True si el usuario confirma, false si cancela
 */
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Estás seguro de realizar esta acción?');
}

/**
 * Confirma la eliminación de un elemento
 * Muestra un mensaje personalizado con el nombre del elemento
 * 
 * @param {Event} event - Evento del click
 * @param {string} nombre - Nombre del elemento a eliminar
 * @returns {boolean} - True si confirma, false si cancela
 */
function confirmarEliminacion(event, nombre) {
    if (!confirmarAccion(`¿Estás seguro de eliminar "${nombre}"? Esta acción no se puede deshacer.`)) {
        event.preventDefault();
        return false;
    }
    return true;
}

/**
 * Confirma la salida de una actividad
 * 
 * @param {Event} event - Evento del click
 * @param {string} nombreActividad - Nombre de la actividad
 * @returns {boolean} - True si confirma, false si cancela
 */
function confirmarSalida(event, nombreActividad) {
    if (!confirmarAccion(`¿Estás seguro de salir de "${nombreActividad}"?`)) {
        event.preventDefault();
        return false;
    }
    return true;
}

/* ================================================================================
   UTILIDADES DE INTERFAZ
   Funciones para mejorar la experiencia del usuario
   ================================================================================ */

/**
 * Muestra una vista previa de una imagen seleccionada
 * Útil para formularios de carga de imágenes de perfil o actividades
 * 
 * @param {HTMLInputElement} input - Input de tipo file
 * @param {string} previewId - ID del elemento img donde mostrar la preview
 */
function previewImagen(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById(previewId).src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Agrega un contador de caracteres a un textarea
 * Muestra la cantidad actual y máxima de caracteres
 * 
 * @param {string} textareaId - ID del textarea
 * @param {string} contadorId - ID del elemento donde mostrar el contador
 * @param {number} max - Cantidad máxima de caracteres permitidos
 */
function contarCaracteres(textareaId, contadorId, max) {
    const textarea = document.getElementById(textareaId);
    const contador = document.getElementById(contadorId);

    if (!textarea || !contador) return;

    // Actualizar contador en cada input
    textarea.addEventListener('input', function () {
        const actual = this.value.length;
        contador.textContent = `${actual}/${max}`;

        // Cambiar a rojo si excede el máximo
        if (actual > max) {
            contador.classList.add('text-danger');
        } else {
            contador.classList.remove('text-danger');
        }
    });
}

/**
 * Inicializa los tooltips de Bootstrap en la página
 * Debe llamarse después de que el DOM esté cargado
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/* ================================================================================
   CÓDIGO DE VERIFICACIÓN
   Funciones para validación de código en recuperación de contraseña
   ================================================================================ */

/**
 * Configura el sistema de código de verificación para recuperación de contraseña
 * Genera un código de 4 dígitos y valida el ingreso del usuario
 * 
 * ⚠️ NOTA: Esta funcionalidad está temporalmente deshabilitada por seguridad
 * Se recomienda implementar un sistema de tokens por email en su lugar
 */
function setupCodigoVerificacion() {
    const modal = document.getElementById("codigoModal");
    if (!modal) return;

    let codigo = null;

    // Generar código aleatorio de 4 dígitos cuando se abre el modal
    modal.addEventListener("show.bs.modal", () => {
        codigo = Math.floor(1000 + Math.random() * 9000);
        document.getElementById("codigoGenerado").innerText = codigo;
        document.getElementById("codigoIngresado").value = "";
    });

    // Validar el código ingresado
    const btnValidar = document.querySelector('[data-validar-codigo]');
    if (btnValidar) {
        btnValidar.addEventListener('click', () => {
            const ingresado = document.getElementById("codigoIngresado").value;
            const urlCambio = btnValidar.dataset.urlCambio;

            if (ingresado == codigo) {
                // Código correcto, redirigir
                window.location.href = urlCambio;
            } else {
                // Código incorrecto
                alert("Código incorrecto, inténtalo nuevamente.");
            }
        });
    }
}

/* ================================================================================
   INICIALIZACIÓN
   Configuración inicial cuando el DOM está completamente cargado
   ================================================================================ */

/**
 * Inicializa todas las funcionalidades del formulario
 * Se ejecuta automáticamente cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function () {
    // Inicializar tooltips de Bootstrap
    initTooltips();

    // Agregar validación al formulario de crear actividad
    const formActividad = document.getElementById('form-crear-actividad');
    if (formActividad) {
        formActividad.addEventListener('submit', validarFormularioActividad);
    }

    // Agregar validación al formulario de perfil
    const formPerfil = document.getElementById('form-perfil');
    if (formPerfil) {
        formPerfil.addEventListener('submit', validarFormularioPerfil);
    }
    
    // Inicializar código de verificación si la función existe
    if (typeof setupCodigoVerificacion === 'function') {
        setupCodigoVerificacion();
    }
});
