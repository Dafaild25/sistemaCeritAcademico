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

// Mostrar el formulario de asignatura y ocultar la lista de asignaturas
document.getElementById('registroAsignatura').addEventListener('click', function() {
    document.getElementById('formularioAsignatura').classList.remove('hidden');
    document.getElementById('contenedor_clases').classList.add('hidden');
    document.getElementById('tarjetasAsignaturas').classList.add('hidden');
});

// Mostrar la lista de asignaturas y ocultar el formulario
document.getElementById('verAsignatura').addEventListener('click', function() {
    document.getElementById('formularioAsignatura').classList.add('hidden');
    document.getElementById('contenedor_clases').classList.add('hidden');
    document.getElementById('tarjetasAsignaturas').classList.remove('hidden');

    // Cargar tarjetas de asignaturas mediante solicitud AJAX
    fetch('../listar_asignaturas/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'  // Asegúrate de que se envíe el encabezado
        }
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('tarjetasAsignaturas').innerHTML = html;
    })
    .catch(error => {
        console.error('Error al cargar las asignaturas:', error);
    });
});

document.getElementById('verClases').addEventListener('click', function() {
    document.getElementById('formularioAsignatura').classList.add('hidden');
    document.getElementById('tarjetasAsignaturas').classList.add('hidden');
    document.getElementById('contenedor_clases').classList.remove('hidden');

    // Cargar tarjetas de asignaturas mediante solicitud AJAX
    fetch('../listar_asignaturas/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'  // Asegúrate de que se envíe el encabezado
        }
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('tarjetasAsignaturas').innerHTML = html;
    })
    .catch(error => {
        console.error('Error al cargar las asignaturas:', error);
    });
});





//otra funcion para agregar asigantura
function guardarDatosAsignatura() {
    const formulario = new FormData(document.getElementById('asignaturaForm'));
    const datosDeAsignatura = formatearJSON(formulario);

    fetch('../guardarAsignatura', {
        method: 'POST',
        body: datosDeAsignatura,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Asignatura creada exitosamente.');
            alert('Asignatura creada exitosamente.');
            // Resetear el formulario
            document.getElementById('asignaturaForm').reset();
        } else {
            console.log('Error al crear la asignatura:', data.message || 'Error desconocido.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al guardar la asignatura.');

    });
}


// Cargar los datos del docente en el modal
function obtenerAsignatura(id) {
    fetch(`../obtenerAsignatura/${id}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('asignaturaId').value = data.id;
            document.getElementById('editarNombre').value = data.nombre;
            document.getElementById('editarNivel').value = data.nivel;
            document.getElementById('editarEstado').value = data.estado;
            document.getElementById('editarDescripcion').value = data.descripcion;
        
            var myModalAsignatura = new bootstrap.Modal(document.getElementById('editarAsignaturaModal'));
            myModalAsignatura.show();
        })
        .catch(error => console.error('Error:', error));
}

// Guardar los cambios de la asignatura
function actualizarAsignatura() {
    var asignaturaId = document.getElementById('asignaturaId').value;

    // Verifica si el ID se obtiene correctamente
    if (!asignaturaId) {
        console.error("Error: asignaturaId no está definido");
        return;
    }

    var formulario = new FormData(document.getElementById('formEditarAsignatura'));
    var datosDeAsignaturas = formatearJSON(formulario);

    // Enviar solicitud para actualizar la asignatura
    fetch(`/actualizarAsignatura/${asignaturaId}/`, {
        method: 'POST',
        body: datosDeAsignaturas,
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
        cargarAsignaturas();
        listarAsiganturasClase();

        // Cerrar el modal
        var myModalEl = document.getElementById('editarAsignaturaModal');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Esta función debería recargar la lista de asignaturas
function cargarAsignaturas() {
    fetch('../listar_asignaturas/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'  // Asegúrate de que se envíe el encabezado
        }
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('tarjetasAsignaturas').innerHTML = html;
    })
    .catch(error => {
        console.error('Error al cargar las asignaturas:', error);
    });
}



//ahora vamos a eliminar 
function eliminarAsignatura(id) {
    if (confirm('¿Estás seguro de que deseas eliminar esta Asignatura?')) {
        fetch(`../eliminarAsignatura/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),  // Incluye el token CSRF
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                
                // Llama a la función para actualizar la lista de asignaturas
                cargarAsignaturas();
                listarAsiganturasClase();
                
                // Opcionalmente, puedes realizar alguna actualización específica en la UI
            } else {
                console.error('Error al eliminar la asignatura:', data.mensaje);
                alert(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar la asignatura.');
        });
    }
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

            periodoAcademicoClase.innerHTML=opciones  ;
            
            listarCursosClase(data.periodos[0].id);
        } else {
            // Si no hay periodos activos
            periodoAcademicoClase.innerHTML = `<option value='' disabled>No hay periodos activos</option>`;
            console.log('No hay periodos activos.');
            // Aquí puedes mostrar un mensaje en la interfaz de usuario, si lo deseas.

        
        }

    } catch (error) {
        console.log(error);
        
        
    }
}

