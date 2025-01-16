
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
        const  response = await fetch("../listarPeriodosAcademicosReportes/")
        const data = await response.json();
        if(data.message === "okey"){
            let opciones = ``
            data.periodos.forEach((periodos)=>{
                opciones+=`<option value='${periodos.id}'>${periodos.nombre}</option>`;
            })
            periodoAcademico.innerHTML=opciones  ;
            listarCursosReportes(data.periodos[0].id);
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
// aqui vamos a listar los cursos y llamaremos al template que se inserte en un contenedor 
function listarCursosReportes(periodo_id) {
    // Limpia el contenedor antes de cargar los nuevos datos
    document.getElementById('contenedor_tarjetas').innerHTML = '';

    // Realiza la petición fetch a la URL creada
    fetch(`../listarCursosReportes/${periodo_id}/`)
        .then(response => response.text())
        .then(html => {
            // Inserta el HTML recibido en el contenedor
            document.getElementById('contenedor_tarjetas').innerHTML = html;
            // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
        });
}

// desde aqui va la segunda opcion

function vistaTrimestresReportes(clase_id){
    // Asegúrate de que periodoTrabajo está correctamente definido
    const periodoReporte = document.getElementById('periodoReporte'); // Reemplaza 'id-del-periodo-trabajo' con el ID correcto
    
    if (periodoReporte) { // Verifica que periodoTrabajo no sea null o undefined
        const periodo_id = periodoReporte.getAttribute('data-periodoReporte');
        
        document.getElementById('contenedor_trimestres').innerHTML = '';
        
        // Realiza la petición fetch a la URL creada
        fetch(`../vistaTrimestresReportes/${clase_id}/`)
            .then(response => response.text())
            .then(html => {
                cerrarAccordion();
                // Inserta el HTML recibido en el contenedor
                document.getElementById('contenedor_trimestres').innerHTML = html;
                // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
                cargarTrimestresReportes(periodo_id);
            })
            .catch(error => {
                console.error('Error al cargar el listado de aportes:', error);
            });
    } else {
        console.error('Elemento periodoTrabajo no encontrado');
    }
}



function cargarTrimestresReportes(periodo_id) {

    if (!periodo_id) {
        console.error("El ID del periodo no es válido.");
        return;
    }
    fetch(`../listarTrimestresReportes/${periodo_id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.message === "ok") {
                const select = document.getElementById('cboTrimestreReportes');
                select.innerHTML = '<option value="">Selecciona un trimestre o unidad</option>';
                // para la opcion general 
                const calificacionGeneralAdminOption = document.createElement('option');
                calificacionGeneralAdminOption.value =`periodo_${data.periodo_id}`;
                calificacionGeneralAdminOption.textContent = 'REPORTE GENERAL';
                select.appendChild(calificacionGeneralAdminOption);

                // trimestres y unidades 
                data.trimestres.forEach(trimestre => {
                    const option = document.createElement('option');
                    option.value = `trimestre_${trimestre.id}`;
                    option.textContent = trimestre.nombre;
                    select.appendChild(option);
                

                    trimestre.unidades.forEach(unidad=>{
                        const unidadOption = document.createElement('option');
                        unidadOption.value = `unidad_${unidad.id}`;
                        unidadOption.textContent = '    ' + unidad.nombre; // Sangría para las unidades
                        unidadOption.style.fontSize = '0.9em';
                        select.appendChild(unidadOption);
                    });
                });

                // Configura el manejador de eventos para el cambio en el select
                select.addEventListener('change', function () {
                    const selectedValue = this.value;
                    const selectedId = selectedValue.split('_')[1];
                    const claseId = document.getElementById('claseReporte').value;
                    
                    if (selectedValue.startsWith('periodo_')) {
                        console.log('Seleccionado el reporte general');
                        cargarVistaCalificacionGeneralAdmin(selectedId,claseId);
                        


                    } else if (selectedValue.startsWith('trimestre_')) {
                        cargarReportesTrimestrales(selectedId, claseId);
                        //cargarReportesUnidad(selectedId, claseId);
                    
                    } else if (selectedValue.startsWith('unidad_')) {
                        cargarReportesUnidad(selectedId, claseId);
                    }
                });

            } else {
                console.error("Error en la respuesta del servidor:", data.message);
            }
        })
        .catch(error => console.error("Error al cargar los trimestres:", error));
}

function cargarReportesUnidad(unidad_id, clase_id,posicionScroll){
    const contenedorAportes = document.getElementById('reportes-Trimestrales');
    fetch(`../vistaReporteUnidad/${unidad_id}/${clase_id}/`)
   // Realiza la petición fetch a la URL creada
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        contenedorAportes.innerHTML = html;
        // Selecciona las celdas con la clase grade-column
            const tablaReportes = document.getElementById('tbl-reportes-unidad');
            
            // Verifica que la tabla exista
            if (!tablaReportes) {
                console.error('No se encontró el contenedor de la tabla.');
                return; // Salir de la función si el contenedor no existe
            }

        
            $('#tbl-reportes-unidad').DataTable({
                language: {
                    search: "Buscar:",
                },
                paging: false,          // Desactiva la paginación
                ordering: false,        // Desactiva las flechas de ordenamiento
                info: false,             // Desactiva el texto de información de la tabla
                scrollX: true,          // Activa el desplazamiento horizontal
                fixedHeader: true,      // Fija el encabezado y el buscador
            });
            
            setTimeout(() => {
            const contenedorTabla = tablaReportes.parentElement; // Asegúrate de tener acceso a la tabla
        
            // Verifica si posicionScroll está vacío y establece la posición adecuada
            const posicionHorizontal = posicionScroll ? parseFloat(posicionScroll) : contenedorTabla.scrollWidth;
        
            // Desplazamiento horizontal en el contenedor de la tabla
            contenedorTabla.scrollTo({
                left: posicionHorizontal,
                behavior: 'smooth' // Desplazamiento suave
            });
         }, 100); // Ajusta el tiempo según lo necesites 
            
        
    })
    .catch(error => {
        console.error('Error al cargar el listado de cursos:', error);
    });
}

// aqui cargo los apores 
function cargarReportesTrimestrales(trimestreId, claseId) {
    // Limpia el contenedor antes de cargar los nuevos datos
    //document.getElementById('contenedor-aportes-trimestrales').innerHTML = '';
    const contenedorAportes = document.getElementById("reportes-Trimestrales");
    const currentScrollPosition = contenedorAportes.scrollTop;
    // Realiza la petición fetch a la URL creada
    fetch(`../vistaCalificacionTrimestreAdmin/${trimestreId}/${claseId}/`)
   // Realiza la petición fetch a la URL creada
    .then(response => response.text())
    .then(html => {
        // Inserta el HTML recibido en el contenedor
        document.getElementById("reportes-Trimestrales").innerHTML = html;
        // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
        // Restaura la posición del scroll al valor guardado
        contenedorAportes.scrollTop = currentScrollPosition;
        cargarSubpromediosUnidadesAdmin(claseId);
        cargarCalificacionesExamenAdmin(claseId);
        cargarPromediosTrimestralesAdmin(claseId);
        $('#tbl-reportes-trimestrales').DataTable({
            language: {
                search: "Buscar:",
            },
            paging: false,          // Desactiva la paginación
            ordering: false,        // Desactiva las flechas de ordenamiento
            info: false,             // Desactiva el texto de información de la tabla
            scrollX: true,          // Activa el desplazamiento horizontal
            fixedHeader: true,      // Fija el encabezado y el buscador
        });
        
       
        
    })
    .catch(error => {
        console.error('Error al cargar el listado de cursos:', error);
    });
}



function cargarVistaCalificacionGeneralAdmin(periodo_id,clase_id,posicionScroll) {
    
    const contenedorAportes = document.getElementById("reportes-Trimestrales");
    
    fetch(`../vistaCalificacionGeneralAdmin/${periodo_id}/${clase_id}/`)
   
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        contenedorAportes.innerHTML = html;
        // Selecciona las celdas con la clase grade-column
            const tablaAportes = document.getElementById('tbl-calificacion-general-admin');
            
            // Verifica que la tabla exista
            if (!tablaAportes) {
                console.error('No se encontró el contenedor de la tabla.');
                return; // Salir de la función si el contenedor no existe
            }
            
        
            $('#tbl-calificacion-general-admin').DataTable({
                language: {
                    search: "Buscar:",
                },
                paging: false,          // Desactiva la paginación
                ordering: false,        // Desactiva las flechas de ordenamiento
                info: false,             // Desactiva el texto de información de la tabla
                scrollX: true,          // Activa el desplazamiento horizontal
                fixedHeader: true,      // Fija el encabezado y el buscador
            });
            obtenerPromediosGeneralesTrimestralesAdmin();
            obtenerPromediosGeneralesAdmin(clase_id,periodo_id);
            calcularPromedioClaseGeneralAdmin(clase_id);
            cargarCalificacionesSupletorioAdmin();

            setTimeout(() => {
            const contenedorTabla = tablaAportes.parentElement; // Asegúrate de tener acceso a la tabla
        
            // Verifica si posicionScroll está vacío y establece la posición adecuada
            const posicionHorizontal = posicionScroll ? parseFloat(posicionScroll) : contenedorTabla.scrollWidth;
        
            // Desplazamiento horizontal en el contenedor de la tabla
            contenedorTabla.scrollTo({
                left: posicionHorizontal,
                behavior: 'smooth' // Desplazamiento suave
            });
         }, 100); // Ajusta el tiempo según lo necesites 
            
        
    })
    .catch(error => {
        console.error('Error al cargar el listado de cursos:', error);
    });
}



function cargarSubpromediosUnidadesAdmin(clase_Id) {
    // Seleccionar todas las celdas donde se va a mostrar la calificación
    const celdasCalificacion = document.querySelectorAll('.calificacion-unidad');
    
    // Para cada celda, obtener los IDs y hacer la solicitud para obtener la calificación
    celdasCalificacion.forEach(celda => {
        const matriculaId = celda.dataset.matriculaId;
        const unidadId = celda.dataset.unidadId;
        const trimestreId = celda.dataset.trimestreId;
        

        // Hacer una solicitud a la vista que retorna el subPromedioUnidad
        fetch(`../obtenerSubPromedioUnidadAdmin/${unidadId}/${matriculaId}/${trimestreId}/${clase_Id}`)
            .then(response => response.json())
            .then(data => {
                // Si la respuesta es exitosa, actualizar el valor de la celda
                if (!data.error) {
                    celda.textContent = data.subPromedio;
                } else {
                    celda.textContent = "Error";
                }
            })
            .catch(error => {
                console.error('Error:', error);
                celda.textContent = "Error";
            });
    });
}


const listarEstudiantes = async (cursoId) => {
    try {
        const response = await fetch(`../listarEstudiantes/${cursoId}/`);
        
        if (!response.ok) {
            throw new Error('Error en la solicitud');
        }
        
        const html = await response.text();  // Obtener el HTML generado desde Django

        // Insertar el HTML de la tabla de estudiantes en el contenedor correspondiente
        document.getElementById('contenedor_tabla_estudiantes').innerHTML = html;

    } catch (error) {
        console.error('Error al listar los estudiantes:', error);
    }
};


//aqui hago que el valor de los periodos academicos  pase  a la filtracion por curso
const cargaInicial = async()=>{
    await listarPeriodos();
    periodoAcademico.addEventListener("change",(event)=>{  //si detecta un cambio este cambiara
        listarCursosReportes(event.target.value);
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


function ocultarListado() {
    document.getElementById('contenedor_tabla_estudiantes').innerHTML = '';
}
function ocultarAsignaturas() {
    document.getElementById('contenedor_asignaturas').innerHTML = '';
}





// puede crear aportes 
function abrirModalYcargarTiposConUnidad(trimestreId) {
    const crearAporteModal = new bootstrap.Modal(document.getElementById('crearAporteModalAdmin'));
    
    // Llama a la función que carga los tipos de evaluación
    cargarTiposDeEvaluacionCalificacion(trimestreId)
        .then(() => {

            // Si se cargan correctamente, muestra el modal
            setFechaActual('fechaAporteAdmin');
            crearAporteModal.show();
        })
        .catch(error => {
            console.error('Error al cargar los tipos de evaluación:', error);
            alert('Hubo un problema al cargar los tipos de evaluación. Inténtalo de nuevo.');
        });
}


// reutilizo el link que tengo
// aqui llamamos a las urls de Clase Trabajo
function cargarTiposDeEvaluacionCalificacion(trimestreId) {
    return fetch(`../listartiposPorTrimestre/${trimestreId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.message === "ok") {
                const selectTipo = document.getElementById('cboAporteTrimestralAdmin');
                selectTipo.innerHTML = '<option value="">Selecciona un tipo de evaluación</option>';
                data.tipoEvaluacion.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo.id;
                    option.textContent = tipo.nombre;
                    selectTipo.appendChild(option);
                });
            } else {
                console.error('No hay datos disponibles para tipos de evaluación.');
            }
        })
        .catch(error => console.error('Error al cargar los tipos de evaluación:', error));
}

