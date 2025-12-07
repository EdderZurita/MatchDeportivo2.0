// Validaciones y mejoras de formularios

// Validar formulario de crear actividad
function validarFormularioActividad(event) {
    const form = event.target;
    let valido = true;
    const errores = [];

    // Validar título
    const titulo = form.querySelector('[name="titulo"]');
    if (titulo && titulo.value.trim().length < 5) {
        errores.push('El título debe tener al menos 5 caracteres');
        valido = false;
    }

    // Validar deporte
    const deporte = form.querySelector('[name="deporte"]');
    if (deporte && !deporte.value) {
        errores.push('Debes seleccionar un deporte');
        valido = false;
    }

    // Validar ubicación
    const latitud = form.querySelector('[name="latitud_actividad"]');
    const longitud = form.querySelector('[name="longitud_actividad"]');
    if (latitud && longitud && (!latitud.value || !longitud.value)) {
        errores.push('Debes seleccionar una ubicación válida del autocompletado');
        valido = false;
    }

    // Validar cupos
    const cupos = form.querySelector('[name="cupos"]');
    if (cupos) {
        const cuposValue = parseInt(cupos.value);
        if (isNaN(cuposValue) || cuposValue < 1 || cuposValue > 50) {
            errores.push('Los cupos deben estar entre 1 y 50');
            valido = false;
        }
    }

    // Validar fecha
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

    if (!valido) {
        event.preventDefault();
        mostrarErrores(errores);
    }

    return valido;
}

// Validar formulario de perfil
function validarFormularioPerfil(event) {
    const form = event.target;
    let valido = true;
    const errores = [];

    // Validar nombre completo
    const nombre = form.querySelector('[name="nombre"]');
    if (nombre && nombre.value.trim().length < 3) {
        errores.push('El nombre debe tener al menos 3 caracteres');
        valido = false;
    }

    // Validar radio de búsqueda
    const radio = form.querySelector('[name="radio"]');
    if (radio && radio.value) {
        const radioValue = parseInt(radio.value);
        if (isNaN(radioValue) || radioValue < 1 || radioValue > 100) {
            errores.push('El radio debe estar entre 1 y 100 km');
            valido = false;
        }
    }

    if (!valido) {
        event.preventDefault();
        mostrarErrores(errores);
    }

    return valido;
}

// Mostrar errores en el formulario
function mostrarErrores(errores) {
    const contenedor = document.getElementById('errores-formulario');
    if (!contenedor) {
        const div = document.createElement('div');
        div.id = 'errores-formulario';
        div.className = 'alert alert-danger';
        div.innerHTML = '<ul class="mb-0"></ul>';
        document.querySelector('form').prepend(div);
    }

    const lista = document.querySelector('#errores-formulario ul');
    lista.innerHTML = '';

    errores.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        lista.appendChild(li);
    });

    // Scroll al top del formulario
    document.querySelector('#errores-formulario').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Confirmar acción peligrosa
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Estás seguro de realizar esta acción?');
}

// Confirmar eliminación
function confirmarEliminacion(event, nombre) {
    if (!confirmarAccion(`¿Estás seguro de eliminar "${nombre}"? Esta acción no se puede deshacer.`)) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Confirmar salir de actividad
function confirmarSalida(event, nombreActividad) {
    if (!confirmarAccion(`¿Estás seguro de salir de "${nombreActividad}"?`)) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Preview de imagen
function previewImagen(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById(previewId).src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Contador de caracteres
function contarCaracteres(textareaId, contadorId, max) {
    const textarea = document.getElementById(textareaId);
    const contador = document.getElementById(contadorId);

    if (!textarea || !contador) return;

    textarea.addEventListener('input', function () {
        const actual = this.value.length;
        contador.textContent = `${actual}/${max}`;

        if (actual > max) {
            contador.classList.add('text-danger');
        } else {
            contador.classList.remove('text-danger');
        }
    });
}

// Inicializar tooltips de Bootstrap
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    initTooltips();

    // Agregar validación a formularios
    const formActividad = document.getElementById('form-crear-actividad');
    if (formActividad) {
        formActividad.addEventListener('submit', validarFormularioActividad);
    }

    const formPerfil = document.getElementById('form-perfil');
    if (formPerfil) {
        formPerfil.addEventListener('submit', validarFormularioPerfil);
    }
});

// Validación de código de verificación
function setupCodigoVerificacion() {
    const modal = document.getElementById("codigoModal");
    if (!modal) return;

    let codigo = null;

    // Generar código cuando se abre el modal
    modal.addEventListener("show.bs.modal", () => {
        codigo = Math.floor(1000 + Math.random() * 9000);
        document.getElementById("codigoGenerado").innerText = codigo;
        document.getElementById("codigoIngresado").value = "";
    });

    // Validar código
    const btnValidar = document.querySelector('[data-validar-codigo]');
    if (btnValidar) {
        btnValidar.addEventListener('click', () => {
            const ingresado = document.getElementById("codigoIngresado").value;
            const urlCambio = btnValidar.dataset.urlCambio;

            if (ingresado == codigo) {
                window.location.href = urlCambio;
            } else {
                alert("Código incorrecto, inténtalo nuevamente.");
            }
        });
    }
}
