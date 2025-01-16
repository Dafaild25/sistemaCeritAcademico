from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth import logout
from django.contrib import messages
from ..models import Curso,Administrador,PeriodoAcademico,Usuario,Estudiante
from django.core.mail import send_mail
import random
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import re



def registro(request):
    cursos = Curso.objects.all()
    periodos = PeriodoAcademico.objects.all()
    
    user = request.user
    print(f"Usuario autenticado: {user.username}")

    try:
        admin = user.admin  # Intentamos acceder al perfil de admin
        nombre_admin = f' {admin.apellido_Paterno} {admin.apellido_Materno} {admin.primer_nombre} {admin.segundo_nombre}'
        print(f"Perfil de Administrador encontrado: {nombre_admin}")
    except Administrador.DoesNotExist:
        admin = None
        nombre_admin = user.username  # En caso de que no exista perfil de docente
        print("Perfil de Administrador no encontrado.")
    
    context = {
        'nombre_admin': nombre_admin,
        'admin': admin,  # También puedes pasar todo el objeto docente si necesitas más detalles
        'cursos': cursos,
        'periodos':periodos
    }
    print(f"Contexto enviado a la plantilla: {context}")
    
    return render(request, '../templates/Registro/registro.html',context)


def logueo(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = user.username  # Guardar el nombre de usuario en la sesión
            # Redirigir según el tipo de usuario
            if user.tipo_usuario == 'admin':
                return redirect('adminHome')
            elif user.tipo_usuario == 'docente':
                return redirect('docenteHome')
            elif user.tipo_usuario == 'estudiante':
                return redirect('estudianteHome')
        else:
              # Agrega el mensaje de error
              
            messages.error(request, 'Credenciales Invalidas')
            return render(request, '../templates/Login/login.html')  # Asegúrate de que la ruta sea correcta
    return render(request, '../templates/Login/login.html')

def cerrarSesion(request):
    logout(request)
    return redirect('login')




# Validar el formato del correo electrónico
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

# Enviar el código de verificación
# Enviar el código de verificación
def enviar_codigo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        userId = data.get('user_Id')  # ID del usuario que quieres verificar

        # Validar el formato del correo electrónico
        if not is_valid_email(email):
            return JsonResponse({'success': False, 'error': 'El correo electrónico ingresado no es válido.'})

        try:
            # Obtener el usuario
            usuario = Usuario.objects.get(id=userId)

            # Verificar si el correo pertenece a un Administrador
            if hasattr(usuario, 'admin'):
                admin = usuario.admin  # Acceder al administrador relacionado
                if email == admin.email:
                    enviar_codigo_verificacion(email, request)
                    return JsonResponse({'success': True})
            
            # Verificar si el correo pertenece a un Docente
            if hasattr(usuario, 'docente'):
                docente = usuario.docente  # Acceder al docente relacionado
                if email == docente.email:
                    enviar_codigo_verificacion(email, request)
                    return JsonResponse({'success': True})

            # Verificar si el correo pertenece a un Estudiante o sus representantes
            if hasattr(usuario, 'estudiante'):
                estudiante = usuario.estudiante  # Acceder al estudiante relacionado
                if (email == estudiante.email or 
                    email == estudiante.email_R1 or 
                    email == estudiante.email_R2 or 
                    email == estudiante.email_R3):
                    enviar_codigo_verificacion(email, request)
                    return JsonResponse({'success': True})

            return JsonResponse({'success': False, 'error': 'El correo no pertenece al usuario.'})
        
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})  # Muestra el error real para depuración
    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

# Función para enviar el código de verificación
def enviar_codigo_verificacion(email, request):
    # Generar el código de verificación
    verification_code = random.randint(100000, 999999)

    # Guardar el código en la sesión
    request.session['verification_code'] = verification_code
    request.session['email'] = email

    # Enviar el correo con el código de verificación
    send_mail(
        'Código de Verificación',
        f'Tu código de verificación es {verification_code}.',
        'narcisaquintanilla25@gmail.com',  # Correo del remitente
        [email],  # Enviar al correo verificado
        fail_silently=False,
    )


# Verificar el código de verificación
def verificacion_codigo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        verification_code = data.get('verification_code')

        # Verificar si el código coincide con el almacenado en la sesión
        if str(verification_code) == str(request.session.get('verification_code')) and email == request.session.get('email'):
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Código de verificación incorrecto.'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


def buscar_usuario(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')

        try:
            user = Usuario.objects.get(username=username)  # O el campo que estés utilizando para identificar al usuario
            return JsonResponse({'success': True, 'user_id': user.id})  # Puedes devolver el ID u otra información si la necesitas
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


# Cambiar la contraseña
@csrf_exempt
def cambiar_contra(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("userId")
            new_password = data.get("newPassword")

            # Cambiar la contraseña del usuario
            user = Usuario.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()

            # Devolver un mensaje de éxito y campo success
            return JsonResponse({"message": "Contraseña cambiada exitosamente.", "success": True}, status=200)

        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado.", "success": False}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e), "success": False}, status=500)

    return JsonResponse({"error": "Método no permitido.", "success": False}, status=405)