// vamos a guardar el aporte 
function guardarDatosAporteUnidadAdmin() {


    
    // Captura el formulario y convierte sus datos en un objeto FormData
    const formulario = new FormData(document.getElementById('crearAporteAdminForm'));
    const clase_id = formulario.get('cursoAsignaturaAdmin_id');
    const unidad_id = formulario.get('unidadAporteAdmin_id');
    // Extrae el valor de cursoAsignatura_id del FormData
    const matriculas = Array.from(document.querySelectorAll('tbody tr[data-matri-id]'))
    .map(row => row.getAttribute('data-matri-id'));


    // Convierte los datos del formulario a un objeto JSON
    const datosDeAporte = {
    csrfmiddlewaretoken: formulario.get('csrfmiddlewaretoken'),
    nombreAporte: formulario.get('nombreAporteAdmin'),
    cursoAsignatura_id: formulario.get('cursoAsignaturaAdmin_id'),
    trimestreAporte_id: formulario.get('trimestreAporteAdmin_id'),
    fechaAporte: formulario.get('fechaAporteAdmin'),
    cboAporteTrimestral: formulario.get('cboAporteTrimestralAdmin'),
    unidad_id : formulario.get('unidadAporteAdmin_id'),
    matriculas: matriculas // Agrega aquí las matrículas
};
    // Realiza la solicitud fetch para enviar los datos al servidor
    fetch('../crearAporteAdmin', {
        method: 'POST',
        body:JSON.stringify(datosDeAporte),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
        .then(response => response.json())  // Convierte la respuesta a JSON
        .then(data => {
            if (data.estado) {
                console.log('Aporte creado exitosamente.');
                // Cierra el modal automáticamente
                
                const modalElement = document.getElementById('crearAporteModalAdmin');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();
                cargarReportesUnidad(unidad_id, clase_id);
                
                

            } else {
                console.log('Error al crear el aporte:', data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// ahora selecionamos un aporte Admin
function selecionarUnAporteUnidadAdmin(aporteId, trimestreId) {
    
    const contenedorTabla = document.getElementById('tbl-reportes-unidad').parentElement; // Asegúrate de que `tbl-aportes` es el ID correcto
    const posicionScroll = contenedorTabla.scrollLeft; // Captura la posición del scroll horizontal

    document.getElementById('posicionScroll').value = posicionScroll; // Guarda la posición en un campo oculto


    const url = `../selecionarUnAporteAdmin/${aporteId}/`;

    // Realizar la solicitud AJAX
    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error('No se pudo obtener la información del aporte.');
        }
        return response.json();
    })
    .then(data => {
        if (data.message === 'ok') {
            document.querySelector("#nombreAporteActualizarAdmin").value = data.aporte.nombreAporteAdmin;
            document.querySelector("#fechaActualizarAdmin").value = data.aporte.fechaAdmin;

            listarTiposDeEvaluacionEditar(trimestreId, data.aporte.tipoEvaluacionAdmin);
            const modalEditar = document.getElementById('modalAporteAdmin');
            modalEditar.dataset.aporteId = aporteId;

            const modal = new bootstrap.Modal(document.getElementById('modalAporteAdmin'));
            modal.show();
        } else {
            alert("No se pudo obtener la información del aporte.");
        }
    })
    .catch(error => console.error('Error:', error));
}


// reutilizamos de clase trabajo
function listarTiposDeEvaluacionEditar(trimestreId, selectedTipoEvaluacionId) {
    
    const url = `../listartiposPorTrimestre/${trimestreId}/`;

    // Realizar la solicitud AJAX para obtener los tipos de evaluación
    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error('No se pudieron obtener los tipos de evaluación.');
        }
        return response.json();
    })
    .then(data => {
        if (data.message === 'ok') {
            const selectTipoEvaluacion = document.querySelector("#cboTipoActualizarAdmin");
            selectTipoEvaluacion.innerHTML = "";

            data.tipoEvaluacion.forEach(tipo => {
                const option = document.createElement("option");
                option.value = tipo.id;
                option.textContent = tipo.nombre;
                if (tipo.id === selectedTipoEvaluacionId) {
                    option.selected = true;
                }
                selectTipoEvaluacion.appendChild(option);
            });
        } else {
            console.error("No hay datos disponibles para los tipos de evaluación.");
        }
    })
    .catch(error => console.error('Error:', error));
}

// aqui vamos a guardar lo editado 
function guardarAporteUnidadEditadoAdmin() {
    
    const modal = document.getElementById('modalAporteAdmin');
    const aporteId = modal.dataset.aporteId;
    
    if (!aporteId) {
        console.error('ID del aporte no definido');
        return;
    }

    const form = document.getElementById('formularioEditarAporteAdmin');
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    // Obtener los valores del formulario
    const unidad_id = document.getElementById('aporteEditarUnidadId').value;
    const clase_id = document.getElementById('aporteEditarClaseId').value;

    
    const url = `../editarAporteAdmin/${aporteId}/`;

    const data = {
        nombreAporteActualizarAdmin: document.querySelector("#nombreAporteActualizarAdmin").value,
        fechaActualizarAdmin: document.querySelector("#fechaActualizarAdmin").value,
        cboTipoActualizarAdmin: document.querySelector("#cboTipoActualizarAdmin").value,
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Asegúrate de incluir el CSRF token
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            alert(data.message);
            $('#modalAporteAdmin').modal('hide'); // Cierra el modal
            // Actualiza la tabla o la vista según sea necesario
            const posicionScroll = document.getElementById('posicionScroll').value;
            cargarReportesUnidad(unidad_id,clase_id,posicionScroll);
        } else if (data.error) {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error('Error:', error));
}

// ahora vamos a eliminar 
function eliminarAporteAdmin(button) {
    const aporte_id = button.dataset.aporteId;
    const unidad_id = button.dataset.unidadEliminarId;
    const clase_id = button.dataset.claseEliminarId;
    if (!aporte_id) {
        console.error('ID del aporte no definido');
        return;
    }

    if (confirm('¿Estás seguro de que deseas eliminar este aporte?')) {
        fetch(`../eliminarAporteAdmin/${aporte_id}/`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value // Token CSRF
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('El aporte no existe o ya ha sido eliminado.');
            }
            return response.json();
        })
        .then(data => {
            if (data.estado) {
                alert(data.mensaje);
                cargarReportesUnidad(unidad_id, clase_id);
                
            } else {
                alert(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message); // Muestra el error al usuario
            cargarReportesUnidad(unidad_id, clase_id);
        });
    }
}


