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

//antes de guardar debe validarse la fecha de inicio y fin 
// Función para validar fechas de inicio
function validarFechas() {
    const fechaInicioInput = document.getElementById('fechaInicio');
    const fechaFinInput = document.getElementById('fechaFin');

    fechaFinInput.addEventListener('change', function () {
        const fechaInicio = new Date(fechaInicioInput.value);
        const fechaFin = new Date(fechaFinInput.value);

        if (fechaFin < fechaInicio) {
            alert('La fecha de fin no puede ser anterior a la fecha de inicio.');
            fechaFinInput.value = ''; // Limpia el campo de fecha de fin
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {
    // Escuchar cuando el modal es mostrado
    const crearPeriodoModal = document.getElementById('crearPeriodoModal');

    // Verifica si el modal existe antes de intentar agregar el listener
    if (crearPeriodoModal) {
        crearPeriodoModal.addEventListener('shown.bs.modal', function () {
            // Establecer la fecha actual en el input de fecha
            setFechaActual('fechaInicio');
        });
    }

    
});

// Guardar los datos del periodo
function guardarDatosPeriodo() {
    // Captura el formulario y convierte sus datos en un objeto FormData
    const formulario = document.getElementById('crearPeriodoForm');
    
    // Validación de campos requeridos
    if (!formulario.checkValidity()) {
        // Si hay campos no válidos, se muestra un mensaje de error y se detiene el proceso
        alert('Por favor, complete todos los campos requeridos.');
        return;
    }

    // Validar que el campo "decimasPeriodo" esté entre 0 y 5
    const decimasPeriodo = parseInt(document.getElementById('decimasPeriodo').value);
    if (decimasPeriodo < 0 || decimasPeriodo > 5) {
        alert('El valor de "Decimas para este Periodo" debe estar entre 0 y 5.');
        return;
    }

    // Si la validación pasa, se formatea los datos
    setFechaActual('fechaInicio');
    const datosDePeriodos = formatearJSON(new FormData(formulario));

    // Realiza la solicitud fetch para enviar los datos al servidor
    fetch('../crearPeriodo', {
        method: 'POST',
        body: datosDePeriodos,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado) {
            listarPeriodos(); // Actualiza la lista de períodos si es necesario
            // Limpia el formulario o cierra el modal si es necesario
            alert('Período académico creado exitosamente.');
            const modalElement = document.getElementById('crearPeriodoModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            modalInstance.hide();
        } else {
            alert(data.mensaje);  // Muestra el mensaje de error si lo hay
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al intentar crear el período académico.');
    });
}

// Carga la lista de periodos
function listarPeriodos() {
    fetch('../listarPeriodo')
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor_periodos').innerHTML = html;
            // Inicializa DataTables
        })
        .catch(error => {
            console.error('Error al cargar el listado de periodos:', error);
        });
}

// ahora vamos a seleccionar un periodo y enviar esos datos 
function selecionarUnPeriodo(id) {

    fetch(`../selecionarUnPeriodo/${id}/`)
        .then(response => response.json())
        .then(data => {
            // Asigna los datos al formulario del modal
            document.getElementById('periodoId').value = data.id;
            document.getElementById('nombrePeriodoActualizado').value = data.nombre;
            document.getElementById('descripcion').value = data.descripcion;
            document.getElementById('decimasPeriodoActualizado').value = data.cantidad;
            document.getElementById('fechaInicioActualizado').value = data.fecha_inicio;
            document.getElementById('fechaFinActualizado').value = data.fecha_fin;
            document.getElementById('estadoActualizado').value = data.estado;

            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarPeriodo'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// ahora vamos ha actualizar ese periodo que tengamos 
//pero antes veamos las fechas de actualizacion 


function editarUnPeriodo() {
    var formulario = new FormData(document.getElementById('formEditarPeriodo'));

    var datosDePeriodos = formatearJSON(formulario);

    var PeriodoId = document.getElementById('periodoId').value;
    
    

    fetch(`../editarUnPeriodo/${PeriodoId}/`, {
        method: 'POST',
        body: datosDePeriodos,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }

    })
    .then(response => {
        if (!response.ok) {
            throw new Error('El período no existe o ha sido eliminado.');
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message || data.error);
        var myModalEl = document.getElementById('modalEditarPeriodo');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();

        // iziToast.success({
        //     title: "Editado Corectamente",
        //     message: data.message,
        //     position: "topLeft",
        //     timeout: 3000
        // });

        setTimeout(() => {
            listarPeriodos();
        }, 300); // Espera 300ms para asegurar que el modal se haya cerrado completamente
    })
    .catch(error => {
        console.error('Error:', error);
        var myModalEl = document.getElementById('modalEditarPeriodo');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();

        setTimeout(() => {
            listarPeriodos();
            alert(error.message);
        }, 300); // Espera 300ms para asegurar que el modal se haya cerrado completamente
    });
}

// ahora vamos a eliminar es Periodo
function eliminarUnPeriodo(id) {
    if (confirm('¿Estás seguro de que deseas eliminar este período académico?')) {
        fetch(`../eliminarUnPeriodo/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
            }

        })
        .then(response => {
            if (!response.ok) {
                throw new Error('El período no existe o ya ha sido eliminado.');
            }
            return response.json();
        })
            

        .then(data => {
            listarPeriodos();
            if (data.estado) {
                alert(data.mensaje);
                // Aquí podrías agregar lógica para eliminar 

            } else {
                alert(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message); // Muestra el error al usuario
            listarPeriodos(); // Recarga la lista de períodos para reflejar la eliminación
        });
    }
}

// ahora si presionamos en trimestres podremos ver los trimestres de ese id 
function listarTrimestres(id) {
    // Vaciar el contenedor de tipos de evaluación
    document.getElementById('contenedor-tipoEvaluacion').innerHTML = '';
    fetch(`../listarTrimestres/${id}/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor-trabajo').innerHTML = html;
            
            // Inicializa DataTables
        })
        .catch(error => {
            console.error('Error al cargar el listado de periodos:', error);
        });
}

//funcion para que al presionar trimestre se cierre el acordeon 
function cerrarAccordion() {
    var accordionCollapse = document.getElementById('panelsStayOpen-collapseOne');
    var bsCollapse = new bootstrap.Collapse(accordionCollapse, {
        toggle: false
    });
    if (accordionCollapse.classList.contains('show')) {
        bsCollapse.hide();
    }
}

// AHORA SI NO HAY TRIMESTRES PUEDE CREAR 
function guardarDatosTrimestre() {
    const formulario = document.getElementById('formTrimestre');
    
    // Validación de campos requeridos
    if (!formulario.checkValidity()) {
        alert('Por favor, complete todos los campos requeridos.');
        return;
    }

    // Obtener los valores de las fechas
    const fechaInicio = document.getElementById('fechaInicioTri').value;
    const fechaFin = document.getElementById('fechaFinTri').value;

    // Validar que la fecha de inicio sea anterior a la fecha de fin
    if (new Date(fechaInicio) > new Date(fechaFin)) {
        alert('La fecha de inicio no puede ser posterior a la fecha de fin.');
        return;
    }

    const datosDeTrimestre = formatearJSON(new FormData(formulario));

    console.log(datosDeTrimestre);  // Verifica los datos capturados aquí

    fetch('../crearTrimestre', {
        method: 'POST',
        body: datosDeTrimestre,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado) {
            console.log('Trimestre creado exitosamente.');
            const periodoId = JSON.parse(datosDeTrimestre)['periodoTri'];
            console.log('ID del periodo:', periodoId);
            if (periodoId) {
                listarTrimestres(periodoId); // Actualiza la vista sin recargar
            } else {
                console.log('Error al crear el trimestre:', data.mensaje);
            }
        } else {
            console.log('Error al crear el trimestre:', data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// ahora seleccionaremos un  trimestre y mandraemos a un modal los datos 
function selecionarUnTrimestre(id) {

    fetch(`../selecionarUnTrimestre/${id}/`)
        .then(response => response.json())
        .then(data => {
            // Asigna los datos al formulario del modal
            document.getElementById('trimestreId').value = data.id;
            document.getElementById('nombreTrimestreActualizado').value = data.nombre;
            document.getElementById('fechaTrimestreInicio').value = data.fecha_inicio;
            document.getElementById('fechaTrimestreFin').value = data.fecha_fin;


            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarTrimestre'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

//una ves en el modal podemos mandar a guardar los cambios en caso de que haya 
function editarUnTrimestre() {
    const formulario = document.getElementById('formEditarTrimestre');
    
    // Validación de campos vacíos
    if (!formulario.checkValidity()) {
        alert('Por favor, complete todos los campos requeridos.');
        return;
    }

    // Obtener las fechas
    const fechaInicio = document.getElementById('fechaTrimestreInicio').value;
    const fechaFin = document.getElementById('fechaTrimestreFin').value;

    // Validar que la fecha de inicio sea anterior a la fecha de fin
    if (new Date(fechaInicio) > new Date(fechaFin)) {
        alert('La fecha de inicio no puede ser posterior a la fecha de fin.');
        return;
    }

    // Obtener los datos del formulario y el ID del trimestre
    const datosDeTrimestre = formatearJSON(new FormData(formulario));
    const periodo_id = document.getElementById('periodoTriId').value;
    const trimestreId = document.getElementById('trimestreId').value;

    // Realizar la solicitud fetch para editar el trimestre
    fetch(`../editarUnTrimestre/${trimestreId}/`, {
        method: 'POST',
        body: datosDeTrimestre,
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
        listarTrimestres(periodo_id); // Actualiza la lista de trimestres
        const myModalEl = document.getElementById('modalEditarTrimestre');
        const modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide(); // Cierra el modal
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function eliminarUnTrimestre(id) {
    var periodo_id = document.getElementById('periodoTriEli').value
    if (confirm('¿Estás seguro de que deseas eliminar este Trimestre?')) {
        fetch(`../eliminarUnTrimestre/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
            }

        })

            .then(response => response.json())
            .then(data => {
                //listarTrimestres(); 
                if (data.estado) {
                    alert(data.mensaje);
                    // Aquí podrías agregar lógica para eliminar el período de la vista actual, por ejemplo:
                    listarTrimestres(periodo_id);
                    listarTiposEvaluacion(periodo_id);

                    // Maneja la visibilidad del botón y del acordeón
                    if (!data.hay_trimestres) {

                        // Limpia el contenido del acordeón
                        document.getElementById('contenedor-tipoEvaluacion').innerHTML = '';
                    }

                } else {
                    alert(data.mensaje);
                }
            })
            .catch(error => console.error('Error:', error));
    }
}

function listarTiposEvaluacion(id) {
    fetch(`../listarTiposEvaluacion/${id}/`)
        .then(response => response.text())
        .then(html => {
            const contenedor = document.getElementById('contenedor-tipoEvaluacion');

            if (html.trim()) {
                contenedor.innerHTML = html;
            } else {
                contenedor.innerHTML = ''; // Vaciar el contenedor si no hay contenido
                console.log('No hay trimestres, no se muestra el acordeón');
            }
        })
        .catch(error => {
            console.error('Error al cargar el listado de periodos:', error);
        });
}




// ahora vamos a guardar un tipo de evaluacion en lista 
function guardarTipoEvaluacion() {
    const formulario = document.getElementById('crearTipoEvaluacionForm');
    const formData = new FormData(formulario);

    // Validar que todos los campos requeridos están completos
    if (!formulario.checkValidity()) {
        alert('Por favor, complete todos los campos requeridos.');
        return;
    }

    // Obtener el valor del input hidden para el periodo
    const periodoTipo = formData.get('periodoTipo');

    // Obtener los IDs de los trimestres seleccionados
    const trimestresSeleccionados = Array.from(formData.getAll('trimestres'));

    // Verificar que al menos un trimestre esté seleccionado
    if (trimestresSeleccionados.length === 0) {
        alert('Por favor, seleccione al menos un trimestre.');
        return;
    }

    // Obtener el valor del campo de color (con valor predeterminado si no se selecciona)
    const colorTipo = formData.get('colorTipo') || '#FFFFFF'; 

    // Obtener la ponderación
    const ponderadoTipo = parseFloat(formData.get('ponderadoTipo'));

    // Validar que la ponderación esté entre 0 y 100
    if (isNaN(ponderadoTipo) || ponderadoTipo < 0 || ponderadoTipo > 100) {
        alert('La ponderación debe ser un número entre 0 y 100.');
        return;
    }

    // Extraer los datos del formulario
    const datosDeEvaluacion = {
        nombreTipo: formData.get('nombreTipo'),
        ponderadoTipo: ponderadoTipo,
        colorTipo: colorTipo,
        trimestres: trimestresSeleccionados // Lista de IDs de trimestres
    };

    // Realizar la solicitud fetch para guardar el tipo de evaluación
    fetch('../crearTipoEvaluacion', {
        method: 'POST',
        body: JSON.stringify(datosDeEvaluacion),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado) {
            console.log('Tipo de evaluación creado exitosamente.');
            // Actualiza la lista o realiza cualquier acción necesaria
            listarTiposEvaluacion(periodoTipo);
            // Cierra el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('crearTipoEvaluacionModal'));
            modal.hide();
        } else {
            console.log('Error al crear el tipo de evaluación:', data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// ahora vamos a seleciona un TIPO DE Evaluacion

function selecionarUnTipoEvaluacion(id) {

    fetch(`../selecionarUnTipoEvaluacion/${id}/`)
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                console.error('Error al obtener el tipo de evaluación:', data.error);
                return;
            }
            // Asigna los datos al formulario del modal
            document.getElementById('tipoEvaluacionId').value = data.id;
            document.getElementById('nombreEvaluacion').value = data.nombre;
            document.getElementById('ponderadoEvaluacion').value = data.ponderacion;
            document.getElementById('colorEvaluacion').value= data.color;
            
    


            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarTipoEvaluacion'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


// teniendo un solo tipo de evaluacion lo podemos editar

function editarUnTipoEvaluacion() {
    const formulario = document.getElementById('editarTipoEvaluacionForm');
    
    // Validar que todos los campos requeridos están completos
    if (!formulario.checkValidity()) {
        alert('Por favor, complete todos los campos requeridos.');
        return;
    }

    var formData = new FormData(formulario);  // Obtener los datos del formulario

    var tipoId = document.getElementById('tipoEvaluacionId').value;
    var periodo_id = document.getElementById('periodoTipoEva').value;

    // Obtener la ponderación y verificar que esté entre 0 y 100
    var ponderadoEvaluacion = parseFloat(formData.get('ponderadoEvaluacion'));
    if (isNaN(ponderadoEvaluacion) || ponderadoEvaluacion < 0 || ponderadoEvaluacion > 100) {
        alert('La ponderación debe ser un número entre 0 y 100.');
        return;
    }

    // Realizar la solicitud fetch para editar el tipo de evaluación
    fetch(`../editarUnTipoEvaluacion/${tipoId}/`, {
        method: 'POST',
        body: formData,  // Enviar directamente FormData
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),  // Asegúrate de incluir el CSRF token
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message || data.error);
        listarTiposEvaluacion(periodo_id);
    
        // Cerrar el modal de edición
        var myModalEl = document.getElementById('modalEditarTipoEvaluacion');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// ahora vamos a eliminar este tipo de evaluacion
function eliminarUnTipoEvaluacion(id) {
    const periodo_id = document.getElementById('periodoTipoActualizar').value
    if (confirm('¿Estás seguro de que deseas eliminar este Tipo de evaluacion?')) {
        fetch(`../eliminarUnTipoEvaluacion/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                listarTiposEvaluacion(periodo_id)
                // Actualizar la UI, eliminar la fila del tipo de evaluación, etc.
            } else {
                console.error(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}


function listarExamenesTrimestrales(id) {
    fetch(`../listarExamenesTrimestrales/${id}/`)
        .then(response => response.text())
        .then(html => {
            const contenedor = document.getElementById('contenedor-tipoEvaluacion');

            if (html.trim()) {
                contenedor.innerHTML = html;
            } else {
                contenedor.innerHTML = ''; // Vaciar el contenedor si no hay contenido
                console.log('No hay trimestres, no se muestra el acordeón');
            }
        })
        .catch(error => {
            console.error('Error al cargar el listado de periodos:', error);
        });
}

function selecionarUnExamenTrimestral(id) {

    fetch(`../selecionarExamenTrimestral/${id}/`)
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                console.error('Error al obtener el tipo de evaluación:', data.error);
                return;
            }
            // Asigna los datos al formulario del modal
            document.getElementById('ExamenTrimestralId').value = data.id;
            document.getElementById('nombreExamen').value = data.nombre;
            document.getElementById('ponderadoExamen').value = data.ponderacion;
            document.getElementById('descripcionExamen').value= data.descripcion;
            // Selecciona el estado adecuado
            const estadoSelect = document.getElementById('estadoExamen');
            if (data.estado === 'ACTIVO') {
                estadoSelect.value = 'ACTIVO';
            } else {
                estadoSelect.value = 'INACTIVO';
            }
    


            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarExamenTrimestral'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function editarUnExamenTrimestral() {
    // Obtener referencia al formulario
    const form = document.getElementById('editarExamenTrimestralForm');
    const nombreExamen = document.getElementById('nombreExamen').value.trim();
    const ponderadoExamen = document.getElementById('ponderadoExamen').value.trim();
    const descripcionExamen = document.getElementById('descripcionExamen').value.trim();
    const estadoExamen = document.getElementById('estadoExamen').value;

    // Validar campos requeridos
    if (!nombreExamen) {
        alert('El campo "Nombre del Examen Trimestral" es obligatorio.');
        return;
    }

    if (!ponderadoExamen) {
        alert('El campo "Ponderación (%)" es obligatorio.');
        return;
    }

    if (!descripcionExamen) {
        alert('El campo "Descripción" es obligatorio.');
        return;
    }

    // Validar que el ponderado esté entre 0 y 100
    const ponderacion = parseFloat(ponderadoExamen);
    if (isNaN(ponderacion) || ponderacion < 0 || ponderacion > 100) {
        alert('La "Ponderación (%)" debe ser un número entre 0 y 100.');
        return;
    }

    // Validar estado del examen
    if (!estadoExamen) {
        alert('El campo "Estado" es obligatorio.');
        return;
    }

    // Preparar los datos para enviar
    const formulario = new FormData(form);
    const datosExamenTrimestral = formatearJSON(formulario);
    const examen_id = document.getElementById('ExamenTrimestralId').value;
    const periodo_id = document.getElementById('periodoExamenTrimestral').value;

    // Realizar la petición Fetch
    fetch(`../editarUnExamenTrimestral/${examen_id}/`, {
        method: 'POST',
        body: datosExamenTrimestral,
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
        listarExamenesTrimestrales(periodo_id);

        // Cerrar modal
        const myModalEl = document.getElementById('modalEditarExamenTrimestral');
        const modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// ahora vamos a guardar un tipo de evaluacion en lista 
function guardarExamenTrimestral() {
    const formulario = document.getElementById('crearExamenTrimestralForm');
    const formData = new FormData(formulario);

    // Validar que el nombre del examen no esté vacío
    const nombreExamen = formData.get('newNombreExamen').trim();
    if (!nombreExamen) {
        alert('El nombre del examen es requerido.');
        return;
    }

    // Validar que la ponderación esté entre 0 y 100
    const ponderadoExamen = parseFloat(formData.get('newPonderadoExamen'));
    if (isNaN(ponderadoExamen) || ponderadoExamen < 0 || ponderadoExamen > 100) {
        alert('La ponderación debe ser un número entre 0 y 100.');
        return;
    }

    // Validar que la descripción no esté vacía
    const descripcionExamen = formData.get('newDescripcionExamen').trim();
    if (!descripcionExamen) {
        alert('La descripción del examen es requerida.');
        return;
    }

    // Validar que al menos un trimestre esté seleccionado
    const trimestresSeleccionados = Array.from(formData.getAll('trimestres'));
    if (trimestresSeleccionados.length === 0) {
        alert('Debe seleccionar al menos un trimestre.');
        return;
    }

    // Extraer los datos del formulario
    const datosExamenTrimestral = {
        nombreExamen: nombreExamen,
        ponderadoExamen: ponderadoExamen,
        descripcionExamen: descripcionExamen,
        estadoExamen: formData.get('newEstadoExamen'),
        trimestres: trimestresSeleccionados // Lista de IDs de trimestres
    };

    // Enviar los datos al servidor
    fetch('../crearExamenTrimestral', {
        method: 'POST',
        body: JSON.stringify(datosExamenTrimestral),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado) {
            console.log('Examen trimestral creado exitosamente.');
            listarExamenesTrimestrales(formData.get('periodoTipo')); // Actualiza la lista
            const modal = bootstrap.Modal.getInstance(document.getElementById('crearExamenTrimestralModal'));
            modal.hide();
        } else {
            alert('Error al crear el examen: ' + data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar la solicitud.');
    });
}
// ahora vamos a eliminar este tipo de evaluacion
function eliminarUnExamenTrimestral(id) {
    var periodo_id = document.getElementById('periodoTrimestreExamen').value
    if (confirm('¿Estás seguro de que deseas eliminar este examen Trimestral?')) {
        fetch(`../eliminarUnExamenTrimestral/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                listarExamenesTrimestrales(periodo_id)
                // Actualizar la UI, eliminar la fila del tipo de evaluación, etc.
            } else {
                console.error(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function editarUnidadTrimestral() {
    var formulario = new FormData(document.getElementById('editarUnidadTrimestralForm'));

    var datosUnidadrimestral = formatearJSON(formulario);
    var unidad_id = document.getElementById('UnidadTrimestralId').value
    
    var periodo_id = document.getElementById('periodoUnidadTrimestral').value

    //var trimestreId = document.getElementById('trimestreId').value;

    fetch(`../editarUnidadTrimestral/${unidad_id}/`, {
        method: 'POST',
        body: datosUnidadrimestral,
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
            listarUnidadesTrimestrales(periodo_id);
            var myModalEl = document.getElementById('modalEditarUnidadTrimestral');
            var modal = bootstrap.Modal.getInstance(myModalEl);
            modal.hide();
        })
        .catch(error => {
            console.error('Error:', error);

        });
}
// CRUD UNIDAD TRIMESTRAL

function listarUnidadesTrimestrales(id) {
    fetch(`../listarUnidadesTrimestrales/${id}/`)
        .then(response => response.text())
        .then(html => {
            const contenedor = document.getElementById('contenedor-tipoEvaluacion');

            if (html.trim()) {
                contenedor.innerHTML = html;
            } else {
                contenedor.innerHTML = ''; // Vaciar el contenedor si no hay contenido
                console.log('No hay trimestres, no se muestra el acordeón');
            }
        })
        .catch(error => {
            console.error('Error al cargar el listado de periodos:', error);
        });
}

function selecionarUnidadTrimestral(id) {

    fetch(`../selecionarUnidadTrimestral/${id}/`)
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                console.error('Error al obtener La unidad de este trimestre:', data.error);
                return;
            }
            // Asigna los datos al formulario del modal
            document.getElementById('UnidadTrimestralId').value = data.id;
            document.getElementById('nombreUnidad').value = data.nombre;
            
            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarUnidadTrimestral'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function guardarUnidadTrimestral() {
    const formulario = document.getElementById('crearUnidadTrimestralForm');
    const formData = new FormData(formulario);

    // Obtener el valor del input hidden para el periodo
    const periodoTipo = formData.get('periodoTipo');

    


    // Verificar que el nombre de la unidad no esté vacío
    const nombreUnidad = formData.get('newNombreUnidad').trim();
    if (!nombreUnidad) {
        alert('El nombre de la unidad trimestral no puede estar vacío.');
        return;
    }

    // Obtener los IDs de los trimestres seleccionados
    const trimestresSeleccionados = Array.from(formData.getAll('trimestres'));
    // Verificar que trimestresSeleccionados sea una lista de strings
    if (trimestresSeleccionados.length === 0) {
        alert('No se han seleccionado trimestres.');
        return;
    }

    

    // Extraer los datos del formulario
    const datosUnidadTrimestral = {
        nombreUnidad: nombreUnidad, // Asegurarse de que se envíe el nombre correcto
        trimestres: trimestresSeleccionados // Lista de IDs de trimestres
    };

    fetch('../crearUnidadTrimestral', {
        method: 'POST',
        body: JSON.stringify(datosUnidadTrimestral),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Asegúrate de tener una función `getCookie`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado) {
            console.log('Unidad trimestral creada exitosamente.');
            // Actualiza la lista o realiza cualquier acción necesaria
            listarUnidadesTrimestrales(periodoTipo);
            // Cierra el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('crearUnidadTrimestralModal'));
            modal.hide();
        } else {
            console.log('Error al crear la unidad trimestral:', data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function eliminarUnaUnidadTrimestral(id) {
    var periodo_id = document.getElementById('periodoTrimestreExamen').value
    if (confirm('¿Estás seguro de que deseas eliminar esta Unidad Trimestral?')) {
        fetch(`../eliminarUnidadTrimestral/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                listarUnidadesTrimestrales(periodo_id)
                // Actualizar la UI, eliminar la fila del tipo de evaluación, etc.
            } else {
                console.error(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function listarExamenesFinales(id) {
    document.getElementById('contenedor-tipoEvaluacion').innerHTML = '';
    fetch(`../listarExamenFinal/${id}/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor-trabajo').innerHTML = html;
            
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
        });
}


function selecionarUnExamenFinal(id) {

    fetch(`../selecionarExamenFinal/${id}/`)
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                console.error('Error al obtener el tipo de evaluación:', data.error);
                return;
            }
            // Asigna los datos al formulario del modal
            document.getElementById('examenFinalId').value = data.id;
            document.getElementById('nombreExamenFinal').value = data.nombre;
            document.getElementById('ponderadoExamenFinal').value = data.ponderacion;
            document.getElementById('descripcionExamenFinal').value= data.descripcion;
            // Selecciona el estado adecuado
            const estadoSelect = document.getElementById('estadoExamenFinal');
            if (data.estado === 'ACTIVO') {
                estadoSelect.value = 'ACTIVO';
            } else {
                estadoSelect.value = 'INACTIVO';
            }
    


            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarExamenFinal'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function editarUnExamenFinal() {
    // Obtener los datos del formulario
    const formulario = new FormData(document.getElementById('editarExamenFinalForm'));

    // Validar el campo de ponderado
    const ponderado = parseFloat(document.getElementById('ponderadoExamenFinal').value);
    if (isNaN(ponderado) || ponderado < 0 || ponderado > 100) {
        alert('El campo "Ponderación" debe ser un número entre 0 y 100.');
        return; // Detener la ejecución si no cumple la validación
    }

    // Formatear los datos a JSON
    const datosExamenFinal = formatearJSON(formulario);
    const examenFinal_id = document.getElementById('examenFinalId').value;
    const periodo_id = document.getElementById('periodoExamenFinal').value;

    fetch(`../editarUnExamenFinal/${examenFinal_id}/`, {
        method: 'POST',
        body: datosExamenFinal,
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
            listarExamenesFinales(periodo_id);
            const myModalEl = document.getElementById('modalEditarExamenFinal');
            const modal = bootstrap.Modal.getInstance(myModalEl);
            modal.hide();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function guardarExamenFinal(periodo_id) {
    // Obtener los datos del formulario
    const formulario = new FormData(document.getElementById('crearExamenFinalForm'));

    // Validar los campos
    const nombre = document.getElementById('newNombreExamenFinal').value.trim();
    const ponderado = parseFloat(document.getElementById('newPonderadoExamenFinal').value);
    const estado = document.getElementById('newEstadoExamenFinal').value;
    const descripcion = document.getElementById('newDescripcionExamenFinal').value.trim();

    // Validar que el nombre no esté vacío
    if (!nombre) {
        alert('El campo "Nombre del Examen Final" es obligatorio.');
        return;
    }

    // Validar el rango del ponderado
    if (isNaN(ponderado) || ponderado < 0 || ponderado > 100) {
        alert('El campo "Ponderación" debe ser un número entre 0 y 100.');
        return;
    }

    // Validar que el estado esté seleccionado
    if (!estado) {
        alert('Debe seleccionar un estado para el examen final.');
        return;
    }

    

    // Formatear los datos a JSON
    const datosExamenFinal = formatearJSON(formulario);

    // Enviar los datos al servidor
    fetch(`../crearExamenFinal/${periodo_id}/`, {
        method: 'POST',
        body: datosExamenFinal,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log('Examen Final creado exitosamente.');

                // Cerrar el modal
                const myModalEl = document.getElementById('crearExamenFinalModal');
                const modal = bootstrap.Modal.getInstance(myModalEl);
                modal.hide();

                // Actualizar la lista de exámenes finales
                listarExamenesFinales(periodo_id);
            } else {
                console.log('Error al crear el Examen Final:', data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function eliminarUnExamenFinal(id) {
    var periodo_id = document.getElementById('periodoExamenFinal').value
    console.log(periodo_id)
    if (confirm('¿Estás seguro de que deseas eliminar esta Examen Final?')) {
        fetch(`../eliminarUnExamenFinal/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                listarExamenesFinales(periodo_id)
                // Actualizar la UI, eliminar la fila del tipo de evaluación, etc.
            } else {
                console.error(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}



document.addEventListener('DOMContentLoaded', function () {

    listarPeriodos();
});


// aqui vamos a  listar los cursos
// ahora si presionamos en trimestres podremos ver los trimestres de ese id 
function listarCursos(id) {
    document.getElementById('contenedor-tipoEvaluacion').innerHTML = '';
    fetch(`../listarCursos/${id}/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('contenedor-trabajo').innerHTML = html;
            // Inicializa DataTables
        })
        .catch(error => {
            console.error('Error al cargar el listado de cursos:', error);
        });
}

// guardar los cursos nuevos 
function guardarDatosCurso(){
    const formulario = new FormData(document.getElementById('formCrearCurso'))
    const  datosdeCurso = formatearJSON(formulario)

    fetch('../crearCurso', {
        method: 'POST',
        body: datosdeCurso,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado) {
            console.log('Curso creado exitosamente.');
            const periodoId = JSON.parse(datosdeCurso)['periodoAcademico_id'];
            console.log('ID del periodo:', periodoId);
            if (periodoId) {
                listarCursos(periodoId); // <--- Actualizamos la vista sin recargar
            } else {
                console.log('Error al crear el trimestre:', data.mensaje);
            }

            // Aquí puedes actualizar la lista de cursos o hacer cualquier otra acción
            document.getElementById('formCrearCurso').reset(); // Resetea el formulario
            var modal = bootstrap.Modal.getInstance(document.getElementById('crearCursoModal'));
            modal.hide(); // Cierra el modal

            // Puedes llamar a una función para listar cursos aquí, si es necesario
            // listarCursos();
        } else {
            console.log('Error al crear el curso:', data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });


}




function selecionarUnCurso(id) {

    fetch(`../selecionarUnCurso/${id}/`)
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                console.error('Error al obtener el tipo de evaluación:', data.error);
                return;
            }
            // Asigna los datos al formulario del modal
            document.getElementById('CursoIdActualizar').value = data.id;
            document.getElementById('nombreCursoActualizar').value = data.nombreCurso;
            document.getElementById('paraleloCursoActualizar').value = data.paraleloCurso;
            document.getElementById('descripcionCursoActualizar').value = data.descripcionCurso;
            document.getElementById('estadoCursoActualizar').value = data.estadoCurso;


            // Muestra el modal
            var myModal = new bootstrap.Modal(document.getElementById('modalEditarCurso'));
            myModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


function editarUnCurso() {
    var formulario = new FormData(document.getElementById('formEditarCurso'));

    var datosDeCurso = formatearJSON(formulario);
    var cursoId = document.getElementById('CursoIdActualizar').value
    var periodo_id = document.getElementById('periodoCursoId').value

    //var trimestreId = document.getElementById('trimestreId').value;

    fetch(`../editarUnCurso/${cursoId}/`, {
        method: 'POST',
        body: datosDeCurso,
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
            listarCursos(periodo_id);
            var myModalEl = document.getElementById('modalEditarCurso');
            var modal = bootstrap.Modal.getInstance(myModalEl);
            modal.hide();
        })
        .catch(error => {
            console.error('Error:', error);

        });
}

// ahora vamos a eliminar este tipo de evaluacion
function eliminarUnCurso(id) {
    var periodo_id = document.getElementById('periodoCursoEliminar').value
    if (confirm('¿Estás seguro de que deseas eliminar este Curso?')) {
        fetch(`../eliminarUnCurso/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.estado) {
                console.log(data.mensaje);
                listarCursos(periodo_id)
                // Actualizar la UI, eliminar la fila del tipo de evaluación, etc.
            } else {
                console.error(data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}


// setear el inicio del trimestre 
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