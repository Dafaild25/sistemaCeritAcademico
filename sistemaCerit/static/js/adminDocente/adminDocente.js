

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


// aqui mandamos a que la funcion pueda listar los periodos y que este en un select 
const listarPeriodosDocente = async()=>{
    try {
        const  response = await fetch("../listarPeriodosDocente")
        const data = await response.json();
        if(data.message === "okey"){
            let opciones = ``
            data.periodos.forEach((periodos)=>{
                opciones+=`<option value='${periodos.id}'>${periodos.nombre}</option>`;
            })
            cboPeriodoClase.innerHTML=opciones  ;
            listarCursos(data.periodos[0].id)
            
            
        
        }

    } catch (error) {
        console.log(error);
        
        
    }
}

// aqui vamos a listar los cursos y llamaremos al template que se inserte en un contenedor 
function listarCursos(periodo_id) {
    // Limpia el contenedor antes de cargar los nuevos datos
    document.getElementById('container_cursosAsignaturas').innerHTML = '';

    // Realiza la petición fetch a la URL creada
    fetch(`../listarCursosDocente/${periodo_id}/`)
        .then(response => response.text())
        .then(html => {
            // Inserta el HTML recibido en el contenedor
            document.getElementById('container_cursosAsignaturas').innerHTML = html;
            // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
        });
}


const cargaInicial=async()=>{
    await listarPeriodosDocente();
    cboPeriodoClase.addEventListener("change",(event)=>{
        listarCursos(event.target.value)
        
    })

    
}

//lo que debe hacer si essta cargada la pagina 
window.addEventListener("load",async()=>{
    await cargaInicial()
    
    
})

// desde aqui va la segunda opcion

function vistaTrabajoClase(clase_id){
    // Asegúrate de que periodoTrabajo está correctamente definido
    const periodoTrabajo = document.getElementById('periodoTrabajo'); // Reemplaza 'id-del-periodo-trabajo' con el ID correcto
    
    if (periodoTrabajo) { // Verifica que periodoTrabajo no sea null o undefined
        const periodo_id = periodoTrabajo.getAttribute('data-periodoTrabajo');
        
        document.getElementById('contenedor-trabajo-clase').innerHTML = '';
        
        // Realiza la petición fetch a la URL creada
        fetch(`../vistaTrabajoClase/${clase_id}/`)
            .then(response => response.text())
            .then(html => {
                // Inserta el HTML recibido en el contenedor
                document.getElementById('contenedor-trabajo-clase').innerHTML = html;
                // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
                
                cargarTrimestresTrabajo(periodo_id);
                // Configurar el observer para detectar cuando el canvas esté en el DOM

                observeCanvasAndLoadChart();
                

                dashboardTiposEvaluacion();

            })
            .catch(error => {
                console.error('Error al cargar el listado de aportes:', error);
            });
    } else {
        console.error('Elemento periodoTrabajo no encontrado');
    }
}


// Función para observar cuándo el canvas se añade al DOM
function dashboardTiposEvaluacion() {
    const observer = new MutationObserver((mutationsList, observer) => {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList') {
                const canvas = document.getElementById('evaluacionChart');
                if (canvas) {
                    console.log("Canvas encontrado, cargando datos del gráfico.");
                    
                    // Obtén el ID de la asignatura desde el input
                    const cursoAsignaturaId = document.getElementById('cursoAsignaturaId').value;
                    const trimestre = document.getElementById('trimestre').value;
                    
                    // Asegúrate de que el ID es válido
                    if (cursoAsignaturaId) {
                        cargarDatosGraficosTiposEvaluacion(cursoAsignaturaId,trimestre);
                    } else {
                        console.error("Error: No se encontró el ID de la asignatura.");
                    }
                    
                    observer.disconnect(); // Detener el observador después de encontrar el canvas
                    return;
                }
            }
        }
    });

    // Iniciar la observación del contenedor donde se carga el contenido dinámico
    const targetNode = document.getElementById('contenedor-trabajo-clase');
    observer.observe(targetNode, { childList: true, subtree: true });
}