// aqui vamos a  guardar una calificacion 
function validarNota(nota) {
    nota = nota.replace(',', '.');
    let valorNumerico = parseFloat(nota);
    return !isNaN(valorNumerico) && valorNumerico >= 0 && valorNumerico <= 10;  // Rango de notas entre 0 y 10
}

// ahora vamos a guardar una calificacion
function guardarCalificaciones(aporteId, trimestreId, claseId) {

    

    // Seleccionamos todos los inputs relacionados con ese aporteId
    const inputFields = document.querySelectorAll(`input[id$='-${aporteId}']`);
    
    const calificaciones = [];
    let errores = false; // Para rastrear si hubo errores

    // Recorremos los campos y obtenemos los valores de calificación
    inputFields.forEach(input => {

        const matriculaId = input.dataset.matriculaId;
        const aporteId = input.dataset.aporteId;
        let nota = input.value.trim(); // Eliminar espacios innecesarios
        
        if (!validarNota(nota)) {
            input.classList.add('input-error');  // Añadir clase para borde rojo
            errores = true;  // Marcar error
        } else {
            input.classList.remove('input-error');
            calificaciones.push({
                matricula_id: matriculaId,
                aporte_id: aporteId,
                nota: parseFloat(nota)
            });
        }
    });
    // Si hay errores, detener la ejecución y mostrar la alerta después de un pequeño retraso
    if (errores) {
        // Esperar un breve momento antes de mostrar la alerta para que los estilos se apliquen
        setTimeout(() => {
            alert("Por favor, corrige las notas antes de continuar.");
        }, 100); // 100ms debería ser suficiente para que los estilos se apliquen
        return;  
    }

    // Enviar los datos al servidor (Fetch API)
    fetch(`../calificacionAporteTrimestralAdmin/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Para Djangos
        },
        body: JSON.stringify({
            calificaciones: calificaciones,
            trimestre_id: trimestreId, // Incluye el trimestreId
            clase_id: claseId // Incluye el claseId
        })
    })
    .then(response => response.json())
    .then(data => {
        
        if (data.success) {
            
            // Deshabilitamos los campos nuevamente
            inputFields.forEach(input => input.disabled = true);
            
            cargarCalificacionesAdmin();

        } else {
            alert('Error al guardar las calificaciones');
        }
    })
    .catch(error => console.error('Error:', error));
}


function cargarCalificacionesAdmin() {
    // Selecciona todos los inputs de calificaciones
    const inputsCalificaciones = document.querySelectorAll('.nota-input');

    inputsCalificaciones.forEach(function(input) {
        const matricula_id = input.getAttribute('data-matricula-id');
        const aporte_id = input.getAttribute('data-aporte-id');
        const calificacion_id = input.getAttribute('data-calificacion-id');
        
        // Verifica si calificacionId es válido antes de hacer la solicitud
        if (calificacion_id) {
            // Construye la URL para obtener las calificaciones
            const url = `../obtenerCalificacionesUnidadAdmin/${matricula_id}/${aporte_id}/${calificacion_id}/`;
            
            // Realiza la petición para obtener las calificaciones
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Si la petición fue exitosa, rellena el input con la nota
                        if (data.data.calificaciones.length > 0) {
                            input.value = data.data.calificaciones[0].nota;
                        }
                    } else {
                        console.error('Error al obtener las calificaciones:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error en la petición:', error);
                });
        }
    });
}


document.addEventListener('DOMContentLoaded', function () {
    const inputsNotas = document.querySelectorAll('input.nota');
    inputsNotas.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(',', '.');
        });
    });


    // Delegar eventos en el contenedor que siempre está presente en el DOM
    document.body.addEventListener('click', function (event) {
        if (event.target.closest('.btn-calificar')) {
            const button = event.target.closest('.btn-calificar');
            const aporteId = button.getAttribute('data-aporte-id');
            const trimestreId = button.getAttribute('data-trimestre-id'); // Obtener el trimestreId
            const claseId = button.getAttribute('data-clase-id'); // Obtener el claseId
            //const aporteId = button.getAttribute('data-aporte-id');
            // Seleccionar inputs basados en el `aporteId`
            const inputFields = document.querySelectorAll(`input[id$='-${aporteId}']`);
            
            

            // Si los inputs ya están habilitados, se guardarán las calificaciones
            if (!inputFields[0].disabled) {
                guardarCalificaciones( aporteId, trimestreId, claseId);
                cargarCalificacionesAdmin;
                //button.innerHTML = '<i class="fas fa-file"></i>'; // Icono de archivo
                button.classList.add('btn-guardar');
                inputFields.forEach(input => {
                    input.disabled = false; // Deshabilitar inputs después de guardar
                    input.classList.add('highlight-input'); // Quitar clase de borde fluorescente
                });
                
            }else{
                inputFields.forEach(input => {
                    // Mostrar el valor actual o 0 si está vacío
                    if (input.value === '' || input.value === '0') {
                        input.value = ''; // Mantener vacío si ya está vacío o era 0
                    }
                    input.disabled = false;
                    input.classList.add('highlight-input');

                    agregarEventoPaste(input);
                });
            
                button.innerHTML = '<i class="fas fa-save"></i>';
                button.classList.add('btn-guardar');
                
            }
  
        }
    });
});

// funncion para lanzar el modal con la observacion
function mostrarObservacionAdmin(element) {

    const calificacionId = element.getAttribute('data-observacion-id');
    var observacionTexto = document.getElementById('observacionesTexto');
    var observacionIdInput = document.getElementById('observacionEditar');

    // Establecer el ID de calificación en el campo oculto del modal
    observacionIdInput.value = calificacionId;
    
    // Hacer una solicitud fetch para obtener la observación
    fetch(`../obtenerObservacionUnidadAdmin/${calificacionId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.observacion) {
                observacionTexto.textContent = data.observacion;
            } else {
                observacionTexto.textContent = 'No hay observaciones';
            }
        })
        .catch(error => {
            console.error('Error al obtener la observación:', error);
            observacionTexto.textContent = 'Error al obtener la observación';
        });
}


