
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

function vistaAsitencias(clase_id){
  // Asegúrate de que periodoTrabajo está correctamente definido
  const periodoAsistencia = document.getElementById('periodoAsistenciaReporte'); // 
  
  if (periodoAsistencia) { // Verifica que periodoTrabajo no sea null o undefined
      const periodo_id = periodoAsistencia.getAttribute('data-periodoAsistencia-Reporte');
      
      document.getElementById('contenedor_trimestres').innerHTML = '';
      
      // Realiza la petición fetch a la URL creada
      fetch(`../vistaAsistencias/${clase_id}/`)
          .then(response => response.text())
          .then(html => {
              cerrarAccordion();
              // Inserta el HTML recibido en el contenedor
              document.getElementById('contenedor_trimestres').innerHTML = html;
              // Aquí puedes inicializar cualquier plugin adicional, como DataTables, si es necesario
              
              verTrimestres(periodo_id);
          })
          .catch(error => {
              console.error('Error al cargar el listado de aportes:', error);
          });
  } else {
      console.error('Elemento periodoAsistenciaReporte no encontrado');
  }
}

function verTrimestres(periodo_id){
  
  if (!periodo_id) {
    console.error("El ID del periodo no es válido.");
    return;
  }
  fetch(`../obtener_trimestres/${periodo_id}/`)
      .then(response => response.json())
      .then(data => {
          if (data.message === "ok") {
              const select = document.getElementById('cboTrimestreAsistencia');
              select.innerHTML = '<option value="">Selecciona un trimestre</option>';
              data.trimestres.forEach(trimestre => {
                  const option = document.createElement('option');
                  option.value = trimestre.id;
                  option.textContent = trimestre.nombre;
                  select.appendChild(option);
              });
              // Configura el manejador de eventos para el cambio en el select
              select.addEventListener('change', function () {
                  const trimestre_id = this.value;
                  const clase_id = document.getElementById('claseAsistencia').value;

                  if (trimestre_id) {
                      
                      listarAsistencias(trimestre_id,clase_id);
                      
                  }
              });

          } else {
              console.error("Error en la respuesta del servidor:", data.message);
          }
      })
      .catch(error => console.error("Error al cargar los trimestres:", error));
}

function inicializarTablas() {
  // Seleccionar todas las tablas que quieres inicializar con DataTables
  // Inicializar DataTables si la tabla existe
  const tablas = document.querySelectorAll('.estilo-tablas');
  
  tablas.forEach(tabla => {
      $(tabla).DataTable({
          language: {
              search: "Buscar:",
          },
          paging: false,
          ordering: false,
          info: false,
          scrollX: true,
          fixedHeader: true,
      });
  });
}

//html para listar asistencias
function listarAsistencias(trimestre_id, clase_id) {
  console.log(trimestre_id, clase_id);

  const contenedorAsistencias = document.getElementById('contenedor-asistencias');
  contenedorAsistencias.innerHTML = '';  // Limpiar el contenedor
  const currentScrollPosition = contenedorAsistencias.scrollTop;

  // Verificar la URL antes de realizar la petición
  const url = `../listar_asistencias/${trimestre_id}/${clase_id}/`;
  console.log("Petición a: " + url);

  // Realiza la petición fetch a la URL creada
  fetch(url)
      .then(response => response.text())
      .then(html => {
          if (html) {
              // Inserta el HTML recibido en el contenedor
              contenedorAsistencias.innerHTML = html;
              loadCalendar();  // Asegúrate de que esta función está definida correctamente
              contenedorAsistencias.scrollTop = currentScrollPosition;
              inicializarTablas();
          } else {
              console.error('Error: no se recibió HTML válido.');
          }
      })
      .catch(error => {
          console.error('Error al cargar el listado de asistencias:', error);
      });
}

let currentDate = new Date();

