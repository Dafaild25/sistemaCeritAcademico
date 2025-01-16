
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
function formatearJSON(formData) {
    const object = {};
    formData.forEach((value, key) => {
        object[key] = value;
    });
    return JSON.stringify(object);
}

// primero hay que listar los Periodos
const listarPeriodos = async()=>{
    try {
        const  response = await fetch("../listarPeriodosAcademicos/")
        const data = await response.json();
        if(data.message === "okey"){
            let opciones = ``
            data.periodos.forEach((periodos)=>{
                opciones+=`<option value='${periodos.id}'>${periodos.nombre}</option>`;
            })
            periodoAcademico.innerHTML=opciones  ;
            listarCursos(data.periodos[0].id);
        } else {
            // Si no hay periodos activos
            periodoAcademico.innerHTML = `<option value='' disabled>No hay periodos activos</option>`;
            console.log('No hay periodos activos.');
            // Aquí puedes mostrar un mensaje en la interfaz de usuario, si lo deseas.
        
        }

    } catch (error) {
        console.log(error);
        
        
    }
}

//ahora si seleciono un periodo academico voy a poder ver los cursos y llamo que se ingrese
const listarCursos = async(idPeriodo)=>{
    fetch(`../listarCursosPeriodo/${idPeriodo}/`)
        .then(response => response.text())
            .then(html => {
                document.getElementById('contenedor_tarjetas').innerHTML = html;
                
            
        })
        .catch(error => {
            console.error('Error al cargar el listado de Asignaturas:', error);
    });
}

//aqui hago que el valor de los periodos academicos  pase  a la filtracion por curso
const cargaInicial = async()=>{
    await listarPeriodos();
    periodoAcademico.addEventListener("change",(event)=>{  //si detecta un cambio este cambiara
        listarCursos(event.target.value);
    })
    
}

function cerrarAccordion() {
    var accordionCollapse = document.getElementById('panelsStayOpen-collapseTres');
    var bsCollapse = new bootstrap.Collapse(accordionCollapse, {
        toggle: false
    });
    if (accordionCollapse.classList.contains('show')) {
        bsCollapse.hide();
    }
}









//cuando la ventana este cargada se ejecutara la carga inicial
window.addEventListener("load",async()=>{
    await cargaInicial()
    
})


function listarEstudiantes(cursoId) {
    document.getElementById('curso_id').value = cursoId;
    document.getElementById('contenedor_estudiantes').style.display = 'block';

    fetch(`../listarEstudiantes/?curso_id=${cursoId}`)
        .then(response => response.text())
            .then(html => {
                cerrarAccordion()
                document.getElementById('listado_estudiantes').innerHTML = html;
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
                console.error('Error al obtener estudiantes:', error);
               
        });
}

function enviarArchivo() {
    const cursoId = document.getElementById('curso_id').value;
    const formData = new FormData(document.getElementById('importarForm'));
    $('#loadingModal').modal('show');
    fetch('/importarEstudiantes/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        $('#loadingModal').modal('hide');
        if (data.success) {
            alert(data.message);
            // Limpia el formulario
            document.getElementById('importarForm').reset();
            // Llama a listarEstudiantes para recargar la tabla
            listarEstudiantes(cursoId); // Pasa el cursoId para recargar la tabla
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        $('#loadingModal').modal('hide');
        console.error('Error al importar estudiantes:', error);
        alert('Hubo un error al importar los estudiantes.');
    });
}

function ocultarListado() {
    document.getElementById('contenedor_estudiantes').style.display = 'none';
}