// Modificar la función cargarDatosGraficosTiposEvaluacion para aceptar el ID de la asignatura
function cargarDatosGraficosTiposEvaluacion(cursoAsignaturaId,trimestre) {
    const ctx = document.getElementById('evaluacionChart');
    if (!ctx) {
        console.error('Error: El elemento canvas no se encontró');
        return;
    }

    const context = ctx.getContext('2d');

    // Modificar la URL para incluir el ID de la asignatura
    fetch(`../obtener_tipos_evaluacion/${cursoAsignaturaId}/${trimestre}/`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos para el gráfico:", data);
            const maxDataValue = Math.max(...data.data) || 0; // Valor máximo de los datos o 0 si no hay datos
            const maxYAxisValue = Math.ceil(maxDataValue / 5) * 5; // Redondear hacia arriba al siguiente múltiplo de 5

            // Limpiar el canvas antes de dibujar
            context.clearRect(0, 0, ctx.width, ctx.height);

            // Crear el gráfico con los datos recibidos
            const chart = new Chart(context, {
                type: 'bar',
                data: {
                    labels: data.labels || [], // Etiquetas de los tipos de evaluación
                    datasets: [{
                        label: 'Número de Aportes',
                        data: data.aportes_count || [], // Datos de aportes
                        backgroundColor: data.colors || [],  // Colores extraídos de la respuesta
                        borderColor: data.colors || [],      // Usar el mismo color para el borde
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true, // Comenzar desde cero
                            max: maxYAxisValue, // Establecer el valor máximo del eje Y
                        }
                    }
                },
            });
        })
        .catch(error => {
            console.error('Error al cargar los datos del gráfico:', error);
        });
}