const listarPeriodosClase = async()=>{
    try {
        const  response = await fetch("../listarPeriodosAcademicos/")
        const data = await response.json();
        if (data.message === "okey") {
            let opciones = ``;
            data.periodos.forEach((periodo) => {
                opciones += `<option value='${periodo.id}'>${periodo.nombre}</option>`;
            });

            cboPeriodo.innerHTML=opciones; 
        
        } else {
            // Si no hay periodos activos
            cboPeriodo.innerHTML = `<option value='' disabled>No hay periodos activos</option>`;
            console.log('No hay periodos activos.');
            // Aquí puedes mostrar un mensaje en la interfaz de usuario, si lo deseas.

        }

    } catch (error) {
        console.log(error);   
    }
}



// teniendo el peridodo  podemos listar los cursos
const listarCursosClase = async(periodo_id)=>{
    try {
        const response = await fetch(`../listarCursosClase/${periodo_id}/`);
        //const response = await fetch('./listarCiudades/1');
        const data =  await response.json();
        if (data.message=="ok"){
            let opciones = ``;
            data.cursos.forEach((cursos)=>{
                opciones+=`<option value= '${cursos.id}'>${cursos.nombre}</option>`;
            })
            cboCursos.innerHTML=opciones;
        }
        else{
            console.log("No se encontraron datos ")
        }    
    } catch (error) {
        
    }
}




// AHORA PODEMOS LISTAR LAS ASIGNATURAS
const listarAsiganturasClase = async()=>{
    try {
        const  response = await fetch("../listarAsignaturasClase")
        const data = await response.json();
        if(data.message === "ok"){
            let opciones = ``
            data.asignaturas.forEach((asignaturas)=>{
                opciones+=`<option value='${asignaturas.id}'>${asignaturas.nombre}</option>`;
            })
            cboAsignatura.innerHTML=opciones  ;
        
        } else {
            // Si no hay asiganturas activos
            cboAsignatura.innerHTML = `<option value='' disabled>No hay  Asignaturas</option>`;
            console.log('No asignaturas activos.');
            // Aquí puedes mostrar un mensaje en la interfaz de usuario, si lo deseas.
        
        }

    } catch (error) {
        console.log(error);
        
        
    }
}
const listarDocentesClase = async()=>{
    try {
        const  response = await fetch("../listarDocentesClase")
        const data = await response.json();
        if(data.message === "ok"){
            let opciones = ``
            data.docentes.forEach((docentes)=>{
                opciones+=`<option value='${docentes.id}'>${docentes.apellido_Paterno} ${docentes.apellido_Materno} ${docentes.primer_nombre} ${docentes.segundo_nombre}</option>`;
            })
            cboDocente.innerHTML=opciones  ;
        
        } else {
            // Si no hay asiganturas activos
            cboDocente.innerHTML = `<option value='' disabled>No hay  Docentes</option>`;
            console.log('No Docentes activos.');
            // Aquí puedes mostrar un mensaje en la interfaz de usuario, si lo deseas.
        
        }

    } catch (error) {
        console.log(error);
        
        
    }
}



//aqui hago que el valor de los periodos academicos  pase  a la filtracion por curso
const cargaInicial = async()=>{
    await listarPeriodos();
    await listarPeriodosClase();
    await listarAsiganturasClase();
    await listarDocentesClase();
    periodoAcademicoClase.addEventListener("change",(event)=>{  //si detecta un cambio este cambiara
        listarCursosClase(event.target.value);
    })

    cboPeriodo.addEventListener('change',(event)=>{
        listarCursosAsignatura();
        
    })

    
}



window.addEventListener("load",async()=>{
    await cargaInicial ();
    $('#agregarClasesModal').on('shown.bs.modal', function () {
        listarAsiganturasClase();
        listarDocentesClase();
        
    });
    
})

// una vez que se cargan yo si puedo guardar
function guardarCursoAsignatura() {
    
    const curso_id = document.getElementById('cboCursos').value;
    const asignatura_id = document.getElementById('cboAsignatura').value;
    const docente_id = document.getElementById('cboDocente').value;

    // Crear un objeto con los datos
    const datosCursoAsignatura = {
        curso_id: curso_id,
        asignatura_id: asignatura_id,
        docente_id: docente_id,
    };

    fetch('../guardarCursoAsignatura', {
        method: 'POST',
        body: JSON.stringify(datosCursoAsignatura),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('CursoAsignatura guardado exitosamente.');
            alert('Curso y Asignatura guardados exitosamente.');
            // Cerrar el modal
            $('#agregarClasesModal').modal('hide');
            // Resetear el formulario
            document.getElementById('formAgregarClases').reset();
            listarCursosAsignatura();
           
        } else {
            console.log('Error al guardar CursoAsignatura:', data.message || 'Error desconocido.');
            alert('Error al crear CursoAsignatura: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al guardar el curso y asignatura.');
    });
}