function loadCalendar() {
  const monthYear = document.getElementById("monthYear");
  const calendarDays = document.getElementById("calendarDays");
  const claseId = document.getElementById("claseAsistencia").value; // Obtener ID de la clase
  const trimestreId = document.getElementById("cboTrimestreAsistencia").value;

  // Obtener el número total de días en el mes actual
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  
  // Obtener el día de la semana del primer día del mes (ajustando para que empiece el lunes)
  let firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  if (firstDay === 0) firstDay = 7; // Si es domingo, lo tratamos como 7
  
  monthYear.innerText = currentDate.toLocaleDateString("es-ES", { month: 'long', year: 'numeric' });

  // Limpiar los días del calendario antes de volver a dibujar
  calendarDays.innerHTML = "";

  let days = '';
  
  // Rellenar las celdas vacías antes del primer día del mes
  for (let i = 1; i < firstDay; i++) {
    days += `<td></td>`;
  }
  
  for (let i = 1; i <= daysInMonth; i++) {
    const currentDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
  
    // Habilitar todos los días sin restricciones
    days += `<td data-dia="${i}" data-mes="${currentDate.getMonth()}" data-anio="${currentDate.getFullYear()}" onclick="selectDate(this, ${i})" style="cursor: pointer;">${i}</td>`;
  
  
    if ((i + firstDay - 1) % 7 === 0) { // Salto de línea después de cada domingo
      days += `</tr><tr>`;
    }

  }
  

  calendarDays.innerHTML = `<tr>${days}</tr>`;

  // Obtener las asistencias para el mes y marcar los días con asistencia
  obtenerAsistenciasDelMes(claseId,trimestreId);
}



function prevMonth() {
  currentDate.setMonth(currentDate.getMonth() - 1);
  loadCalendar();
}

function nextMonth() {
  currentDate.setMonth(currentDate.getMonth() + 1);
  loadCalendar();
}

function obtenerAsistenciasDelMes(claseId,trimestreId) {
  const fechaMes = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, "0")}`;
  
  
  fetch(`/obtener_asistencias_por_mes/${claseId}/${trimestreId}/${fechaMes}/`) // Agregamos el ID de la clase
      .then((response) => {
          if (!response.ok) {
              throw new Error("Error al obtener asistencias");
          }
          return response.json();
      })
      .then((data) => {
          if (data.status === "success") {
              marcarDiasConAsistencia(data.diasConAsistencia);
          } else {
              console.error("Error del servidor:", data.message || "Error desconocido");
          }
      })
      .catch((error) => {
          console.error("Error al obtener las asistencias:", error);
      });
}



function selectDate(element, diaSeleccionado) {
  console.log("Valor recibido de day:", diaSeleccionado); // Depuración del valor del día
  const selected = document.querySelector('.selected');
  if (selected) {
    selected.classList.remove('selected');
  }
  element.classList.add('selected');

  fechaSeleccionadaGlobal = new Date(currentDate.getFullYear(), currentDate.getMonth(), diaSeleccionado);

  if (isNaN(fechaSeleccionadaGlobal)) {
      console.error("Fecha inválida:", fechaSeleccionadaGlobal);
      return;
  }

  // Formatear manualmente la fecha (YYYY-MM-DD)
  const fechaISO = `${fechaSeleccionadaGlobal.getFullYear()}-${String(fechaSeleccionadaGlobal.getMonth() + 1).padStart(2, "0")}-${String(fechaSeleccionadaGlobal.getDate()).padStart(2, "0")}`;
  console.log("Fecha en formato ISO:", fechaISO);

  // Mostrar la columna de asistencias
  mostrarAsistencias(diaSeleccionado);

}




function mostrarAsistencias(diaSeleccionado) {
  const fechaSeleccionada = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, "0")}-${String(diaSeleccionado).padStart(2, "0")}`;

  fetch(`/obtener_asistencia/${fechaSeleccionada}/`) // Usamos el ID de la clase
      .then((response) => {
          if (!response.ok) {
              throw new Error("Error al obtener asistencias");
          }
          return response.json();
      })
      .then((data) => {
          if (data.status === "success") {
              actualizarTablaAsistencias(data.data, diaSeleccionado);
          } else {
              console.error("Error del servidor:", data.message || "Error desconocido");
          }
      })
      .catch((error) => {
          console.error("Error al obtener las asistencias:", error);
      });
}