// Función para redirigir a la página de edición con el ID del estudiante
function editarEstudiante(estudianteId) {
    // Redirigir a la página de edición con el ID del estudiante en la URL
    window.location.href = `../datosEstudiantes/?id=${estudianteId}`;    
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

// Guardar los cambios del estudiante
function actualizarDatosEstudiante() {
    var formulario = new FormData(document.getElementById('formEditarEstudiante'));
    var datosDeEstudiante = formatearJSON(formulario);
    var estudianteId = document.getElementById('estudianteId').value;

    // Asegúrate de que los datos no contengan un campo de contraseña vacío
    var datos = JSON.parse(datosDeEstudiante);
    if (!datos.password || datos.password.trim() === '') {
        delete datos.password;
    }
    datosDeEstudiante = JSON.stringify(datos);

    fetch(`../actualizarDatosEstudiante/${estudianteId}/`, {
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
        window.location.href = `../adminCurso/`;  
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

//Necesito eliminar una matricula y recargar la lista de estudiantes
function eliminarMatricula(estudianteId) {
    const cursoId = document.getElementById('curso_id').value;
    if (confirm("¿Estás seguro de que deseas eliminar esta matrícula?")) {
        fetch(`/eliminarMatricula/${estudianteId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Asegúrate de que la CSRF token se pase correctamente
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                alert(data.mensaje);
                // Llama a listarEstudiantes para recargar la tabla
                listarEstudiantes(cursoId);  // Pasa el cursoId para que la tabla se actualice
            } else {
                alert(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error al intentar eliminar la matrícula:', error);
            alert('Hubo un error al intentar eliminar la matrícula.');
        });
    }
}

//Necesito matricular individualmente

function matriculaIndividual() {
    // Obtén los valores del formulario
    const estudianteSelect = document.getElementById('estudiante');
    const estadoSelect = document.getElementById('estado_matricula');
    const cursoId = document.getElementById('curso_id').value;

    const estudianteId = estudianteSelect.value;
    const estado = estadoSelect.value;

    // Verifica que se haya seleccionado un estudiante y un estado
    if (!estudianteId || !estado) {
        alert('Por favor, completa todos los campos.');
        return;
    }

    // Crea un FormData para enviar los datos del formulario
    const formData = new FormData();
    formData.append('estudiante', estudianteId);
    formData.append('estado_matricula', estado);
    formData.append('curso_id', cursoId);

    $('#loadingModal').modal('show');

    // Enviar la petición al servidor
    fetch('../matriculaIndividual/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')  // Agrega el CSRF token
        }
    })
    .then(response => response.json())
    .then(data => {
        $('#loadingModal').modal('hide');
        if (data.success) {

            // Limpia el formulario 
            document.getElementById('matriculaForm').reset();
            // Llama a listarEstudiantes para recargar la tabla
            listarEstudiantes(cursoId); // Pasa el cursoId para recargar la tabla
            alert(data.message);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        $('#loadingModal').modal('hide');
        console.error('Error:', error);
        alert('Hubo un problema con la matrícula.');
    });
}




function cargarDatosModal(matriculaId) {
    fetch(`../obtener_matricula/?id=${matriculaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
            } else {
                document.getElementById('edit-matricula-id').value = data.id;
                document.getElementById('edit-estudiante-id').value = data.estudiante_id;
                document.getElementById('edit-curso-id').value = data.curso_id;
                document.getElementById('edit-estado').value = data.estado;

                // Mostrar el modal
                var editModal = new bootstrap.Modal(document.getElementById('editMatriculaModal'));
                editModal.show();
            }
        })
        .catch(error => console.error('Error:', error));
}

function editarMatricula(id) {
    cargarDatosModal(id);
}

function guardarCambios() {
    const cursoId = document.getElementById('curso_id').value;
    const form = document.getElementById('editMatriculaForm');
    const formData = new FormData(form);

    fetch('../actualizar_matricula/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Matrícula actualizada correctamente');
            // Cerrar el modal
            $('#editMatriculaModal').modal('hide');
            // Llama a listarEstudiantes para recargar la tabla
            listarEstudiantes(cursoId); // Pasa el cursoId para recargar la tabla
        } else {
            alert('Error al actualizar matrícula: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

fetch('../cargar_estudiantes/')
.then(response => {
    if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
    }
    return response.json();
})
.then(data => {
    const selectEstudiante = document.getElementById('estudiante');
    data.forEach(estudiante => {
        const option = document.createElement('option');
        option.value = estudiante.id;
        option.textContent = `${estudiante.cedula} ${estudiante.apellido_Paterno} ${estudiante.apellido_Materno} ${estudiante.primer_nombre} ${estudiante.segundo_nombre} `;
        selectEstudiante.appendChild(option);
    });
})
.catch(error => {
    console.error("Error al cargar estudiantes:", error);
});