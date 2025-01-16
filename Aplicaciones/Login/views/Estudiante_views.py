import json

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from ..models import Usuario, Estudiante,Administrador,Docente
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings  # Asegúrate de importar settings

@login_required
def estudianteHome(request):
    user = request.user
    print(f"Usuario autenticado: {user.username}")

    try:
        estudiante = user.estudiante  # Intentamos acceder al perfil de estudiante
        nombre_estudiante = f'{estudiante.apellido_Paterno} {estudiante.apellido_Materno} {estudiante.primer_nombre} {estudiante.segundo_nombre}'
        print(f"Perfil de Estudiante encontrado: {nombre_estudiante}")
    except Estudiante.DoesNotExist:
        nombre_estudiante = user.username  # En caso de que no exista perfil de estudiante
        print("Perfil de Estudiante no encontrado.")
    
    context = {
        'nombre_estudiante': nombre_estudiante,
        'estudiante': estudiante,  # También puedes pasar todo el objeto estudiante si necesitas más detalles
    }
    print(f"Contexto enviado a la plantilla: {context}")
    return render(request, '../templates/Estudiante/estudianteHome.html', context)



def registroEstudiante(request):
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Extraer datos del JSON
            cedula = str(data.get('cedula_estudiante', '')).strip()
            primer_nombre = str(data.get('primer_nombre_estudiante', '')).strip()
            segundo_nombre = str(data.get('segundo_nombre_estudiante', '')).strip()
            apellido_Paterno = str(data.get('apellido_Paterno_estudiante', '')).strip()
            apellido_Materno = str(data.get('apellido_Materno_estudiante', '')).strip()
            fecha_nacimiento = data.get('fecha_nacimiento_estudiante')
            telefono = str(data.get('telefono_estudiante', '')).strip()
            ciudad = str(data.get('ciudad_estudiante', '')).strip()
            direccion = str(data.get('direccion_estudiante', '')).strip()
            email = str(data.get('email_estudiante', '')).strip() if str(data.get('email_estudiante', '')).strip() else None
            estado = str(data.get('estado_estudiante', '')).strip()
            tipo_usuario = str(data.get('usuarioEstudiante', '')).strip()

            # Datos de los representantes (opcional)
            cedula_R1 = str(data.get('cedula_R1', '')).strip() or None
            nombres_R1 = str(data.get('nombres_R1', '')).strip() or None
            apellido_paterno_R1 = str(data.get('apellido_Paterno_R1', '')).strip() or None
            apellido_materno_R1 = str(data.get('apellido_Materno_R1', '')).strip() or None
            celular_R1 = str(data.get('celular_R1', '')).strip() or None
            email_R1 = str(data.get('email_R1', '')).strip() or None
            estado_R1 = str(data.get('estado_R1', '')).strip() or None
            parentesco_R1 = str(data.get('parentesco_R1', '')).strip() or None

            cedula_R2 = str(data.get('cedula_R2', '')).strip() or None
            nombres_R2 = str(data.get('nombres_R2', '')).strip() or None
            apellido_paterno_R2 = str(data.get('apellido_Paterno_R2', '')).strip() or None
            apellido_materno_R2 = str(data.get('apellido_Materno_R2', '')).strip() or None
            celular_R2 = str(data.get('celular_R2', '')).strip() or None
            email_R2 = str(data.get('email_R2', '')).strip() or None
            estado_R2 = str(data.get('estado_R2', '')).strip() or None
            parentesco_R2 = str(data.get('parentesco_R2', '')).strip() or None

            cedula_R3 = str(data.get('cedula_R3', '')).strip() or None
            nombres_R3 = str(data.get('nombres_R3', '')).strip() or None
            apellido_paterno_R3 = str(data.get('apellido_Paterno_R3', '')).strip() or None
            apellido_materno_R3 = str(data.get('apellido_Materno_R3', '')).strip() or None
            celular_R3 = str(data.get('celular_R3', '')).strip() or None
            email_R3 = str(data.get('email_R3', '')).strip() or None
            estado_R3 = str(data.get('estado_R3', '')).strip() or None
            parentesco_R3 = str(data.get('parentesco_R3', '')).strip() or None

            # Validaciones
            if not cedula or not primer_nombre or not segundo_nombre or not apellido_Paterno or not apellido_Materno or not telefono or not fecha_nacimiento  or not direccion or not email or not tipo_usuario:
                return JsonResponse({'success': False, 'error': "Todos los campos son obligatorios"}, status=400)

            if len(cedula) != 10 or not cedula.isdigit():
                return JsonResponse({'success': False, 'error': "La cédula debe tener exactamente 10 dígitos numéricos"}, status=400)

            if len(telefono) != 10 or not telefono.isdigit():
                return JsonResponse({'success': False, 'error': "El teléfono debe tener exactamente 10 dígitos numéricos"}, status=400)


            # Validaciones básicas
            if not cedula:
                return JsonResponse({"success": False, "error": "El campo 'cedula' es obligatorio"}, status=400)

            if Usuario.objects.filter(username=cedula).exists():
                return JsonResponse({"success": False, "error": "El nombre de usuario ya está en uso"}, status=400)

            # Crear el usuario
            username = cedula
            password = cedula

            user = Usuario.objects.create_user(username=username, tipo_usuario=tipo_usuario, password=password)
            user.save()

            # Verificar tipo de usuario y crear perfil de estudiante
            if tipo_usuario == 'estudiante':
                try:
                    estudiante = Estudiante.objects.create(
                        usuario=user,
                        cedula=cedula,
                        primer_nombre=primer_nombre,
                        segundo_nombre=segundo_nombre,
                        apellido_Paterno=apellido_Paterno,
                        apellido_Materno=apellido_Materno,
                        fecha_nacimiento=fecha_nacimiento,
                        telefono=telefono,
                        ciudad=ciudad,
                        direccion=direccion,
                        email=email,
                        estado=estado,
                        cedula_R1=cedula_R1,
                        nombres_R1=nombres_R1,
                        apellido_paterno_R1=apellido_paterno_R1,
                        apellido_materno_R1=apellido_materno_R1,
                        celular_R1=celular_R1,
                        email_R1=email_R1,
                        estado_R1=estado_R1,
                        parentesco_R1=parentesco_R1,
                        cedula_R2=cedula_R2,
                        nombres_R2=nombres_R2,
                        apellido_paterno_R2=apellido_paterno_R2,
                        apellido_materno_R2=apellido_materno_R2,
                        celular_R2=celular_R2,
                        email_R2=email_R2,
                        estado_R2=estado_R2,
                        parentesco_R2=parentesco_R2,
                        cedula_R3=cedula_R3,
                        nombres_R3=nombres_R3,
                        apellido_paterno_R3=apellido_paterno_R3,
                        apellido_materno_R3=apellido_materno_R3,
                        celular_R3=celular_R3,
                        email_R3=email_R3,
                        estado_R3=estado_R3,
                        parentesco_R3=parentesco_R3
                    )
                    print(f"Perfil de Estudiante creado: {estudiante}")
                    return JsonResponse({'success': True})

                except Exception as e:
                    print(f"Error al crear el perfil de estudiante: {e}")
                    user.delete()  # Elimina el usuario si falla la creación del perfil
                    return JsonResponse({'success': False, 'error': f"Error al crear el perfil de estudiante: {str(e)}"}, status=500)

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Error al decodificar JSON'}, status=400)
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            print(f"Excepción capturada: {e}")
            return JsonResponse({'success': False, 'error': f"Error al crear el usuario: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'error': "Método no permitido"}, status=405)


        

# aqui lista los docentes
def listadoEstudiantes(request):
    estudiantes = Estudiante.objects.all().order_by('apellido_Paterno', 'primer_nombre')  # Obtener todos los docentes
    
    context = {
        'estudiantes': estudiantes
    }
    return render(request, '../templates/Administrador/listadoEstudiantes.html', context)


@receiver(post_delete, sender=Estudiante)
def eliminar_usuario_asociado(sender, instance, **kwargs):
    # Verifica si el usuario existe antes de intentar eliminarlo
    if instance.usuario:
        instance.usuario.delete()

def eliminarEstudiante(request, id):
    print(f'ID recibido para eliminación: {id}')  # Añadir para depuración
    if request.method == 'DELETE':
        try:
            estudiante = Estudiante.objects.get(id=id)
            usuario = estudiante.usuario
            estudiante.delete()
           
            # Puedes agregar lógica adicional aquí si es necesario, como verificar otras condiciones
            
            return JsonResponse({
                'estado': True,
                'mensaje': 'Estudiante eliminado exitosamente.'
            }, status=200)
        except Estudiante.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Estudiante no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    
@login_required
def editarEstudiante(request):
    user = request.user
    print(f"Usuario autenticado: {user.username}")

    try:
        admin = user.admin  # Intentamos acceder al perfil del admin
        nombre_admin = f' {admin.apellido_Paterno} {admin.apellido_Materno} {admin.primer_nombre} {admin.segundo_nombre}'
        print(f"Perfil de Administrador encontrado: {nombre_admin}")
    except Administrador.DoesNotExist:
        admin = None
        nombre_admin = user.username  # En caso de que no exista perfil de docente
        print("Perfil de Administrador no encontrado.")
    
    context = {
        'nombre_admin': nombre_admin,
        'admin': admin,  # También puedes pasar todo el objeto docente si necesitas más detalles
    }
    print(f"Contexto enviado a la plantilla: {context}")
    return render(request, '../templates/Administrador/editarEstudiante.html', context)

def obtenerEstudiante(request, id):
    try:
        estudiante = Estudiante.objects.get(id=id)
        data = {
            "id": estudiante.id, #aqui solo creo variables
            "cedula": estudiante.cedula,
            "usuario": estudiante.usuario.username if estudiante.usuario else "No asignado",
            "primer_nombre": estudiante.primer_nombre,
            "segundo_nombre": estudiante.segundo_nombre,
            "apellido_Paterno": estudiante.apellido_Paterno,
            "apellido_Materno":estudiante.apellido_Materno,
            "telefono": estudiante.telefono,
            "email": estudiante.email,
            "fecha_nacimiento": estudiante.fecha_nacimiento,
            "estado": estudiante.estado,
            "ciudad": estudiante.ciudad,
            "direccion": estudiante.direccion,


            #DATOS DE LOS REPRESETANTES
            "cedula_R1": estudiante.cedula_R1,
            "nombres_R1": estudiante.nombres_R1,
            "apellido_paterno_R1": estudiante.apellido_paterno_R1,
            "apellido_materno_R1": estudiante.apellido_materno_R1,
            "celular_R1": estudiante.celular_R1,
            "email_R1": estudiante.email_R1,
            "estado_R1": estudiante.estado_R1,
            "parentesco_R1": estudiante.parentesco_R1,

            #REPRESENTANTE 2
            "cedula_R2": estudiante.cedula_R2,
            "nombres_R2": estudiante.nombres_R2,
            "apellido_paterno_R2": estudiante.apellido_paterno_R2,
            "apellido_materno_R2": estudiante.apellido_materno_R2,
            "celular_R2": estudiante.celular_R2,
            "email_R2": estudiante.email_R2,
            "estado_R2": estudiante.estado_R2,
            "parentesco_R2": estudiante.parentesco_R2,

            #REPRESENTANTE 3
            "cedula_R3": estudiante.cedula_R3,
            "nombres_R3": estudiante.nombres_R3,
            "apellido_paterno_R3": estudiante.apellido_paterno_R3,
            "apellido_materno_R3": estudiante.apellido_materno_R3,
            "celular_R3": estudiante.celular_R3,
            "email_R3": estudiante.email_R3,
            "estado_R3": estudiante.estado_R3,
            "parentesco_R3": estudiante.parentesco_R3,
           
        }
        return JsonResponse(data)
    except Estudiante.DoesNotExist:
        return JsonResponse({"error": "Estudiante no encontrado"}, status=404)




@csrf_exempt
def actualizarEstudiante(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            estudiante = Estudiante.objects.get(id=id)

            # Validar que la nueva cédula no exista ya en otro estudiante
            nueva_cedula = data.get('cedula', estudiante.cedula)
            if (
                Estudiante.objects.filter(cedula=nueva_cedula).exclude(id=estudiante.id).exists() or
                Docente.objects.filter(cedula=nueva_cedula).exists() or
                Administrador.objects.filter(cedula=nueva_cedula).exists()
            ):
                return JsonResponse({"error": "La cédula ya está en uso "}, status=400)

            # Actualizar datos del estudiante
            estudiante.cedula = nueva_cedula
            estudiante.primer_nombre = data.get('primer_nombre', estudiante.primer_nombre)
            estudiante.segundo_nombre = data.get('segundo_nombre', estudiante.segundo_nombre)
            estudiante.apellido_Paterno = data.get('apellido_Paterno', estudiante.apellido_Paterno)
            estudiante.apellido_Materno = data.get('apellido_Materno', estudiante.apellido_Materno)    
            estudiante.telefono = data.get('telefono', estudiante.telefono)
            estudiante.email = data.get('email', estudiante.email)
            estudiante.estado = data.get('estado', estudiante.estado)
            estudiante.ciudad = data.get('ciudad', estudiante.ciudad)
            estudiante.direccion = data.get('direccion', estudiante.direccion)
            estudiante.fecha_nacimiento = data.get('fecha_nacimiento', estudiante.fecha_nacimiento)

            # Actualizar representantes
            estudiante.cedula_R1 = data.get('cedula_R1', estudiante.cedula_R1)
            estudiante.nombres_R1 = data.get('nombres_R1', estudiante.nombres_R1)
            estudiante.apellido_paterno_R1 = data.get('apellido_paterno_R1', estudiante.apellido_paterno_R1)
            estudiante.apellido_materno_R1 = data.get('apellido_materno_R1', estudiante.apellido_materno_R1)
            estudiante.celular_R1 = data.get('celular_R1', estudiante.celular_R1)
            estudiante.email_R1 = data.get('email_R1', estudiante.email_R1)
            estudiante.estado_R1 = data.get('estado_R1', estudiante.estado_R1)
            estudiante.parentesco_R1 = data.get('parentesco_R1', estudiante.parentesco_R1)

            estudiante.cedula_R2 = data.get('cedula_R2', estudiante.cedula_R2)
            estudiante.nombres_R2 = data.get('nombres_R2', estudiante.nombres_R2)
            estudiante.apellido_paterno_R2 = data.get('apellido_paterno_R2', estudiante.apellido_paterno_R2)
            estudiante.apellido_materno_R2 = data.get('apellido_materno_R2', estudiante.apellido_materno_R2)
            estudiante.celular_R2 = data.get('celular_R2', estudiante.celular_R2)
            estudiante.email_R2 = data.get('email_R2', estudiante.email_R2)
            estudiante.estado_R2 = data.get('estado_R2', estudiante.estado_R2)
            estudiante.parentesco_R2 = data.get('parentesco_R2', estudiante.parentesco_R2)

            estudiante.cedula_R3 = data.get('cedula_R3', estudiante.cedula_R3)
            estudiante.nombres_R3 = data.get('nombres_R3', estudiante.nombres_R3)
            estudiante.apellido_paterno_R3 = data.get('apellido_paterno_R3', estudiante.apellido_paterno_R3)
            estudiante.apellido_materno_R3 = data.get('apellido_materno_R3', estudiante.apellido_materno_R3)
            estudiante.celular_R3 = data.get('celular_R3', estudiante.celular_R3)
            estudiante.email_R3 = data.get('email_R3', estudiante.email_R3)
            estudiante.estado_R3 = data.get('estado_R3', estudiante.estado_R3)
            estudiante.parentesco_R3 = data.get('parentesco_R3', estudiante.parentesco_R3)

            estudiante.save()

            # Actualizar datos del usuario asociado (si existe)
            usuario = estudiante.usuario
            if usuario:
                usuario.username = data.get('username', usuario.username)  # Actualizar el nombre de usuario si se proporciona
                new_password = data.get('password')
                if new_password:
                    usuario.set_password(new_password)
                usuario.save()
            
            return JsonResponse({"message": "Estudiante y usuario actualizados correctamente"})
        except Estudiante.DoesNotExist:
            return JsonResponse({"error": "Estudiante no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