function actualizarTablaAsistencias(asistencias, diaSeleccionado) {
  const tablaAsistencia = document.getElementById("tbl-asistencia");
  const filas = tablaAsistencia.querySelectorAll("tbody tr");

  filas.forEach((fila) => {
    const matriculaId = fila.getAttribute("data-matricula-id");
    const periodoDivisionId = fila.getAttribute("data-periodo-division-id");
    const claseId = fila.getAttribute("data-clase-id");

    // Buscamos la asistencia correspondiente
    const asistencia = asistencias.find((as) => 
      as.matricula_id === parseInt(matriculaId) &&
      as.periodo_division_id === parseInt(periodoDivisionId) &&
      as.clase_id === parseInt(claseId)
    );

    const asistenciaCell = fila.querySelector(".asistencia-col"); // Asegúrate de que la celda correcta sea seleccionada

    if (asistencia) {
      // Si la asistencia está disponible, se carga el estado seleccionado
      asistenciaCell.innerHTML = `
        <select data-dia="${diaSeleccionado}">
          <option value="ASISTENCIA" ${asistencia.estado === "ASISTENCIA" ? "selected" : ""}>AS</option>
          <option value="ATRASO" ${asistencia.estado === "ATRASO" ? "selected" : ""}>AT</option>
          <option value="FALTA JUSTIFICADA" ${asistencia.estado === "FALTA JUSTIFICADA" ? "selected" : ""}>FJ</option>
          <option value="FALTA INJUSTIFICADA" ${asistencia.estado === "FALTA INJUSTIFICADA" ? "selected" : ""}>FI</option>
        </select>
      `;
    } else {
      // Si no hay asistencia, se carga el select con opciones vacías
      asistenciaCell.innerHTML = `
        <select data-dia="${diaSeleccionado}">
          <option value="ASISTENCIA">AS</option>
          <option value="ATRASO">AT</option>
          <option value="FALTA JUSTIFICADA">FJ</option>
          <option value="FALTA INJUSTIFICADA">FI</option>
        </select>
      `;
    }

    console.log(`Estado de la asistencia para matrícula ${matriculaId}: ${asistencia?.estado || 'No disponible'}`);
  });

  // Actualización del encabezado de la columna de asistencia
  const thAsistencia = document.getElementById("btn-asis");  // Cambié aquí para que busque por ID
 

  thAsistencia.innerHTML = `
    <div class="d-flex flex-column align-items-center">
      <span>Asistencia (${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${diaSeleccionado})</span>
      <button id="btn-guardar" class="btn btn-success btn-sm mt-2" onclick="guardarAsistencia(event)">
        <i class="fas fa-save"></i>
      </button>
    </div>
  `;

  // Asegurarse de que las celdas de asistencia sean visibles
  document.querySelectorAll(".asistencia-col").forEach((col) => {
    col.style.display = ""; // Mostrar columna de asistencia
  });
}




// Obtener el token CSRF del campo oculto
function getCSRFToken() {
  return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

function guardarAsistencia(event) {
  event.preventDefault(); // Evitar el submit por defecto del formulario

  const selects = document.querySelectorAll("tbody select");
  const asistenciaData = Array.from(selects).map((select) => {
    const diaSeleccionado = select.getAttribute("data-dia");
    const fechaCompleta = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      diaSeleccionado
    );

    return {
      fecha: fechaCompleta.toISOString().split("T")[0], // Formato 'YYYY-MM-DD'
      estado: select.value,
      matricula_id: select.closest("td").getAttribute("data-matricula-id"),
      periodo_division_id: select.closest("td").getAttribute("data-periodo-division-id"),
      clase_id: select.closest("td").getAttribute("data-clase-id"),
    };
  });

  console.log("Datos de asistencia a guardar:", asistenciaData);

  fetch("/registrar_asistencia/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify(asistenciaData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Error en la respuesta del servidor");
      }
      return response.json();
    })
    .then((data) => {
      if (data.status === "success") {
        alert("Asistencia guardada exitosamente.");
        loadCalendar();
        const trimestre_id = document.getElementById('cboTrimestreAsistencia').value;
        const clase_id = document.getElementById('claseAsistencia').value;
        listarAsistencias(trimestre_id, clase_id); // Actualiza la tabla
      } else {
        alert("Hubo un error al guardar la asistencia.");
        console.error("Error del servidor:", data.message || "Error desconocido");
      }
    })
    .catch((error) => {
      console.error("Error al guardar la asistencia:", error);
      alert("No se pudo guardar la asistencia.");
    });
}

