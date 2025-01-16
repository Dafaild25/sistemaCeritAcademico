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

document.addEventListener('DOMContentLoaded', () => {
    cargarDatosInstitucion();  
});

function cargarDatosInstitucion() {
    fetch('obtenerEscuela/', { method: 'GET' })  // Realizamos la solicitud GET
        .then(respuesta => respuesta.json())    // Parseamos la respuesta como JSON
        .then(datos => {
            if (datos.success) {
                // Si la respuesta es exitosa, completamos los campos con los datos recibidos
                const { nombre, direccion, telefono, email, rector, fundacion, vision, mision, logo_url } = datos.data;

                document.getElementById('nombreInstitucion').value = nombre || '';
                document.getElementById('direccionInstitucion').value = direccion || '';
                document.getElementById('telefonoInstitucion').value = telefono || '';
                document.getElementById('emailInstitucion').value = email || '';
                document.getElementById('rectorInstitucion').value = rector || '';
                document.getElementById('fundacionInstitucion').value = fundacion || '';
                document.getElementById('visionInstitucion').value = vision || '';
                document.getElementById('misionInstitucion').value = mision || '';

                // Si existe un logo, lo mostramos
                if (logo_url) {
                    const logoPreview = document.getElementById('logoPreview');
                    logoPreview.src = logo_url;
                    logoPreview.style.display = 'block';  // Hacer visible el logo
                }
            } else {
                // Si la respuesta no es exitosa, mostramos un error en consola
                console.error(datos.error || 'Error al cargar los datos de la institución');
            }
        })
        .catch(error => {
            // Si ocurre un error en la solicitud, mostramos un mensaje en consola
            console.error('Error al realizar la solicitud GET:', error);
        });
}

let editando = false;  // Variable para determinar si está en modo edición

// Función para habilitar los inputs y cambiar color del botón
const habilitarEdicion = (event) => {
    event.preventDefault();  // Prevenir el envío del formulario

    const inputs = document.querySelectorAll('input, textarea');  // Selecciona todos los inputs y textareas
    const botonEditarGuardar = document.getElementById('editSaveButton');  // Botón de Editar/Guardar

    if (editando) {
        // Guardar los datos
        guardarDatosInstitucion();
        

        // Cambiar el color del botón a su estado original
        botonEditarGuardar.style.backgroundColor = '';  // Color original
        botonEditarGuardar.style.color = '';  // Color de texto original

        // Deshabilitar los inputs
        inputs.forEach(input => {
            input.disabled = true;  // Cambiar el atributo disabled a true
        });

        botonEditarGuardar.textContent = 'Editar';  // Cambiar el texto del botón
    } else {
        // Habilitar los inputs
        inputs.forEach(input => {
            input.disabled = false;  // Cambiar el atributo disabled a false
        });

        // Cambiar el color del botón a verde
        botonEditarGuardar.style.backgroundColor = 'green';
        botonEditarGuardar.style.color = 'white';  // Cambiar el color del texto a blanco para mejorar la visibilidad

        botonEditarGuardar.textContent = 'Guardar';  // Cambiar el texto del botón
    }

    // Cambiar el estado de edición
    editando = !editando;  // Alternar entre habilitar y guardar
};

// Función para guardar los datos
const guardarDatosInstitucion = () => {
    const formData = new FormData();
    formData.append('nombre', document.getElementById('nombreInstitucion').value);
    formData.append('direccion', document.getElementById('direccionInstitucion').value);
    formData.append('telefono', document.getElementById('telefonoInstitucion').value);
    formData.append('email', document.getElementById('emailInstitucion').value);
    formData.append('rector', document.getElementById('rectorInstitucion').value);
    formData.append('fundacion', document.getElementById('fundacionInstitucion').value);
    formData.append('vision', document.getElementById('visionInstitucion').value);
    formData.append('mision', document.getElementById('misionInstitucion').value);

    // Obtener el archivo de logo (imagen)
    const logoInput = document.getElementById('logoInstitucion');
    if (logoInput.files.length > 0) {
        formData.append('logo', logoInput.files[0]);
    }
    
    // Realizar la solicitud con fetch
    fetch('registrarEscuela/', {
        method: 'POST',
        body: formData,  // Enviar los datos del formulario
        headers: {
            'X-CSRFToken': getCookie('csrftoken')  // Asegurarse de incluir el token CSRF
        }
    })
    .then(response => response.json())  // Suponiendo que el servidor responde con JSON
    .then(data => {
        
        if (data.success) {
            alert("Los datos de la institución han sido guardados.");code 
            // Actualiza los datos en el formulario
            cargarDatosInstitucion();
        } else {
            console.error("Error al guardar los datos:", data.message);
        }
    })
    .catch(error => {
        console.error("Error al guardar los datos:", error);
    });
};


document.getElementById('editSaveButton').addEventListener('click', habilitarEdicion);


// Función para mostrar la vista previa del logo
function mostrarVistaPrevia(event) {
    const logoInput = event.target;
    const logoPreview = document.getElementById('logoPreview');

    // Si se seleccionó un archivo, mostramos la vista previa
    if (logoInput.files && logoInput.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            logoPreview.src = e.target.result;
            logoPreview.style.display = 'block'; // Mostrar la imagen
        };

        reader.readAsDataURL(logoInput.files[0]);
    }
}


const actualizarCamposFormulario = (datos) => {
    const { nombre, direccion, telefono, email, rector, fundacion, vision, mision, logo_url } = datos;

    document.getElementById('nombreInstitucion').value = nombre || '';
    document.getElementById('direccionInstitucion').value = direccion || '';
    document.getElementById('telefonoInstitucion').value = telefono || '';
    document.getElementById('emailInstitucion').value = email || '';
    document.getElementById('rectorInstitucion').value = rector || '';
    document.getElementById('fundacionInstitucion').value = fundacion || '';
    document.getElementById('visionInstitucion').value = vision || '';
    document.getElementById('misionInstitucion').value = mision || '';

    // Si existe un logo, lo mostramos
    if (logo_url) {
        const logoPreview = document.getElementById('logoPreview');
        logoPreview.src = logo_url;
        logoPreview.style.display = 'block';  // Hacer visible el logo
    }
};