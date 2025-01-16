document.addEventListener("DOMContentLoaded", function () {
    const tipoUsuarioSelect = document.getElementById("tipo_usuario");
    const formularioAdministrador = document.getElementById("formulario_Administrador");
    const formularioDocente = document.getElementById("formulario_Docente");
    const formularioEstudiante = document.getElementById("formulario_Estudiante");

    // Ocultar todos los formularios al inicio
    formularioAdministrador.style.display = "none";
    formularioDocente.style.display = "none";
    formularioEstudiante.style.display = "none";

    // Escuchar cambios en el select de tipo de usuario
    tipoUsuarioSelect.addEventListener("change", function () {
        const selectedValue = tipoUsuarioSelect.value;

        // Ocultar todos los formularios primero
        formularioAdministrador.style.display = "none";
        formularioDocente.style.display = "none";
        formularioEstudiante.style.display = "none";

        // Mostrar el formulario correspondiente al valor seleccionado
        if (selectedValue === "admin") {
            formularioAdministrador.style.display = "block";
        } else if (selectedValue === "docente") {
            formularioDocente.style.display = "block";
        } else if (selectedValue === "estudiante") {
            formularioEstudiante.style.display = "block";
        }
    });
});



// Función para obtener el valor de la cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Convierte los datos del formulario a JSON
function formatearJSON(formulario) {
    const objeto = {};
    formulario.forEach((valor, clave) => {
        objeto[clave] = valor;
    });
    return JSON.stringify(objeto);
}



// Función para mostrar el toast con el mensaje de error
function mostrarToastError(mensaje) {
    // Actualizar el contenido del toast
    document.getElementById('toastErrorMessage').innerText = mensaje;

    // Mostrar el toast
    const toastElement = document.getElementById('toastError');
    const toast = new bootstrap.Toast(toastElement);
    toastElement.style.display = 'block'; // Asegurar que esté visible
    toast.show();
}

// Función para mostrar el toast con el mensaje de éxito
function mostrarToastExito(mensaje) {
    // Actualizar el contenido del toast
    document.getElementById('toastSuccessMessage').innerText = mensaje;

    // Mostrar el toast
    const toastElement = document.getElementById('toastSuccess');
    const toast = new bootstrap.Toast(toastElement);
    toastElement.style.display = 'block'; // Asegurar que esté visible
    toast.show();
}

// Guardar los datos del administrador
function guardarDatosAdmin() {
    // Recoger datos del formulario
    const formulario = new FormData(document.getElementById('registroAdministrador'));

    // Convertir datos del formulario a un objeto JSON
    const datosAdmin = formatearJSON(formulario);

    // Enviar datos usando Fetch
    fetch('../registroAdmin/', {
        method: 'POST',
        body: datosAdmin,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito en el toast
            mostrarToastExito('Administrador creado exitosamente');
            document.getElementById('registroAdministrador').reset();
            cargarAdmin();
        } else {
            // Mostrar mensaje de error en el toast
            mostrarToastError(data.error || 'Error desconocido');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToastError('Error en la conexión con el servidor');
    });
}


function eliminarAdministrador(id) {
    // Mostrar el modal de confirmación
    const modalElement = document.getElementById('modalConfirmacion');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Agregar evento al botón de confirmación
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    btnConfirmarEliminar.onclick = function () {
        // Cerrar el modal después de la confirmación
        modal.hide();

        // Realizar la eliminación
        fetch(`../eliminarAdministrador/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), // Incluye el token CSRF
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                mostrarToastExito(data.mensaje); // Mostrar mensaje de éxito
                cargarAdmin(); // Actualizar la lista de administradores
            } else {
                mostrarToastError(data.mensaje); // Mostrar mensaje de error
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarToastError('Error al eliminar al administrador.'); // Mostrar mensaje de error genérico
        });
    };
}



// Cargar los datos del docente en el modal
function obtenerAdministrador(id) {
    fetch(`../obtenerAdministrador/${id}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('administradorId').value = data.id;
            document.getElementById('editarCedulaAdministrador').value = data.cedula;
            document.getElementById('editarDireccionAdministrador').value = data.direccion;
            document.getElementById('editarUsernameAdministrador').value = data.usuario;
            document.getElementById('editarPasswordAdministrador').value = '';
            document.getElementById('editarPrimerNombreAdministrador').value = data.primer_nombre;
            document.getElementById('editarSegundoNombreAdministrador').value = data.segundo_nombre;
            document.getElementById('editarApellidoPaternoAdministrador').value = data.apellido_Paterno;
            document.getElementById('editarApellidoMaternoAdministrador').value = data.apellido_Materno;
            document.getElementById('editarTelefonoAdministrador').value = data.telefono;
            document.getElementById('editarEmailAdministrador').value = data.email;
            var myModalAdministrador = new bootstrap.Modal(document.getElementById('modalEditarAdministrador'));
            myModalAdministrador.show();
        })
        .catch(error => console.error('Error:', error));
}

// Guardar los cambios del docente
function actualizarAdministrador() {
    var formulario = new FormData(document.getElementById('formEditarAdministrador'));
    var datosDeAdministrador = formatearJSON(formulario);
    var administradorId = document.getElementById('administradorId').value;

    // Asegúrate de que los datos no contengan un campo de contraseña vacío
    var datos = JSON.parse(datosDeAdministrador);
    if (!datos.password || datos.password.trim() === '') {
        delete datos.password;
    }
    datosDeAdministrador = JSON.stringify(datos);

    fetch(`../actualizarAdministrador/${administradorId}/`, {
        method: 'POST',
        body: datosDeAdministrador,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        mostrarToastExito('Administrador actualizado exitosamente'); // Mostrar mensaje de éxito
        cargarAdmin(); // Actualizar la lista de administradores
        var myModalEl = document.getElementById('modalEditarAdministrador');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();
    })
    .catch(error => {
        mostrarToastError('Error:', error);
    });
}



function cargarAdmin(){
    fetch('../listadoAdministrador/')
        .then(response => response.text())
            .then(html => {
                document.getElementById('container_listados').innerHTML = html;
                // Inicializa DataTables después de que el contenido se haya cargado
                $('#tbl-admin').DataTable({
                    language: {
                        search: "Buscar:",
                        lengthMenu: "Mostrar _MENU_ registros",
                        info: "Mostrando del _START_ al _END_ de _TOTAL_ registros",
                        paginate: {
                            first: "Primero",
                            last: "Último",
                            next: "Siguiente",
                            previous: "Anterior"
                        }
                    }
                    
                });
        })
        .catch(error => {
            console.error('Error al cargar el listado de Docentes:', error);
    });
}

function ocultarListado() {
    document.getElementById('container_listados').innerHTML = '';
}

