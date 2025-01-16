
//esta es una funcion  que ayuda a cifrar es de la documentacion 
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

//aqui convierte los datos del input a tipo json nos evita escribir 
function formatearJSON(formData) {
    const object = {};
    formData.forEach((value, key) => {
        object[key] = value;
    });
    return JSON.stringify(object);
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


// Guardar los datos del docente
function guardarDatosDocente() {
    // Recoger datos del formulario
    const formulario = new FormData(document.getElementById('registroDocente'));

    // Convertir datos del formulario a un objeto JSON
    const datosDocente = formatearJSON(formulario);

    // Enviar datos usando Fetch
    fetch('../registroDocente/', {
        method: 'POST',
        body: datosDocente,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito en el toast
            mostrarToastExito('Docente creado exitosamente');
            document.getElementById('registroDocente').reset();
            cargarDocentes();
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

// Cargar los datos del docente en el modal
function editarDocente(id) {
    fetch(`../obtenerDocente/${id}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('docenteId').value = data.id;
            document.getElementById('editarCedulaDocente').value = data.cedula;
            document.getElementById('editarUsernameDocente').value = data.usuario;
            document.getElementById('editarPasswordDocente').value = '';
            document.getElementById('editarPrimerNombreDocente').value = data.primer_nombre;
            document.getElementById('editarSegundoNombreDocente').value = data.segundo_nombre;
            document.getElementById('editarApellidoPaternoDocente').value = data.apellido_Paterno;
            document.getElementById('editarApellidoMaternoDocente').value = data.apellido_Materno;
            document.getElementById('editarEspecialidadDocente').value = data.especialidad;
            document.getElementById('editarTelefonoDocente').value = data.telefono;
            document.getElementById('editarDireccionDocente').value = data.direccion;
            document.getElementById('editarEmailDocente').value = data.email;
            document.getElementById('editarEstadoDocente').value = data.estado;
            var myModalDocente = new bootstrap.Modal(document.getElementById('modalEditarDocente'));
            myModalDocente.show();
        })
        .catch(error => console.error('Error:', error));
}

// Guardar los cambios del docente
function actualizarDocente() {
    var formulario = new FormData(document.getElementById('formEditarDocente'));
    var datosDeDocentes = formatearJSON(formulario);
    var docenteId = document.getElementById('docenteId').value;

    // Asegúrate de que los datos no contengan un campo de contraseña vacío
    var datos = JSON.parse(datosDeDocentes);
    if (!datos.password || datos.password.trim() === '') {
        delete datos.password;
    }
    datosDeDocentes = JSON.stringify(datos);

    fetch(`../actualizarDocente/${docenteId}/`, {
        method: 'POST',
        body: datosDeDocentes,
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
        mostrarToastExito('Docente actualizado exitosamente'); 
        cargarDocentes();
        var myModalEl = document.getElementById('modalEditarDocente');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();
    })
    .catch(error => {
        mostrarToastError('Error:', error);
    });
}




function eliminarDocente(id) {
         // Mostrar el modal de confirmación
    const modalElement = document.getElementById('modalConfirmacion');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Agregar evento al botón de confirmación
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    btnConfirmarEliminar.onclick = function () {
        // Cerrar el modal después de la confirmación
        modal.hide();
        fetch(`../eliminarDocente/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),  // Incluye el token CSRF
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                mostrarToastExito(data.mensaje); // Mostrar mensaje de éxito
                cargarDocentes(); // Actualizar la lista de administradores
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

async function enviarArchivo() {
    // Obtén el formulario por su ID
    const form = document.getElementById('importarForm');

    // Verifica si el formulario y el input están disponibles
    if (!form) {
        alert('Formulario no encontrado.');
        return;
    }

    // Crea un FormData con el formulario completo
    const formData = new FormData(form);

    try {
        const response = await fetch('../importar_docentes/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Incluye el token CSRF para la protección de Django
            }
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message || 'Docentes importados correctamente.');
            cargarDocentes();
        } else {
            alert(result.message || 'Hubo un problema al importar los docentes.');
        }
    } catch (error) {
        alert('Error al enviar el archivo.');
        console.error('Error:', error);
    }
}

function cargarDocentes(){
    fetch('../listadoDocentes/')
        .then(response => response.text())
            .then(html => {
                document.getElementById('container_listados').innerHTML = html;
                // Inicializa DataTables después de que el contenido se haya cargado
                $('#tbl-docentes').DataTable({
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