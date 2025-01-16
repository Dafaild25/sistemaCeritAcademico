// Función para obtener el CSRF token
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

const iconoVerContraseña = document.querySelector("#verContraseña");
const inputContraseña = document.querySelector("#password");

const iconoNuevaContraseña = document.querySelector("#iconoNuevaContraseña");
const inputNuevaContraseña = document.querySelector("#newPassword");

const iconoConfirmarContraseña = document.querySelector("#iconoConfirmarContraseña");
const inputConfirmarContraseña = document.querySelector("#confirmPassword");

iconoVerContraseña.addEventListener("click", function () {
    // Alternar entre el tipo de campo 'password' y 'text'
    const type = inputContraseña.getAttribute("type") === "password" ? "text" : "password";
    inputContraseña.setAttribute("type", type);
    
    // Alternar el icono de ojo
    this.classList.toggle("fa-eye");
    this.classList.toggle("fa-eye-slash");
});

iconoNuevaContraseña.addEventListener("click", function () {
    // Alternar entre el tipo 'password' y 'text' para el campo Nueva Contraseña
    const type = inputNuevaContraseña.getAttribute("type") === "password" ? "text" : "password";
    inputNuevaContraseña.setAttribute("type", type);

    // Alternar icono
    this.classList.toggle("fa-eye");
    this.classList.toggle("fa-eye-slash");
});

iconoConfirmarContraseña.addEventListener("click", function () {
    // Alternar entre el tipo 'password' y 'text' para el campo Confirmar Contraseña
    const type = inputConfirmarContraseña.getAttribute("type") === "password" ? "text" : "password";
    inputConfirmarContraseña.setAttribute("type", type);

    // Alternar icono
    this.classList.toggle("fa-eye");
    this.classList.toggle("fa-eye-slash");
});

// Abrir el modal de verificación de código al hacer clic en el enlace
document.getElementById("boton_cambio_contraseña").addEventListener("click", function(event) {
    event.preventDefault(); // Evitar que el enlace realice su acción predeterminada
    $('#CambiarContraseñaModal').modal('show'); // Mostrar el modal de verificación
});

// Función para reiniciar el modal
function limpiarModal() {
    document.getElementById("usernameBuscar").value = ""; // Limpia el campo de usuario
    document.getElementById("email").value = "";            // Limpia el campo de correo
    document.getElementById("newPassword").value = "";      // Limpia el campo de nueva contraseña
    document.getElementById("confirmPassword").value = "";   // Limpia el campo de confirmar contraseña
    document.getElementById('errorDiv').style.display = 'none'; // Oculta el mensaje de error
    document.getElementById('verificacionCodigoDiv').style.display = 'none'; // Oculta la sección de verificación
    document.getElementById('cambiarContraseñaDiv').style.display = 'none'; // Oculta la sección de cambio de contraseña
    document.getElementById('savePasswordBtn').style.display = 'none'; // Oculta el botón de guardar contraseña
}

// Al cerrar el modal, reiniciar los campos
$('#CambiarContraseñaModal').on('hidden.bs.modal', function () {
    limpiarModal(); // Llama a la función para reiniciar
});

//Cerrar modal cambio de contraseña
function cerrarModalCambioContraseña(){
    $('#CambiarContraseñaModal').modal('hide'); // Usa jQuery para cerrar el modal
}

//Cerrar modal erro autenticacion
function cerrarModalAutenticacion(){
    $('#errorModalAutenticacion').modal('hide'); // Usa jQuery para cerrar el modal
}


