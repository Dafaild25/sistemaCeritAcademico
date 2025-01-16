// Función para obtener el valor de una cookie por su nombre
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


// Convierte los datos del formulario a JSON
function formatearJSON(formulario) {
    const objeto = {};
    formulario.forEach((valor, clave) => {
        objeto[clave] = valor.trim();
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

function guardarDatosEstudiante() {
     // Recoger datos del formulario
     const formulario = new FormData(document.getElementById('registroEstudiante'));

     // Convertir datos del formulario a un objeto JSON
     const datosEstudiante = formatearJSON(formulario);
 
     // Enviar datos usando Fetch
     fetch('../registroEstudiante/', {
         method: 'POST',
         body: datosEstudiante,
         headers: {
             'Content-Type': 'application/json',
             'X-CSRFToken': getCookie('csrftoken'),
         }
     })
     .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito en el toast
            mostrarToastExito('Estudiante creado exitosamente');
            document.getElementById('registroEstudiante').reset();
            cargarEstudiantes();
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




function eliminarEstudiante(id) {
    // Mostrar el modal de confirmación
    const modalElement = document.getElementById('modalConfirmacion');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Agregar evento al botón de confirmación
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    btnConfirmarEliminar.onclick = function () {
        // Cerrar el modal después de la confirmación
        modal.hide();
        fetch(`../eliminarEstudiante/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),  // Incluye el token CSRF
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                mostrarToastExito(data.mensaje);
                
                // Llama a la función para actualizar la lista de estudiantes
                cargarEstudiantes();
                
                // Opcionalmente, puedes realizar alguna actualización específica en la UI
            } else {
                mostrarToastError(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarToastError('Error al eliminar al estudiante.');
        });
    }
}

// Función para redirigir a la página de edición con el ID del estudiante
function editarEstudiante(estudianteId) {
    // Redirigir a la página de edición con el ID del estudiante en la URL
    window.location.href = `../editarEstudiante/?id=${estudianteId}`;    
}

document.addEventListener('DOMContentLoaded', () => {
    // Obtener el ID del estudiante desde los parámetros de URL
    const urlParams = new URLSearchParams(window.location.search);
    const estudianteId = urlParams.get('id');

    if (estudianteId) {
        // Realizar una solicitud para obtener los datos del estudiante
        fetch(`../obtenerEstudiante/${estudianteId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta de la red');
                }
                return response.json();
            })
            .then(data => {
                // Rellenar el formulario con los datos obtenidos
                document.getElementById('editarUsername').value = data.usuario || '';
                document.getElementById('estudianteId').value = data.id || '' ;
                document.getElementById('editarCedula_estudiante').value = data.cedula || '';
                document.getElementById('editarPrimer_nombre_estudiante').value = data.primer_nombre || '';
                document.getElementById('editarSegundo_nombre_estudiante').value = data.segundo_nombre || '';
                document.getElementById('editarApellido_Paterno_estudiante').value = data.apellido_Paterno || '';
                document.getElementById('editarApellido_Materno_estudiante').value = data.apellido_Materno || '';
                document.getElementById('editarTelefono_estudiante').value = data.telefono || '';
                document.getElementById('editarEmail_estudiante').value = data.email || '';
                document.getElementById('editarFecha_nacimiento_estudiante').value = data.fecha_nacimiento || '';
                document.getElementById('editarEstado_estudiante').value = data.estado || '';
                document.getElementById('editarCiudad_estudiante').value = data.ciudad || '';
                document.getElementById('editarDireccion_estudiante').value = data.direccion || '';

                //REPRESENTANTE 1
                document.getElementById('editarCedula_R1').value = data.cedula_R1 || '';
                document.getElementById('editarNombres_R1').value = data.nombres_R1 || '';
                document.getElementById('editarApellido_Paterno_R1').value = data.apellido_paterno_R1 || '';
                document.getElementById('editarApellido_Materno_R1').value = data.apellido_materno_R1 || '';
                document.getElementById('editarEmail_R1').value = data.email_R1 || '';
                document.getElementById('editarCelular_R1').value = data.celular_R1 || '';
                document.getElementById('editarParentesco_R1').value = data.parentesco_R1 || '';
                document.getElementById('editarEstado_R1').value = data.estado_R1 || '';
                
                //REPRESENTANTE 2
                document.getElementById('editarCedula_R2').value = data.cedula_R2 || '';
                document.getElementById('editarNombres_R2').value = data.nombres_R2 || '';
                document.getElementById('editarApellido_Paterno_R2').value = data.apellido_paterno_R2 || '';
                document.getElementById('editarApellido_Materno_R2').value = data.apellido_materno_R2 || '';
                document.getElementById('editarEmail_R2').value = data.email_R2 || '';
                document.getElementById('editarCelular_R2').value = data.celular_R2 || '';
                document.getElementById('editarParentesco_R2').value = data.parentesco_R2 || '';
                document.getElementById('editarEstado_R2').value = data.estado_R2 || '';

                //REPRENSENTANTE 3
                document.getElementById('editarCedula_R3').value = data.cedula_R3 || '';
                document.getElementById('editarNombres_R3').value = data.nombres_R3 || '';
                document.getElementById('editarApellido_Paterno_R3').value = data.apellido_paterno_R3 || '';
                document.getElementById('editarApellido_Materno_R3').value = data.apellido_materno_R3 || '';
                document.getElementById('editarEmail_R3').value = data.email_R3 || '';
                document.getElementById('editarCelular_R3').value = data.celular_R3 || '';
                document.getElementById('editarParentesco_R3').value = data.parentesco_R3 || '';
                document.getElementById('editarEstado_R3').value = data.estado_R3 || '';

                
                // Agrega más campos según sea necesario
            })
            .catch(error => console.error('Error al obtener los datos del estudiante:', error));
    } else {
        console.error('No se encontró el ID del estudiante en la URL');
    }
});

// Guardar los cambios del docente
function actualizarEstudiante() {
    var formulario = new FormData(document.getElementById('formEditarEstudiante'));
    var datosDeEstudiante = formatearJSON(formulario);
    var estudianteId = document.getElementById('estudianteId').value;

    // Asegúrate de que los datos no contengan un campo de contraseña vacío
    var datos = JSON.parse(datosDeEstudiante);
    if (!datos.password || datos.password.trim() === '') {
        delete datos.password;
    }
    datosDeEstudiante = JSON.stringify(datos);

    fetch(`../actualizarEstudiante/${estudianteId}/`, {
        method: 'POST',
        body: datosDeEstudiante,
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
        console.log(data.message || data.error);
        window.location.href = `../registro/`;  
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function cargarEstudiantes(){
    fetch('../listadoEstudiantes/')
        .then(response => response.text())
            .then(html => {
                document.getElementById('container_listados').innerHTML = html;
                // Inicializa DataTables después de que el contenido se haya cargado
                $('#tbl-estudiantes').DataTable({
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