function guardarObservacionAdmin() {
    var calificacionId = document.getElementById('observacionEditar').value;
    var observacion = document.getElementById('observacionesTexto').value;

    if (!observacion.trim()) {
        alert("La observación no puede estar vacía.");
        return;
    }

    var formData = new FormData();
    formData.append('observacion', observacion);

    fetch(`/editarObservacionUnidadAdmin/${calificacionId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("Observación guardada correctamente.");
            var modal = document.getElementById('observacionModal');
            var modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error al guardar la observación:', error);
        alert("Ocurrió un error al intentar guardar la observación.");
    });
}


// FUNCION PARA COPIAR Y PEGAR NOTAS 
// Función para agregar el evento "paste" en los inputs habilitados
function agregarEventoPaste(input) {
    input.addEventListener('paste', function(event) {
        event.preventDefault();  // Previene el comportamiento predeterminado de pegar
        const pasteData = event.clipboardData.getData('text'); // Obtiene los datos pegados

        // Divide las notas pegadas (cada nota debe estar separada por tabulaciones o saltos de línea)
        const notas = pasteData.split(/\t|\n/);

        // Encuentra todos los inputs que están habilitados
        const inputsHabilitados = document.querySelectorAll('.highlight-input');

        // Asigna cada nota a los inputs correspondientes
        notas.forEach((nota, index) => {
            if (inputsHabilitados[index]) {
                inputsHabilitados[index].value = nota.trim();  // Asigna la nota y elimina espacios innecesarios
            }
        });
    });
}

// setear las fechas actuales 
function setFechaActual(inputId) {
    const input = document.getElementById(inputId);
    const hoy = new Date();
    
    // Formato de fecha YYYY-MM-DD requerido por los inputs de tipo date
    const dia = ("0" + hoy.getDate()).slice(-2);
    const mes = ("0" + (hoy.getMonth() + 1)).slice(-2); // Los meses empiezan en 0
    const fechaActual = hoy.getFullYear() + '-' + mes + '-' + dia;
    
    // Establecer el valor del input
    input.value = fechaActual;
}


// aqui van para los trimestre


// Delegar eventos en el contenedor que siempre está presente en el DOM
document.body.addEventListener('click', function (event) {
    // Si se hace clic en el botón de calificar
    if (event.target.closest('.btn-calificar-examen')) { // Cambié a .btn-calificar-examen
        const button = event.target.closest('.btn-calificar-examen'); // Cambié a .btn-calificar-examen
        const examenId = button.getAttribute('data-examen-id');
        const claseId = button.getAttribute('data-clase-id');
        // Obtener todos los inputs relacionados con el examen
        const inputFields = document.querySelectorAll(`input[data-examen-id='${examenId}']`);
        console.log('inputFields encontrados:', inputFields); // Añade esta línea para depuración

        // Verificar si hay al menos un input
        if (inputFields.length === 0) {
            console.error(`No se encontraron inputs para examenId: ${examenId}`);
            return; // Salir de la función si no se encontraron inputs
        }

        // Verificar si los inputs ya están habilitados
        if (!inputFields[0].disabled) {
            // Lógica para guardar calificaciones
            guardarCalificacionesExamenAdmin(examenId,claseId);

            // Deshabilitar inputs después de guardar
            inputFields.forEach(input => {
                input.disabled = true;
                input.classList.remove('highlight-input'); // Quitar clase de borde fluorescente
            });
            button.innerHTML = '<i class="fas fa-file"></i>'; // Cambiar icono a archivo
            button.classList.remove('btn-guardar');

        } else {
            // Habilitar los inputs para permitir la edición
            inputFields.forEach(input => {
                input.disabled = false; // Habilitar el input
                input.classList.add('highlight-input'); // Añadir clase para destacar el input
            });
            button.innerHTML = '<i class="fas fa-save"></i>'; // Cambiar icono a guardar
            button.classList.add('btn-guardar');
        }
    }
});

function guardarCalificacionesExamenAdmin(examenId, claseId) {
    const inputFields = document.querySelectorAll('.nota-input-examen'); // Captura todos los inputs
    const calificaciones = [];
    let errores = false; 
    // Guardar la posición de desplazamiento actual
    const scrollPosition = window.scrollY;

    // Iterar sobre cada campo de entrada
    inputFields.forEach(input => {
        const matriculaId = input.dataset.matriculaId; // Obtener ID de matrícula
        const examenId = input.dataset.examenId; // Obtener ID de examen
        let nota = input.value.trim(); // Obtener valor de la nota y eliminar espacios

        // Validación de la nota
        if (!validarNota(nota)) {
            input.classList.add('input-error'); // Añadir clase para borde rojo
            errores = true; // Marcar error
        } else {
            input.classList.remove('input-error');
            calificaciones.push({
                matricula_id: matriculaId,
                examen_id: examenId,
                clase_id:claseId,
                nota: parseFloat(nota) // Mantener como cadena con dos decimales
            });
        }
    });

    // Si hay errores, detener la ejecución y mostrar la alerta
    if (errores) {
        setTimeout(() => {
            alert("Por favor, corrige las notas antes de continuar.");
        }, 100); // Esperar 100ms para aplicar estilos
        return;
    }

    // Enviar las calificaciones al servidor
    fetch('../calificacionExamenTrimestralAdmin/', { // Reemplaza con tu URL de API
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ calificaciones: calificaciones }), // Convertir a JSON
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); }); // Manejar el error
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("Calificaciones guardadas exitosamente.");
            // Recargar las calificaciones y promedios
            cargarCalificacionesExamenAdmin(claseId);
            cargarPromediosTrimestralesAdmin(claseId);

            // Mantener la posición del scroll
            window.scrollTo(0, scrollPosition);
        } else {
            alert("Error: " + data.error); // Mostrar error si ocurre
        }
    })
    .catch(error => {
        console.error('Error:', error); // Manejar errores en la solicitud
        alert("Ocurrió un error al enviar las calificaciones.");
    });
}

function cargarCalificacionesExamenAdmin(clase_Id) {
    // Selecciona todos los inputs de calificaciones de exámenes
    const inputsCalificaciones = document.querySelectorAll('.nota-input-examen');

    inputsCalificaciones.forEach(function(input) {
        const matriculaId = input.getAttribute('data-matricula-id');
        const examenId = input.getAttribute('data-examen-id');

        // Construye la URL para obtener las calificaciones
        const url = `/obtenerCalificacionExamenTrimestralAdmin/${matriculaId}/${examenId}/${clase_Id}`;
        
        // Realiza la petición para obtener las calificaciones
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Si la petición fue exitosa, rellena el input con la nota
                    input.value = data.data.nota;

                    // Busca el ícono de observación relacionado con este input
                    const observacionIcon = input.closest('.observaciones').querySelector('.fas.fa-eye');

                    if (observacionIcon) {
                        // Asigna el ID de la calificación al atributo data-observacion-id
                        observacionIcon.setAttribute('data-observacion-id', data.data.id || '');
                    }
                } else {
                    console.error('Error al obtener la calificación:', data.error);
                }
            })
            .catch(error => {
                console.error('Error en la petición:', error);
            });
    });
}



function cargarPromediosTrimestralesAdmin(clase_Id) {
    const celdasPromedio = document.querySelectorAll('.nota-input-promedio');

    celdasPromedio.forEach(function (celda) {
        const matriculaId = celda.getAttribute('data-matricula-id');
        const trimestreId = celda.getAttribute('data-trimestre-id');

        celda.textContent = 'Cargando...'; // Mensaje temporal

        const url = `/obtenerPromedioTrimestralAdmin/${matriculaId}/${trimestreId}/${clase_Id}`;

        fetch(url)
            .then((response) => {
                console.log(`Respuesta para ${url}:`, response);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data.success) {
                    celda.textContent = data.data.nota;
                } else {
                    console.error(`Error en datos: ${data.error}`);
                    celda.textContent = 'Error';
                }
            })
            .catch((error) => {
                console.error(`Error en la petición para ${url}:`, error);
                celda.textContent = 'Error';
            });
    });
}

function mostrarObservacionExamenAdmin(element) {
    const calificacionId = element.getAttribute('data-observacion-id');
    var observacionTexto = document.getElementById('observacionesTextoExamenAdmin');
    var observacionIdInput = document.getElementById('observacionEditarExamenAdmin');

    // Establecer el ID de calificación en el campo oculto del modal
    observacionIdInput.value = calificacionId;
    
    // Hacer una solicitud fetch para obtener la observación
    fetch(`../obtenerObservacionExamenAdmin/${calificacionId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.observacion) {
                observacionTexto.textContent = data.observacion;
            } else {
                observacionTexto.textContent = 'No hay observaciones';
            }
        })
        .catch(error => {
            console.error('Registra primero las notas del examen :', error);
            observacionTexto.textContent = 'Registra primero las notas del examen';
        });
}