// Buscar el usuario por nombre
function buscarUsuario() {
    const username = document.getElementById('usernameBuscar').value;
    const errorMessageDiv = document.getElementById('errorDiv');
    const emailInput = document.getElementById("email");
    const codigoVerificacion = document.getElementById("codigoVerificacion");

    errorMessageDiv.style.display = 'none'; // Ocultar mensaje de error
    emailInput.value = ''; // Limpiar el campo de correo
    codigoVerificacion.value = '';

    fetch('../buscar_usuario/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('verificacionCodigoDiv').style.display = 'block'; // Mostrar campo de correo
            document.getElementById('boton_enviar_codigo').style.display = 'block'; // Mostrar botón enviar código
            document.getElementById('cambiarContraseñaDiv').style.display = 'none';
            document.getElementById('savePasswordBtn').style.display = 'none';
            document.getElementById('userId').value = data.user_id; // Guardar el ID del usuario

        } else {
            document.getElementById('errorMessage').innerText = data.error || 'Usuario no encontrado.';
            document.getElementById('verificacionCodigoDiv').style.display = 'none';
            document.getElementById('cambiarContraseñaDiv').style.display = 'none';
            document.getElementById('savePasswordBtn').style.display = 'none';
            errorMessageDiv.style.display = 'block'; // Mostrar mensaje de error
        }
    })
    .catch(error => console.error('Error:', error));
}

// Enviar código de verificación al correo
function enviarCodigoEmail() {
    const user_Id = document.getElementById("userId").value;
    const email = document.getElementById("email").value;

    // Validar que el campo de correo electrónico no esté vacío
    if (!email) {
        alert("Por favor, ingrese un correo electrónico.");
        return;
    }

    fetch('../enviar_codigo/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ 
            email: email,
            user_Id: user_Id 

        }),
        
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            document.getElementById('boton_enviar_codigo').style.display = 'none'; // Ocultar botón
            alert("Se ha enviado un código de verificación a su correo electrónico.");
            document.getElementById('verificationInputContainer').style.display = 'block'; // Mostrar input para el código
            document.getElementById('boton_verificar_codigo').style.display = 'block'; // Mostrar botón verificar código
        } else {
            alert(data.error); // Mostrar el error devuelto por el servidor
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Ocurrió un error al enviar el código de verificación. Por favor, inténtelo de nuevo más tarde.");
    });
}

// Verificar el código de verificación
function verificarCodigo() {
    const email = document.getElementById("email").value;
    const verificationCode = document.getElementById("codigoVerificacion").value;

    fetch('../verificacion_codigo/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            email: email,
            verification_code: verificationCode,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('verificacionCodigoDiv').style.display = 'none'; // Ocultar
            document.getElementById('verificationInputContainer').style.display = 'none'; // Ocultar input
            document.getElementById('boton_verificar_codigo').style.display = 'none'; // Ocultar botón
            document.getElementById('cambiarContraseñaDiv').style.display = 'block'; // Mostrar sección de cambio de contraseña
            document.getElementById('greeting').innerText = `Ingresa tu nueva contraseña:`; // Mensaje
            document.getElementById('savePasswordBtn').style.display = 'block'; // Mostrar botón guardar contraseña
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Cambiar la contraseña
function cambiarContra() {
    const userId = document.getElementById("userId").value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    console.log("ID del usuario:", userId); // Agregué más logs para depuración

    // Verificar que las contraseñas coincidan
    if (newPassword !== confirmPassword) {
        alert("Las contraseñas no coinciden.");
        return;
    }

    // Hacer la solicitud POST al servidor
    fetch('../cambiar_contra/', {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // Asegúrate de que sea JSON
            "X-CSRFToken": getCookie('csrftoken') // Incluye el token CSRF si es necesario
        },
        body: JSON.stringify({
            userId: userId, // Asegúrate de que este valor esté correcto
            newPassword: newPassword
        })
    })
    .then(response => response.json()) // Convertir la respuesta a JSON
    .then(data => {
        console.log("Respuesta del servidor:", data); // Agrega logs para ver la respuesta en la consola
        if (data.success) {
            alert(data.message || "Contraseña cambiada exitosamente.");
            limpiarModal(); // Limpia los campos del modal
            $('#CambiarContraseñaModal').modal('hide'); // Cierra el modal
        } else {
            alert(data.error || "Ocurrió un error al cambiar la contraseña.");
        }
    })
    .catch(error => {
        console.error("Error al cambiar la contraseña:", error);
        alert("Ocurrió un error: " + error.message);
    });
}