// Marcar el día que tiene asistencia
function marcarDiasConAsistencia(diasConAsistencia) {
  diasConAsistencia.forEach((dia) => {
    const diaElemento = document.querySelector(`#calendarDays td[data-dia="${dia}"]`);
    if (diaElemento) {
      diaElemento.classList.add("con-asistencia"); // Marca el día con la clase 'con-asistencia'
    }
  });
}


function CargarCalendarioDias(matriculaId, trimestreId, estado) {
  fetch(`/obtener_dias_estado/${estado}/${matriculaId}/${trimestreId}`)
    .then(response => response.json())
    .then(data => {
      console.log("Datos recibidos de la API:", data);
      // Actualizar el calendario con los días obtenidos
      actualizarCalendarPorEstado(data, estado);
    })
    .catch(error => console.error("Error al cargar los días de asistencia:", error));
}

function actualizarCalendarPorEstado(days, estado) {
  // Limpia las clases anteriores
  const calendarCells = document.querySelectorAll("#calendarDays td");
  calendarCells.forEach(cell => {
    cell.classList.remove("asistencias", "atrasos", "faltas-justificadas", "faltas-injustificadas");
  });

  // Pintar las celdas correspondientes
  days.forEach(day => {
    const dia = parseInt(day.fecha.split("-")[2]);  // Extrae el día
    const mes = parseInt(day.fecha.split("-")[1]) - 1;  // Extrae el mes (de 0 a 11)
    const anio = parseInt(day.fecha.split("-")[0]); // Extrae el año

    // Busca la celda correspondiente al día, mes y año
    const dayCell = document.querySelector(`[data-dia="${dia}"][data-mes="${mes}"][data-anio="${anio}"]`);
    
    if (dayCell) {
      console.log(`Pintando celda para el día ${dia}/${mes+1}/${anio} con estado ${estado}`);
      if (estado === "ASISTENCIA") {
        dayCell.classList.add("asistencias");
      } else if (estado === "ATRASO") {
        dayCell.classList.add("atrasos");
      } else if (estado === "FALTA JUSTIFICADA") {
        dayCell.classList.add("faltas-justificadas");
      } else if (estado === "FALTA INJUSTIFICADA") {
        dayCell.classList.add("faltas-injustificadas");
      }
    } else {
      console.warn("No se encontró la celda para el día:", dia);
    }
  });
}



function cargarReporte(claseId) {
  const contenedor = document.getElementById('contenedor_trimestres');

  // Mostrar un mensaje de carga mientras se procesa
  contenedor.innerHTML = '<p>Cargando reporte...</p>';

  // Realizar la petición al servidor
  fetch(`/resumen_asistencias/${claseId}/`, {
      method: 'GET',
      headers: {
          'X-Requested-With': 'XMLHttpRequest'
      }
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Error al cargar los datos');
      }
      return response.text(); // HTML esperado desde el servidor
  })
  .then(html => {
      cerrarAccordion();
      // Insertar el HTML recibido en el contenedor
      contenedor.innerHTML = html;
      $(document).ready(function () {
        $('#tablaAsistencias').DataTable({
            language: {
                search: "Buscar:",
               
            },
            info: false,
            paging: false,
            ordering: false,
            
        });
      });
  })
  .catch(error => {
      console.error('Error:', error);
      contenedor.innerHTML = '<p>Ocurrió un error al cargar el reporte</p>';
  });
}

window.onload = function() {
  loadCalendar();
};