function guardarObservacionExamenAdmin() {
    var calificacionId = document.getElementById('observacionEditarExamenAdmin').value;
    var observacion = document.getElementById('observacionesTextoExamenAdmin').value;
    console.log(calificacionId);
    if (!observacion.trim()) {
        alert("La observación no puede estar vacía.");
        return;
    }

    var formData = new FormData();
    formData.append('observacion', observacion);
    
    fetch(`/editarObservacionExamenAdmin/${calificacionId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("Observación guardada correctamente.");
            var modal = document.getElementById('observacionModalExamenAdmin');
            var modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error al guardar la observación:', error);
        alert("Ocurrió un error al intentar guardar la observación.");
    });
}

function obtenerPromediosGeneralesTrimestralesAdmin() {
    const celdasPromediosTrimestralesGenerales = document.querySelectorAll('.nota-input-promedio-general-trimestral');
    const periodo_id = document.getElementById("periodoGeneralTrimestral").value;
    celdasPromediosTrimestralesGenerales.forEach(celda => {
        const clase_id = celda.getAttribute('data-clase-id');
        const matriculaId = celda.getAttribute('data-matricula-id');
        const trimestreId = celda.getAttribute('data-trimestre-id');
        
        const span = celda.querySelector(".subpromedio-valor");

        fetch(`../obtenerPromediosGeneralesTrimestralesAdmin/${matriculaId}/${trimestreId}/${clase_id}/${periodo_id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Si data.nota existe, se asigna; si no, muestra 'N/A'
                span.textContent = data.data.nota || 'N/A';  // Aquí accedemos a data.data.nota
            } else {
                console.error('Error al obtener el subpromedio:', data.error);
                span.textContent = 'N/A';
            }
        })
        .catch(error => {
            console.error('Error en la petición:', error);
            span.textContent = 'Error';
        });
        });
}

