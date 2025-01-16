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

const listarPeriodosEstudiantes = async () => {
    try {
        const response = await fetch("../listarPeriodosEstudiantes");
        const data = await response.json();

        if (data.message === "okey") {
            let opciones = '';
            data.periodos.forEach((periodo) => {
                opciones += `<option value='${periodo.id}'>${periodo.nombre}</option>`;
            });
            cboPeriodoEstudiante.innerHTML = opciones;

            // Seleccionar el primer período por defecto
            const primerPeriodoId = data.periodos[0]?.id;
            listarTrimestresEstudiantes(primerPeriodoId);

            // Llamar a las calificaciones del primer período si no hay trimestre seleccionado
            listarCalificacionesPorPeriodo(primerPeriodoId);

            // Escuchar cambios en el select del período
            cboPeriodoEstudiante.addEventListener("change", () => {
                const periodoSeleccionado = cboPeriodoEstudiante.value;
                listarTrimestresEstudiantes(periodoSeleccionado);

                // Limpiar select de trimestre cuando se cambia el período
                cboTrimestreEstudiante.innerHTML = `<option value="">Selecciona un trimestre</option>`;

                // Ejecutar la función para listar calificaciones solo del período
                listarCalificacionesPorPeriodo(periodoSeleccionado);
            });

            // Escuchar cambios en el select de trimestre
            cboTrimestreEstudiante.addEventListener("change", () => {
                const periodoSeleccionado = cboPeriodoEstudiante.value;
                const trimestreSeleccionado = cboTrimestreEstudiante.value;

                if (trimestreSeleccionado) {
                    // Si hay trimestre seleccionado, listar calificaciones por período y trimestre
                    listarCalificacionesPorTrimestre(periodoSeleccionado, trimestreSeleccionado);
                } else {
                    // Si se selecciona "Selecciona un trimestre", listar solo por período
                    listarCalificacionesPorPeriodo(periodoSeleccionado);
                }
            });
        }
    } catch (error) {
        console.error(error);
    }
};

function listarTrimestresEstudiantes(periodo_id) {
    if (!periodo_id) {
        console.error("El ID del periodo no es válido.");
        return;
    }

    fetch(`../listarTrimestresEstudiantes/${periodo_id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.message === "ok") {
                const select = document.getElementById('cboTrimestreEstudiante');
                // Limpiar opciones previas
                select.innerHTML = '<option value="">Selecciona un trimestre</option>';

                // Agregar cada trimestre al select
                data.trimestres.forEach(trimestre => {
                    const trimestreOption = document.createElement('option');
                    trimestreOption.value = trimestre.id; // Usar solo el ID
                    trimestreOption.textContent = trimestre.nombre; // Texto de la opción
                    select.appendChild(trimestreOption);
                });
            } else {
                console.error("Error en la respuesta del servidor:", data.message);
            }
        })
        .catch(error => console.error("Error al cargar los trimestres:", error));
}

// aqui renderizo el reporte
function listarCalificacionesPorPeriodo(periodo_id) {
    // Limpia el contenedor antes de cargar los nuevos datos
    document.getElementById('contenedor_reporte_trimestral').innerHTML = '';

    // Realiza la petición fetch a la URL creada
    fetch(`../listarCalificacionesPorPeriodo/${periodo_id}/`)
        .then(response => response.text())
        .then(html => {
            // Inserta el HTML recibido en el contenedor
            document.getElementById('contenedor_reporte_trimestral').innerHTML = html;
            // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
        })
        .catch(error => {
            console.error('Error al cargar las calificaciones:', error);
        });
}

function listarCalificacionesPorTrimestre(periodo_id, trimestre_id) {
    // Limpia el contenedor antes de cargar los nuevos datos
    document.getElementById('contenedor_reporte_trimestral').innerHTML = '';

    // Realiza la petición fetch a la URL creada
    fetch(`../listarCalificacionesPorTrimestre/${periodo_id}/${trimestre_id}/`)
        .then(response => response.text())
        .then(html => {
            // Inserta el HTML recibido en el contenedor
            document.getElementById('contenedor_reporte_trimestral').innerHTML = html;
            // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
        })
        .catch(error => {
            console.error('Error al cargar las calificaciones:', error);
        });
}




const cargaInicial=async()=>{
    await listarPeriodosEstudiantes();
    cboPeriodoEstudiante.addEventListener("change",(event)=>{
        listarCalificacionesPorPeriodo(event.target.value)
        
    })  
}

window.addEventListener("load",async()=>{
    await cargaInicial()  
})


// cargar los promedios trimestrales de cada estudiante 

function calcularPromedioTrimestralEstudiante() {
    const celdasPromedio = document.querySelectorAll('.promedio-trimestral-estudiante');

    celdasPromedio.forEach(function(celda) {
        // Extraer los valores correctos desde los atributos data-matricula y data-trimestre
        const matriculaId = celda.dataset.matricula; // Cambiado de 'data-matricula-id' a 'data-matricula'
        const trimestreId = celda.dataset.trimestre; // Correcto, mantén 'data-trimestre'

        // Verificar que trimestreId no sea undefined
        if (trimestreId !== undefined && matriculaId !== undefined) {
            // Realiza la solicitud Fetch con los IDs correctos
            fetch(`/calcularPromedioTrimestralEstudiante/${matriculaId}/${trimestreId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.promedio_total !== undefined) {
                        celda.textContent = data.promedio_total;
                    } else {
                        celda.textContent = "No Disponible";
                    }
                })
                .catch(error => {
                    console.error('Error al obtener el promedio:', error);
                    celda.textContent = "Error";
                });
        } else {
            console.error("El trimestre_id o matricula_id es undefined");
        }
    });
}