function cargarTrimestresTrabajo(periodo_id) {
    if (!periodo_id) {
        console.error("El ID del periodo no es válido.");
        return;
    }

    fetch(`../listarTrimestresTipo/${periodo_id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.message === "ok") {
                const select = document.getElementById('cboTrimestreTrabajo');
                select.innerHTML = '<option value="">Selecciona una opción</option>';

                // Agregar opción "Calificación General"
                const calificacionGeneralOption = document.createElement('option');
                calificacionGeneralOption.value = `periodo_${data.periodo_id}`;
                calificacionGeneralOption.textContent = "REPORTE GENERAL";
                select.appendChild(calificacionGeneralOption);

                // Cargar opciones de trimestres y unidades
                data.trimestres.forEach(trimestre => {
                    // Crear una opción para el trimestre
                    const trimestreOption = document.createElement('option');
                    trimestreOption.value = `trimestre_${trimestre.id}`;
                    trimestreOption.textContent = trimestre.nombre;
                    select.appendChild(trimestreOption);

                    // Agregar las unidades debajo del trimestre con sangría
                    trimestre.unidades.forEach(unidad => {
                        const unidadOption = document.createElement('option');
                        unidadOption.value = `unidad_${unidad.id}`;
                        unidadOption.textContent = '    ' + unidad.nombre; // Sangría para las unidades
                        unidadOption.style.fontSize = '0.9em';
                        select.appendChild(unidadOption);
                    });
                });

                // Manejador de eventos para el cambio en el select
                select.addEventListener('change', function () {
                    const selectedValue = this.value;
                    const selectedId = selectedValue.split('_')[1];
                    const claseId = document.getElementById('claseTrabajo').value;

                    if (selectedValue.startsWith('periodo_')) {
                        cargarVistaCalificacionGeneral(selectedId, claseId);
                    } else if (selectedValue.startsWith('trimestre_')) {
                        cargarVistaCalificacionTrimestre(selectedId, claseId);
                    } else if (selectedValue.startsWith('unidad_')) {
                        cargarVistaCalificacionUnidad(selectedId, claseId);
                    }
                });
            } else {
                console.error("Error en la respuesta del servidor:", data.message);
            }
        })
        .catch(error => console.error("Error al cargar los trimestres:", error));
}




// esta funcion no estamos  usando aun la de cargar detalles clases
function cargarDetallesClase(trimestreId, claseId,posicionScroll) {
    // Limpia el contenedor antes de cargar los nuevos datos
    //document.getElementById('contenedor-aportes-trimestrales').innerHTML = '';
    const contenedorAportes = document.getElementById('contenedor-aportes-trimestrales');
    // Realiza la petición fetch a la URL creada
    fetch(`../claseTrabajo/${trimestreId}/${claseId}/`)
   // Realiza la petición fetch a la URL creada
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        contenedorAportes.innerHTML = html;
        // Selecciona las celdas con la clase grade-column
            const tablaAportes = document.getElementById('tbl-aportes');
            
            // Verifica que la tabla exista
            if (!tablaAportes) {
                console.error('No se encontró el contenedor de la tabla.');
                return; // Salir de la función si el contenedor no existe
            }

        

            $('#tbl-aportes').DataTable({
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
            const contenedorTabla = tablaAportes.parentElement; // Asegúrate de tener acceso a la tabla

        
            // Verifica si posicionScroll está vacío y establece la posición adecuada
            const posicionHorizontal = posicionScroll ? parseFloat(posicionScroll) : contenedorTabla.scrollWidth;
        
            // Desplazamiento horizontal en el contenedor de la tabla
            contenedorTabla.scrollTo({
                left: posicionHorizontal,
                behavior: 'smooth' // Desplazamiento suave
            });
         }, 100); // Ajusta el tiempo según lo necesites 
            //cargarEquivalentes();
            //cargarSubpromedios();
        
    })
    .catch(error => {
        console.error('Error al cargar el listado de cursos:', error);
    });
}

function cargarVistaCalificacionUnidad(unidad_Id, clase_Id,posicionScroll) {
    const contenedorAportes = document.getElementById('contenedor-aportes-trimestrales');
    // Realiza la petición fetch a la URL creada
    fetch(`../vistaCalificacionUnidad/${unidad_Id}/${clase_Id}/`)
   // Realiza la petición fetch a la URL creada
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        contenedorAportes.innerHTML = html;
        // Selecciona las celdas con la clase grade-column
            const tablaAportes = document.getElementById('tbl-aportes-unidad');
            
            // Verifica que la tabla exista
            if (!tablaAportes) {
                console.error('No se encontró el contenedor de la tabla.');
                return; // Salir de la función si el contenedor no existe
            }

        
            $('#tbl-aportes-unidad').DataTable({
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


function cargarVistaCalificacionTrimestre(trimestre_Id, clase_Id) {
    // Limpia el contenedor antes de cargar los nuevos datos
    //document.getElementById('contenedor-aportes-trimestrales').innerHTML = '';
    const contenedorAportes = document.getElementById('contenedor-aportes-trimestrales');
    const currentScrollPosition = contenedorAportes.scrollTop;
    // Realiza la petición fetch a la URL creada
    fetch(`../vistaCalificacionTrimestre/${trimestre_Id}/${clase_Id}/`)
    
   // Realiza la petición fetch a la URL creada
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        contenedorAportes.innerHTML = html;
        contenedorAportes.scrollTop = currentScrollPosition;
        cargarSubpromediosUnidades(clase_Id);
        cargarCalificacionesExamen(clase_Id);
        cargarPromediosTrimestrales(clase_Id);
        $('#tbl-calificacion-trimestre').DataTable({
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


function cargarVistaCalificacionGeneral(periodo_id,clase_id,posicionScroll) {
    
    const contenedorAportes = document.getElementById('contenedor-aportes-trimestrales');
    
    fetch(`../vistaCalificacionGeneral/${periodo_id}/${clase_id}/`)
   
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        contenedorAportes.innerHTML = html;
        // Selecciona las celdas con la clase grade-column
            const tablaAportes = document.getElementById('tbl-calificacion-general');
            
            // Verifica que la tabla exista
            if (!tablaAportes) {
                console.error('No se encontró el contenedor de la tabla.');
                return; // Salir de la función si el contenedor no existe
            }
            
        
            $('#tbl-calificacion-general').DataTable({
                language: {
                    search: "Buscar:",
                },
                paging: false,          // Desactiva la paginación
                ordering: false,        // Desactiva las flechas de ordenamiento
                info: false,             // Desactiva el texto de información de la tabla
                scrollX: true,          // Activa el desplazamiento horizontal
                fixedHeader: true,      // Fija el encabezado y el buscador
            });
            obtenerPromediosGeneralesTrimestrales();
            obtenerPromediosGenerales(clase_id, periodo_id);
            calcularPromedioClaseGeneral(clase_id); // el promedio de la c
            cargarCalificacionesSupletorio(); //calificaciones de supletorio
             //solo los trimestres de cada clase  primer trimestre
            
         // Ajusta el tiempo según lo necesites 
            
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


function cargarSubpromediosUnidades(clase_Id) {
    // Seleccionar todas las celdas donde se va a mostrar la calificación
    const celdasCalificacion = document.querySelectorAll('.calificacion-unidad');
    
    // Para cada celda, obtener los IDs y hacer la solicitud para obtener la calificación
    celdasCalificacion.forEach(celda => {
        const matriculaId = celda.dataset.matriculaId;
        const unidadId = celda.dataset.unidadId;
        const trimestreId = celda.dataset.trimestreId;
        

        // Hacer una solicitud a la vista que retorna el subPromedioUnidad
        fetch(`../obtenerSubPromedioUnidad/${unidadId}/${matriculaId}/${trimestreId}/${clase_Id}`)
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

function cargarReporteTrimestral(trimestreId, claseId) {
    // Limpia el contenedor antes de cargar los nuevos datos
    //document.getElementById('contenedor-aportes-trimestrales').innerHTML = '';
    const cuadernoNotas = document.getElementById('cuaderno-notas');
    // Realiza la petición fetch a la URL creada
    fetch(`../reporteTrimestral/${trimestreId}/${claseId}/`)
   // Realiza la petición fetch a la URL creada
    .then(response => response.text())
    .then(html => {
       // Inserta el HTML recibido en el contenedor
        cuadernoNotas.innerHTML = html;
        // Selecciona las celdas con la clase grade-column
            const tablaAportes = document.getElementById('tbl-reporte');
            
            // Verifica que la tabla exista
            if (!tablaAportes) {
                console.error('No se encontró el contenedor de la tabla.');
                return; // Salir de la función si el contenedor no existe
            }

        
            $('#tbl-reporte').DataTable({
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
            const contenedorTabla = tablaAportes.parentElement; // Asegúrate de tener acceso a la tabla
        
            // Verifica si posicionScroll está vacío y establece la posición adecuada
            const posicionHorizontal = posicionScroll ? parseFloat(posicionScroll) : contenedorTabla.scrollWidth;
        
            // Desplazamiento horizontal en el contenedor de la tabla
            contenedorTabla.scrollTo({
                left: posicionHorizontal,
                behavior: 'smooth' // Desplazamiento suave
            });
         }, 100); // Ajusta el tiempo según lo necesites 
            //cargarEquivalentes();
            //cargarSubpromedios();
    })
    .catch(error => {
        console.error('Error al cargar el listado de cursos:', error);
    });
}







// Función para abrir el modal y cargar los tipos de evaluación si un trimestre está seleccionado
// esto lo mandamos a llamar cuando se carga el template de calificaionesClase
function abrirModalYcargarTipos(trimestreId) {
    const crearAporteModal = new bootstrap.Modal(document.getElementById('crearAporteModal'));
    
    // Llama a la función que carga los tipos de evaluación
    cargarTiposDeEvaluacionCalificacion(trimestreId)
        .then(() => {

            // Si se cargan correctamente, muestra el modal
            setFechaActual('fechaAporte');
            crearAporteModal.show();
        })
        .catch(error => {
            console.error('Error al cargar los tipos de evaluación:', error);
            alert('Hubo un problema al cargar los tipos de evaluación. Inténtalo de nuevo.');
        });
}

function abrirModalYcargarTiposConUnidad(trimestreId) {
    const crearAporteModal = new bootstrap.Modal(document.getElementById('crearAporteModal'));
    
    // Llama a la función que carga los tipos de evaluación
    cargarTiposDeEvaluacionCalificacion(trimestreId)
        .then(() => {

            // Si se cargan correctamente, muestra el modal
            setFechaActual('fechaAporte');
            crearAporteModal.show();
        })
        .catch(error => {
            console.error('Error al cargar los tipos de evaluación:', error);
            alert('Hubo un problema al cargar los tipos de evaluación. Inténtalo de nuevo.');
        });
}



// aqui llamamos a los tipos de evaluacion
function cargarTiposDeEvaluacionCalificacion(trimestreId) {
    return fetch(`../listartiposPorTrimestre/${trimestreId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.message === "ok") {
                const selectTipo = document.getElementById('cboAporteTrimestral');
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













// ahora si vamos a guardar 
function guardarDatosAporteTrimestrales() {


    
    // Captura el formulario y convierte sus datos en un objeto FormData
    const formulario = new FormData(document.getElementById('crearAporteForm'));
// Extrae el valor de cursoAsignatura_id del FormData
    const cursoAsignaturaId = formulario.get('cursoAsignatura_id');
    const trimestreId = formulario.get('trimestreAporte_id')

     // Obtiene los IDs de las matrículas desde la tabla usando el atributo data-matri-id
    const matriculas = Array.from(document.querySelectorAll('tbody tr[data-matri-id]'))
        .map(row => row.getAttribute('data-matri-id'));
    

    // Convierte los datos del formulario a un objeto JSON
    const datosDeAporte = {
        csrfmiddlewaretoken: formulario.get('csrfmiddlewaretoken'),
        nombreAporte: formulario.get('nombreAporte'),
        cursoAsignatura_id: formulario.get('cursoAsignatura_id'),
        trimestreAporte_id: formulario.get('trimestreAporte_id'),
        fechaAporte: formulario.get('fechaAporte'),
        cboAporteTrimestral: formulario.get('cboAporteTrimestral'),

        matriculas: matriculas // Agrega aquí las matrículas
    };
    // Realiza la solicitud fetch para enviar los datos al servidor
    fetch('../crearAporteDocente', {
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
                
                const modalElement = document.getElementById('crearAporteModal');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();
                //cargarDetallesClase(trimestreId, cursoAsignaturaId)
                
                

            } else {
                console.log('Error al crear el aporte:', data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


function guardarDatosAportePorUnidad() {
    // Captura el formulario y convierte sus datos en un objeto FormData
    const formulario = new FormData(document.getElementById('crearAporteForm'));

    // Validación de campos requeridos
    const nombreAporte = formulario.get('nombreAporte');
    const fechaAporte = formulario.get('fechaAporte');
    const cboAporteTrimestral = formulario.get('cboAporteTrimestral');

    if (!nombreAporte || !fechaAporte || !cboAporteTrimestral) {
        alert('Por favor, complete los campos obligatorios: Nombre del Aporte, Fecha y Tipo de Evaluación.');
        return; // Detiene la ejecución si los campos están vacíos
    }

    // Extrae el valor de cursoAsignatura_id y unidadAporte_id del FormData
    const clase_Id = formulario.get('cursoAsignatura_id');
    const unidad_Id = formulario.get('unidadAporte_id');

    // Obtiene los IDs de las matrículas desde la tabla usando el atributo data-matri-id
    const matriculas = Array.from(document.querySelectorAll('tbody tr[data-matri-id]'))
        .map(row => row.getAttribute('data-matri-id'));

    // Convierte los datos del formulario a un objeto JSON
    const datosDeAporte = {
        csrfmiddlewaretoken: formulario.get('csrfmiddlewaretoken'),
        nombreAporte: nombreAporte,
        cursoAsignatura_id: formulario.get('cursoAsignatura_id'),
        trimestreAporte_id: formulario.get('trimestreAporte_id'),
        fechaAporte: fechaAporte,
        cboAporteTrimestral: cboAporteTrimestral,
        unidad_id: unidad_Id,
        matriculas: matriculas // Agrega aquí las matrículas
    };

    // Realiza la solicitud fetch para enviar los datos al servidor
    fetch('../crearAporteDocente', {
        method: 'POST',
        body: JSON.stringify(datosDeAporte),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
        .then(response => response.json()) // Convierte la respuesta a JSON
        .then(data => {
            if (data.estado) {
                console.log('Aporte creado exitosamente.');
                // Cierra el modal automáticamente
                const modalElement = document.getElementById('crearAporteModal');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();
                cargarVistaCalificacionUnidad(unidad_Id, clase_Id);
            } else {
                console.log('Error al crear el aporte:', data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}



// funcion que se debe ejecuatar cuando la taba este cargada 
function selecionarUnAporte(aporteId, trimestreId) {
    const contenedorTabla = document.getElementById('tbl-aportes-unidad').parentElement; // Asegúrate de que `tbl-aportes` es el ID correcto
    const posicionScroll = contenedorTabla.scrollLeft; // Captura la posición del scroll horizontal

    document.getElementById('posicionScroll').value = posicionScroll; // Guarda la posición en un campo oculto


    const url = `../selecionarUnAporte/${aporteId}/`;

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
            document.querySelector("#nombreAporteActualizar").value = data.aporte.nombre;
            document.querySelector("#fechaActualizar").value = data.aporte.fecha;

            listarTiposDeEvaluacionEditar(trimestreId, data.aporte.tipo_evaluacion_id);
            const modalEditar = document.getElementById('modalAporte');
            modalEditar.dataset.aporteId = aporteId;

            const modal = new bootstrap.Modal(document.getElementById('modalAporte'));
            modal.show();
        } else {
            alert("No se pudo obtener la información del aporte.");
        }
    })
    .catch(error => console.error('Error:', error));
}




// otra funcion pero es para ver 

// Función para listar los tipos de evaluación en el modal
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
            
            const selectTipoEvaluacion = document.querySelector("#cboTipoActualizar");
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

// ahora si vamos a guardar el editado 
function guardarAporteEditado() {
    
    const modal = document.getElementById('modalAporte');
    const aporteId = modal.dataset.aporteId;
    
    if (!aporteId) {
        console.error('ID del aporte no definido');
        return;
    }

    const form = document.getElementById('formEditarAporte');
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    // Obtener los valores del formulario
    const idTrimestre = document.getElementById('aporteEditar_idTrimestre').value;
    const idClase = document.getElementById('aporteEditar_idClase').value;

    
    const url = `../editarAporte/${aporteId}/`;

    const data = {
        nombreAporteActualizar: document.querySelector("#nombreAporteActualizar").value,
        fechaActualizar: document.querySelector("#fechaActualizar").value,
        cboTipoActualizar: document.querySelector("#cboTipoActualizar").value,
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
            $('#modalAporte').modal('hide'); // Cierra el modal
        
            
            const posicionScroll = document.getElementById('posicionScroll').value;

            // Llama a la función para cargar los detalles de la clase con la posición del scroll
            //cargarDetallesClase(idTrimestre, idClase, posicionScroll);
        } else if (data.error) {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error('Error:', error));
}


function guardarAporteUnidadEditado() {
    
    const modal = document.getElementById('modalAporte');
    const aporteId = modal.dataset.aporteId;
    
    if (!aporteId) {
        console.error('ID del aporte no definido');
        return;
    }

    const form = document.getElementById('formEditarAporte');
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    // Obtener los valores del formulario
    const idUnidad = document.getElementById('aporteEditar_idUnidad').value;
    const idClase = document.getElementById('aporteEditar_idClase').value;

    
    const url = `../editarAporte/${aporteId}/`;

    const data = {
        nombreAporteActualizar: document.querySelector("#nombreAporteActualizar").value,
        fechaActualizar: document.querySelector("#fechaActualizar").value,
        cboTipoActualizar: document.querySelector("#cboTipoActualizar").value,
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
            $('#modalAporte').modal('hide'); // Cierra el modal
        
            
            const posicionScroll = document.getElementById('posicionScroll').value;

            // Llama a la función para cargar los detalles de la clase con la posición del scroll
            cargarVistaCalificacionUnidad(idUnidad, idClase, posicionScroll);
        } else if (data.error) {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error('Error:', error));
}

// ahora vamos a eliminar 
function eliminarAporte(button) {
    const idAporte = button.dataset.aporteId;
    const idUnidad = button.dataset.unidadEliminarId.trim(); // Elimina espacios
    const idClase = button.dataset.claseEliminarId.trim(); // Elimina espacios
    console.log(idClase)
    if (!idAporte) {
        console.error('ID del aporte no definido');
        return;
    }

    if (confirm('¿Estás seguro de que deseas eliminar este aporte?')) {
        fetch(`../eliminarAporte/${idAporte}/`, {
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
                cargarVistaCalificacionUnidad(idUnidad,idClase);
                // Aquí puedes agregar lógica para actualizar la interfaz de usuario
                // Por ejemplo, eliminar la fila correspondiente o recargar la vista
                // Si estás usando jQuery:
                // $(`#row-${id}`).remove(); // Suponiendo que tienes una fila con un ID específico
            } else {
                alert(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message); // Muestra el error al usuario
            // Opcional: Actualiza la vista o recarga los datos necesarios
            // listarAportes(); // Recarga la lista de aportes para reflejar la eliminación
        });
    }
}

function validarNota(nota) {
    nota = nota.replace(',', '.');
    let valorNumerico = parseFloat(nota);
    return !isNaN(valorNumerico) && valorNumerico >= 0 && valorNumerico <= 10;  // Rango de notas entre 0 y 10
}

// ahora vamos a guardar una calificacion
function guardarCalificaciones(aporteId, trimestreId, claseId) {
    // Guardar la posición de desplazamiento actual
    const scrollPosition = window.scrollY;

    // Seleccionamos todos los inputs relacionados con ese aporteId
    const inputFields = document.querySelectorAll(`input[id$='-${aporteId}']`);
    
    const calificaciones = [];
    let errores = false; // Para rastrear si hubo errores

    // Recorremos los campos y obtenemos los valores de calificación
    inputFields.forEach(input => {
        const matriculaId = input.dataset.matriculaId;
        
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
    fetch(`../calificacionAporteTrimestral/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Para Django
        },
        body: JSON.stringify({
            calificaciones: calificaciones,
            trimestre_id: trimestreId, // Incluye el trimestreId
            clase_id: claseId, // Incluye el claseId
            
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Deshabilitamos los campos nuevamente
            inputFields.forEach(input => input.disabled = true);
            
            cargarCalificaciones();
            //cargarEquivalentes();
            //cargarSubpromedios();
            
            
            // Forzar que la página mantenga la posición de scroll
            window.scrollTo(0, scrollPosition);
        } else {
            alert('Error al guardar las calificaciones');
        }
    })
    .catch(error => console.error('Error:', error));
}

function cargarCalificaciones() {
    // Selecciona todos los inputs de calificaciones
    const inputsCalificaciones = document.querySelectorAll('.nota-input');

    inputsCalificaciones.forEach(function(input) {
        const matriculaId = input.getAttribute('data-matricula-id');
        const aporteId = input.getAttribute('data-aporte-id');
        const calificacionId = input.getAttribute('data-calificacion-id');
        
        // Verifica si calificacionId es válido antes de hacer la solicitud
        if (calificacionId) {
            // Construye la URL para obtener las calificaciones
            const url = `../obtenerCalificaciones/${matriculaId}/${aporteId}/${calificacionId}/`;
            
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

function cargarEquivalentes() {
    const promedioCells = document.querySelectorAll(".porcentaje-promedios");

    promedioCells.forEach(cell => {
        const tipoId = cell.getAttribute("data-tipo-id");
        const matriculaId = cell.getAttribute("data-matricula-id");
        const trimestreId = cell.getAttribute("data-trimestre-id");
        const span = cell.querySelector(".promedio-valor");
        
        // Llamada a la API para obtener el promedio
        fetch(`../obtenerEquivalentesTipos/${tipoId}/${matriculaId}/${trimestreId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    span.textContent = data.promedioTipo;
                } else {
                    span.textContent = "N/A";
                }
            })
            .catch(error => {
                console.error('Error al obtener el promedio:', error);
                span.textContent = "Error";
            });
    });
}

function cargarSubpromedios(){
    // Selecciona todas las celdas donde se cargarán los subpromedios
    const celdasSubpromedio = document.querySelectorAll('.subpromedio');

    // Itera sobre cada celda
    celdasSubpromedio.forEach(celda => {
        const tipoId = celda.getAttribute('data-tipo-id');
        const matriculaId = celda.getAttribute('data-matricula-id');
        const trimestreId = celda.getAttribute('data-trimestre-id');
        const span = celda.querySelector(".subpromedio-valor");
        // Realiza la solicitud para obtener el subpromedio
        fetch(`../obtenerSubpromediosTipos/${tipoId}/${matriculaId}/${trimestreId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Si la solicitud fue exitosa, actualiza el contenido de la celda
                    span.textContent = data.subpromedioTipo; // O usa parseFloat si deseas como número
                } else {
                    console.error('Error al obtener el subpromedio:', data.error);
                    span.textContent = 'N/A'; // Muestra un mensaje si hay error
                }
            })
            .catch(error => {
                console.error('Error en la petición:', error);
                span.textContent = 'Error'; // Muestra un mensaje de error
            });
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
                cargarCalificaciones();
                
                
                

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

                     // Agregar evento paste cuando el input se habilita
                    agregarEventoPaste(input);

                });
            
                button.innerHTML = '<i class="fas fa-save"></i>';
                button.classList.add('btn-guardar');
                
            }
  
        }
    });
});

// funncion para lanzar el modal con la observacion
function mostrarObservacion(element) {

    const calificacionId = element.getAttribute('data-observacion-id');
    var observacionTexto = document.getElementById('observacionesTexto');
    var observacionIdInput = document.getElementById('observacionEditar');

    // Establecer el ID de calificación en el campo oculto del modal
    observacionIdInput.value = calificacionId;
    
    // Hacer una solicitud fetch para obtener la observación
    fetch(`../obtenerObservacion/${calificacionId}/`)
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

function guardarObservacion() {
    var calificacionId = document.getElementById('observacionEditar').value;
    var observacion = document.getElementById('observacionesTexto').value;

    if (!observacion.trim()) {
        alert("La observación no puede estar vacía.");
        return;
    }

    var formData = new FormData();
    formData.append('observacion', observacion);

    fetch(`/editarObservacion/${calificacionId}/`, {
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

// setear la fecha actual 
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
            guardarCalificacionesExamen(examenId,claseId);

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

function guardarCalificacionesExamen(examenId, claseId) {
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
    fetch('../calificacionExamenTrimestral/', { // Reemplaza con tu URL de API
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
            cargarCalificacionesExamen(claseId);
        

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

function cargarCalificacionesExamen(clase_Id) {
    // Selecciona todos los inputs de calificaciones de exámenes
    const inputsCalificaciones = document.querySelectorAll('.nota-input-examen');

    inputsCalificaciones.forEach(function(input) {
        const matriculaId = input.getAttribute('data-matricula-id');
        const examenId = input.getAttribute('data-examen-id');
        
        // Construye la URL para obtener las calificaciones
        const url = `/obtenerCalificacionExamenTrimestral/${matriculaId}/${examenId}/${clase_Id }`;
        
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

function cargarPromediosTrimestrales(clase_Id) {
    const celdasPromedio = document.querySelectorAll('.nota-input-promedio');

    celdasPromedio.forEach(function (celda) {
        const matriculaId = celda.getAttribute('data-matricula-id');
        const trimestreId = celda.getAttribute('data-trimestre-id');

        celda.textContent = 'Cargando...'; // Mensaje temporal

        const url = `/obtenerPromedioTrimestral/${matriculaId}/${trimestreId}/${clase_Id}`;

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


function obtenerPromediosGeneralesTrimestrales() {
    const celdasPromediosTrimestralesGenerales = document.querySelectorAll('.nota-input-promedio-general-trimestral');
    const periodo_id = document.getElementById("periodoGeneralTrimestral").value;
    celdasPromediosTrimestralesGenerales.forEach(celda => {
        const clase_id = celda.getAttribute('data-clase-id');
        const matriculaId = celda.getAttribute('data-matricula-id');
        const trimestreId = celda.getAttribute('data-trimestre-id');
        
        const span = celda.querySelector(".subpromedio-valor");

        fetch(`../obtenerPromediosGeneralesTrimestrales/${matriculaId}/${trimestreId}/${clase_id}/${periodo_id}/`)
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

function mostrarObservacionExamen(element) {
    const calificacionId = element.getAttribute('data-observacion-id');
    var observacionTexto = document.getElementById('observacionesTextoExamen');
    var observacionIdInput = document.getElementById('observacionEditarExamen');

    // Establecer el ID de calificación en el campo oculto del modal
    observacionIdInput.value = calificacionId;
    
    // Hacer una solicitud fetch para obtener la observación
    fetch(`/obtenerObservacionExamen/${calificacionId}/`)
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

function guardarObservacionExamen() {
    var calificacionId = document.getElementById('observacionEditarExamen').value;
    var observacion = document.getElementById('observacionesTextoExamen').value;
    
    if (!observacion.trim()) {
        alert("La observación no puede estar vacía.");
        return;
    }

    var formData = new FormData();
    formData.append('observacion', observacion);
    
    fetch(`/editarObservacionExamen/${calificacionId}/`, {
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
            var modal = document.getElementById('observacionModalExamen');
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



function obtenerPromediosGenerales(clase_id, periodo_id) {
    const celdasPromedio = document.querySelectorAll('.promedio-general');
    
    
    celdasPromedio.forEach(celda => {
        const matricula_id = celda.dataset.matriculaId;
    
        // Realizar la solicitud al endpoint de Django
        fetch(`../obtenerPromediosGenerales/${matricula_id}/${clase_id}/${periodo_id}/`)
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


async function calcularPromedioClaseGeneral(clase_id) {
    try {
        const response = await fetch(`/calcularPromedioClaseGeneral/${clase_id}/`);
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


function manejarSupletorio(boton) {
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
            fetch(`/obtenerMatriculasParaSupletorio/${claseId}/${matriculaId}/`)
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
                                    input.addEventListener('paste',  manejarPegadoSupletorio);
                                }  
                                
                            }
                        });

                        // Mostrar el botón de guardar si al menos un input está habilitado
                        if (botonGuardar) {
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


function manejarPegadoSupletorio(event) {
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


function guardarCalificacionExamenSupletorio(button) {
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
            return fetch('/guardarExamenSupletorio/', {
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


function cargarCalificacionesSupletorio() {
    // Recorrer todos los inputs de calificación en el DOM
    const inputs = document.querySelectorAll('input[data-examen-id][data-matricula-examen][data-clase-id]');

    // Para cada input, obtener el examen_id, matricula_id y clase_id
    inputs.forEach(input => {
        const examenId = input.getAttribute('data-examen-id');
        const matriculaId = input.getAttribute('data-matricula-examen');
        const claseId = input.getAttribute('data-clase-id');

        // Realizar la solicitud fetch para obtener la calificación de este examen
        fetch(`/obtenerCalificacionSupletorio/${examenId}/${matriculaId}/${claseId}/`)
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