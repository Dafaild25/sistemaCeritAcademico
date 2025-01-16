async function cargarDatosGraficos() {
    try {
        // Hacer una solicitud al servidor para obtener los datos
        const response = await fetch('../datos-graficos/');
        const datos = await response.json();

        // Configuración del gráfico de estudiantes
        const graficoEstudiantes = new Chart(document.getElementById('graficoEstudiantes'), {
            type: 'pie',
            data: {
                labels: ['Activos', 'Inactivos'],
                datasets: [{
                    label: 'Estudiantes',
                    data: datos.estudiantes,
                    backgroundColor: ['#007bff', '#dc3545'],
                }]
            }
        });

        // Configuración del gráfico de docentes
        const graficoDocentes = new Chart(document.getElementById('graficoDocentes'), {
            type: 'pie',
            data: {
                labels: ['Activos', 'Inactivos'],
                datasets: [{
                    label: 'Docentes',
                    data: datos.docentes,
                    backgroundColor: ['#28a745', '#ffc107'],
                }]
            }
        });

        // Configuración del gráfico de administradores
        const graficoAdmin = new Chart(document.getElementById('graficoAdmin'), {
            type: 'pie',
            data: {
                labels: ['Total Administradores', 'Ninguno'], // Solo dos etiquetas
                datasets: [{
                    label: 'Administradores',
                    data: datos.administradores,
                    backgroundColor: ['#ff07ff', '#6d6552'], // El segundo color puede ser cualquier cosa
                }]
            }
        });
    } catch (error) {
        console.error('Error al cargar los datos:', error);
    }
}

// Cargar los datos cuando la página esté lista
document.addEventListener('DOMContentLoaded', cargarDatosGraficos);
// Espera a que el DOM esté completamente cargado