function obtenerPromediosGeneralesAdmin(clase_id, periodo_id) {
    // Seleccionar todas las celdas donde se va a mostrar el promedio general
    const celdasPromedio = document.querySelectorAll('.promedio-general');
    
    // Para cada celda, obtener los IDs y hacer la solicitud para obtener el promedio
    celdasPromedio.forEach(celda => {
        const matricula_id = celda.dataset.matriculaId;
      
        // Realizar la solicitud al endpoint de Django
        fetch(`../obtenerPromediosGeneralesAdmin/${matricula_id}/${clase_id}/${periodo_id}/`)
            .then(response => response.json())
            .then(data => {
                // Si la respuesta es exitosa, actualizar el valor de la celda
                if (data.success) {
                    const nota = data.data.nota;
                    const observacion = data.data.observacion;
                    
                    // Limpiar la celda y alinear el contenido a la izquierda
                    celda.classList.add('text-start', 'fs-10');
                    celda.innerHTML = ''; // Limpiar el contenido de la celda

                    // Crear un elemento para la nota
                    const notaSpan = document.createElement('span');
                    notaSpan.textContent = `${nota} `; // Mostrar la nota
                    notaSpan.style.color = 'black'; // Color negro para la nota
                    notaSpan.style.fontWeight = "bold"; // Negrita
                    celda.appendChild(notaSpan);

                    // Crear un elemento para la observación
                    const observacionSpan = document.createElement('span');
                    observacionSpan.textContent = observacion; // Mostrar la observación

                    // Si es "Aprobado", aplicar estilo verde fosforescente
                    if (observacion && observacion.toLowerCase() === "aprobado") {
                        observacionSpan.style.color = "lime"; // Verde fosforescente
                        observacionSpan.style.fontWeight = "bold"; // Negrita
                    } else {
                        observacionSpan.style.color = "inherit";
                        observacionSpan.style.color = "red"; // Verde fosforescente
                        observacionSpan.style.fontWeight = "bold"; // Negrita // Restablecer el color para otras observaciones
                    }

                    // Agregar la observación a la celda
                    celda.appendChild(observacionSpan);
                } else {
                    celda.textContent = "Error";
                }
            })
            .catch(error => {
                console.error('Error:', error);
                celda.textContent = "Error";
            });
    });
}