function listarCursosAsignatura() {
    const periodo_id = document.getElementById('cboPeriodo').value;
    const contenedor = document.getElementById('contenedor_cursoAsignatura');

    // Limpiar el contenedor antes de realizar la solicitud
    contenedor.innerHTML = '';
    // Verificar si periodo_id es válido
    if (!periodo_id) {
        contenedor.innerHTML = '<div class="alert alert-warning">No se ha seleccionado un periodo.</div>';
        return;
    }

    document.getElementById('contenedor_cursoAsignatura').innerHTML = '';
    fetch(`../listarCursosAsignatura/${periodo_id}/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor_cursoAsignatura').innerHTML = html;

            // Inicializa DataTables
            $('#tbl-clases').DataTable({
                language: {
                    search: "Buscar:", // Texto de búsqueda
                
                },
                paging: false,          // Desactiva la paginación
                ordering: false,        // Desactiva las flechas de ordenamiento
                info: false,             // Desactiva el texto de información de la tabla
                scrollX: true,          // Activa el desplazamiento horizontal
                fixedHeader: true,    // Hace que la tabla sea más amigable en dispositivos móviles
            });
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
            contenedor.innerHTML = '<div class="alert alert-danger">Error al cargar el listado de cursos. Inténtalo nuevamente más tarde.</div>';
        });
}


// esta es igual al funcion listarCursosAsignatura pero solicitando un periodo
function listarClases(periodo_id){
    document.getElementById('contenedor_cursoAsignatura').innerHTML = '';
    fetch(`../listarCursosAsignatura/${periodo_id}/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor_cursoAsignatura').innerHTML = html;
            // Inicializa DataTables
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
            contenedor.innerHTML = '<div class="alert alert-danger">Error al cargar el listado de cursos. Inténtalo nuevamente más tarde.</div>';
        });
}


function vistaClases(){
    const periodo_id = document.getElementById('cboPeriodo').value;

    if (!periodo_id) {
        document.getElementById('contenedor_cursoAsignatura').innerHTML = 
            '<div class="alert alert-warning">No hay ningún periodo académico activo.</div>';
        return; // Detenemos la ejecución de la función si no hay periodo
    }
    document.getElementById('contenedor_cursoAsignatura').innerHTML = '';
    fetch(`../vistaClases`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor_cursoAsignatura').innerHTML = html;
            // Inicializa DataTables
            listarClases(periodo_id)
            
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
            contenedor.innerHTML = '<div class="alert alert-danger">Error al cargar el listado de cursos. Inténtalo nuevamente más tarde.</div>';
        });
}









// ahora hacemos la funcionalidad de eliminar 
function eliminarCursoAsigantura(id) {
    const periodo_id = document.getElementById('cboPeriodo').value;
    if (confirm('¿Estás seguro de que deseas eliminar esta clase?')) {
        fetch(`../eliminarCursoAsigantura/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),  // Incluye el token CSRF
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                
                // Llama a la función para actualizar la lista las  clases o cursoAsignatura
                listarCursosAsignatura();
                
                // Opcionalmente, puedes realizar alguna actualización específica en la UI
            } else {
                console.error('Error al eliminar la Clase:', data.mensaje);
                alert(data.mensaje);
                
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar la clase.');
            listarCursoAsignaturaEliminar(periodo_id);
        });
    }
}




async function importarClases() {
    // Obtén el formulario por su ID
    const form = document.getElementById('formImportar');

    // Verifica si el formulario y el input están disponibles
    if (!form) {
        alert('Formulario no encontrado.');
        return;
    }

    // Crea un FormData con el formulario completo
    const formData = new FormData(form);

    try {
        const response = await fetch('../importar-clases/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Incluye el token CSRF para la protección de Django
            }
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message || 'Clases importadas correctamente.');

            // Cierra el modal después de importar las clases
            const modalElement = document.getElementById('importarClasesModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();

              // Limpiar el formulario después de cerrar el modal
              form.reset();

            // Aquí puedes actualizar la lista de clases o realizar otra acción
            vistaClases();
        } else {
            alert(result.message || 'Hubo un problema al importar las clases.');
        }
    } catch (error) {
        alert('Error al enviar el archivo.');
        console.error('Error:', error);
    }
}

async function importarAsignaturas() {
    // Obtén el formulario por su ID
    const form = document.getElementById('formImportarAsignatura');

    // Verifica si el formulario y el input están disponibles
    if (!form) {
        alert('Formulario no encontrado.');
        return;
    }

    // Crea un FormData con el formulario completo
    const formData = new FormData(form);

    try {
        const response = await fetch('/importar-asignaturas/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Incluye el token CSRF para la protección de Django
            }
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message || 'Asignaturas importadas correctamente.');

            // Cierra el modal después de importar las clases
            const modalElement = document.getElementById('importarAsignaturasModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();

              // Limpiar el formulario después de cerrar el modal
              form.reset();

            // Aquí puedes actualizar la lista de clases o realizar otra acción
           cargarAsignaturas()
        } else {
            alert(result.message || 'Hubo un problema al importar las clases.');
        }
    } catch (error) {
        alert('Error al enviar el archivo.');
        console.error('Error:', error);
    }
}