async function calcularPromedioClaseGeneralAdmin(clase_id) {
    try {
        const response = await fetch(`/calcularPromedioClaseGeneralAdmin/${clase_id}/`);
        if (!response.ok) {
            throw new Error(`Error al obtener el promedio: ${response.status}`);
        }

        const data = await response.json();

        const promedioElemento = document.getElementById('PromedioClaseGeneral');
        if (data.promedio !== undefined) {
            promedioElemento.textContent = data.promedio;
        } else {
            promedioElemento.textContent = "No disponible";
        }
    } catch (error) {
        console.error('Error:', error);
        const promedioElemento = document.getElementById('PromedioClaseGeneral');
        promedioElemento.textContent = "Error al cargar";
    }
}

// para supletorio


function manejarSupletorioAdmin(boton) {
    // Leer el estado actual desde el botón
    const estadoActual = boton.dataset.estado === "activo";

    // Obtener todos los inputs relevantes del documento
    const inputs = document.querySelectorAll('input[data-matricula-examen][data-clase-id]');

    // Seleccionar el botón de guardar asociado
    const botonGuardar = boton.parentElement.querySelector('button.btn-success');

    if (estadoActual) {
        // Si está activo, deshabilitar todos los inputs y restablecer el estado inicial
        inputs.forEach(input => {
            input.disabled = true; // Restablecer a deshabilitado
        });

        // Ocultar el botón de guardar
        if (botonGuardar) {
            botonGuardar.style.display = 'none';
        }

        // Cambiar el botón presionado a su estado normal
        boton.classList.remove('btn-danger');
        boton.classList.add('btn-primary');
        boton.innerHTML = '<i class="fas fa-file"></i>'; // Cambiar icono a archivo

        boton.dataset.estado = "inactivo"; // Cambiar el estado del botón
    } else {
        // Si no está activo, habilitar según las condiciones
        inputs.forEach(input => {
            const matriculaId = input.dataset.matriculaExamen;
            const claseId = input.dataset.claseId;
            

            // Llamar a la vista con Fetch
            fetch(`/obtenerMatriculasParaSupletorioAdmin/${claseId}/${matriculaId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const registros = data.data;

                        let alMenosUnInputHabilitado = false; // Para verificar si habilitamos al menos un input

                        registros.forEach(registro => {
                            const input = document.querySelector(`input[data-matricula-examen="${registro.matricula_id}"][data-clase-id="${registro.curso_asignatura_id}"]`);
                            if (input) {
                                // Habilitar si el promedio es menor a 7
                                const promedio = parseFloat(registro.nota);
                                input.disabled = promedio >= 7; // Deshabilitar si la nota es mayor o igual a 7
                                if (promedio < 7) {
                                    alMenosUnInputHabilitado = true;
                                    input.addEventListener('paste',  manejarPegadoSupletorioAdmin);
                                }  
                                
                            }
                        });

                        // Mostrar el botón de guardar si al menos un input está habilitado
                        if (botonGuardar) {
                            console.log("Mostrar botón guardar: ", alMenosUnInputHabilitado);
                            botonGuardar.style.display = alMenosUnInputHabilitado ? 'inline-block' : 'none';
                        }
                    } else {
                        console.error(data.error || 'Error desconocido.');
                    }
                })
                .catch(error => console.error('Error en la solicitud:', error));
        });

        // Cambiar el botón presionado a su estado activo
        boton.classList.remove('btn-primary');
        boton.classList.add('btn-danger');
        boton.innerHTML = '<i class="fas fa-times"></i>'; // Cambiar icono a una "X"
        
        boton.dataset.estado = "activo"; // Cambiar el estado del botón
    }
}


function manejarPegadoSupletorioAdmin(event) {
    event.preventDefault(); // Previene el comportamiento predeterminado de pegar
    const pasteData = event.clipboardData.getData('text'); // Obtiene los datos pegados

    // Divide las notas pegadas (cada nota debe estar separada por tabulaciones o saltos de línea)
    const notas = pasteData.split(/\t|\n/);

    // Encuentra todos los inputs habilitados
    const inputsHabilitados = document.querySelectorAll('input[data-matricula-examen]:not([disabled])');

    // Asigna cada nota a los inputs correspondientes
    notas.forEach((nota, index) => {
        if (inputsHabilitados[index]) {
            inputsHabilitados[index].value = nota.trim(); // Asigna la nota y elimina espacios innecesarios
        }
    });
}


function guardarCalificacionExamenSupletorioAdmin(button) {
    // Obtener el examen_id desde el botón presionado
    const examenId = button.getAttribute('data-examen-id');
    
    // Buscar todos los inputs correspondientes al examen donde se debe guardar la calificación
    const inputs = document.querySelectorAll(`input[data-examen-id='${examenId}']`);

     // Agregar el evento "paste" a los inputs habilitados
    
    
    let calificacionesValidas = true;  // Variable para rastrear si todas las calificaciones son válidas
    let errorEnInput = "";  // Mensaje de error para inputs específicos

    // Referencia al botón "fas fa-file" relacionado que en este caso estarra como btn danger
    const botonEstado = button.parentElement.querySelector('button.btn-danger');

    // Iterar sobre todos los inputs habilitados
    const solicitudes = Array.from(inputs).map(input => {
        if (!input.disabled) {
            const matriculaId = input.getAttribute('data-matricula-examen');
            const claseId = input.getAttribute('data-clase-id');
            const nota = input.value.trim();
            
            // Validar que la nota no esté vacía y sea un número válido entre 0 y 10
            
            if (!validarNota(nota)) {
                // Resaltar el input en rojo y mostrar mensaje de error
                input.style.borderColor = "red";
                errorEnInput = `El input con matrícula ${matriculaId} y clase ${claseId} tiene una calificación inválida.`;
                calificacionesValidas = false;
                return Promise.reject(errorEnInput);
            } else {
                // Restaurar el estilo del input si es válido
                input.style.borderColor = "";
            }

            // Crear el FormData para enviar los datos
            const formData = new FormData();
            formData.append('matricula_id', matriculaId);
            formData.append('examen_id', examenId);
            formData.append('curso_asignatura_id', claseId);
            formData.append('nota', parseFloat(nota.replace(',', '.')));
            formData.append('observacion', "NINGUNA");

            // Enviar la solicitud POST
            return fetch('/guardarExamenSupletorioAdmin/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(`Error al guardar la calificación para matrícula ${matriculaId} y clase ${claseId}.`);
                }
            });
        }
    });

    // Ejecutar todas las solicitudes si las calificaciones son válidas
    if (calificacionesValidas) {
        Promise.allSettled(solicitudes)
            .then(results => {
                results.forEach((result, index) => {
                    if (result.status === "rejected") {
                        console.error(result.reason);
                    }
                });
                alert("Calificaciones guardadas correctamente.");
				 // Deshabilitar inputs
                inputs.forEach(input => input.disabled = true);

                // Ocultar el botón de guardar
                button.style.display = 'none';

                // Restaurar el botón "fas fa-file" al estado inactivo
                if (botonEstado) {
                    botonEstado.classList.remove('btn-danger');
                    botonEstado.classList.add('btn-primary');
                    botonEstado.innerHTML = '<i class="fas fa-file"></i>'; // Cambiar icono
                    botonEstado.dataset.estado = "inactivo"; // Cambiar estado
                }
            })
            .catch(error => {
                console.error("Error al guardar algunas calificaciones:", error);
            });
    } else {
        alert("Por favor, corrige los errores en las calificaciones antes de guardar.");
    }
}


function cargarCalificacionesSupletorioAdmin() {
    // Recorrer todos los inputs de calificación en el DOM
    const inputs = document.querySelectorAll('input[data-examen-id][data-matricula-examen][data-clase-id]');

    // Para cada input, obtener el examen_id, matricula_id y clase_id
    inputs.forEach(input => {
        const examenId = input.getAttribute('data-examen-id');
        const matriculaId = input.getAttribute('data-matricula-examen');
        const claseId = input.getAttribute('data-clase-id');

        // Realizar la solicitud fetch para obtener la calificación de este examen
        fetch(`/obtenerCalificacionSupletorioAdmin/${examenId}/${matriculaId}/${claseId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.calificaciones && data.calificaciones.length > 0) {
                    // Buscar la calificación correspondiente para este examen
                    const calificacion = data.calificaciones.find(cal => cal.matricula_id == matriculaId && cal.clase_id == claseId);

                    // Si se encuentra una calificación válida, asignarla al input
                    if (calificacion) {
                        input.value = calificacion.nota;  // Asignar la nota al input
                        
                    }else{
                        input.value = '';
                    }
                }
            })
            .catch(error => {
                console.error('Error al cargar las calificaciones:', error);
                alert('Hubo un error al cargar las calificaciones.');
            });
    });
}