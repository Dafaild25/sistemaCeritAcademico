from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from ..models import Usuario,Docente,PeriodoAcademico,CursoAsignatura,Estudiante,Curso,TipoEvaluacion,Calificacion,PeriodoDivision,Administrador
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required



def registroDocente(request):
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la solicitud
            data = json.loads(request.body)
            cedula = data.get('cedula_docente')
            primer_nombre = data.get('primer_nombre_docente')
            segundo_nombre = data.get('segundo_nombre_docente')
            apellido_Paterno = data.get('apellido_Paterno_docente')
            apellido_Materno = data.get('apellido_Materno_docente')
            telefono = data.get('telefono_docente')
            direccion = data.get('direccion_docente')
            email = data.get('email_docente')
            especialidad = data.get('especialidad_docente')
            estado = data.get('estado_docente')
            tipo_usuario = data.get('usuarioDocente')

             # Validaciones
            if not cedula or not primer_nombre or not segundo_nombre or not apellido_Paterno or not apellido_Materno or not telefono or not direccion or not email or not tipo_usuario:
                return JsonResponse({'success': False, 'error': "Todos los campos son obligatorios"}, status=400)

            if len(cedula) != 10 or not cedula.isdigit():
                return JsonResponse({'success': False, 'error': "La cédula debe tener exactamente 10 dígitos numéricos"}, status=400)

            if len(telefono) != 10 or not telefono.isdigit():
                return JsonResponse({'success': False, 'error': "El teléfono debe tener exactamente 10 dígitos numéricos"}, status=400)

            if Usuario.objects.filter(username=cedula).exists():
                return JsonResponse({'success': False, 'error': "El nombre de usuario ya está en uso"}, status=400)
       

            
            # Crear el usuario
            password = cedula  # La contraseña es igual a la cédula
            user = Usuario.objects.create_user(username=cedula, tipo_usuario=tipo_usuario, password=password)
            user.save()
            

            # Si el tipo de usuario es 'docente', creamos el perfil de Docente
            if tipo_usuario == 'docente':
                docente = Docente.objects.create(
                    usuario=user,
                    cedula=cedula,
                    primer_nombre=primer_nombre,
                    segundo_nombre=segundo_nombre,
                    apellido_Paterno=apellido_Paterno,
                    apellido_Materno=apellido_Materno,
                    especialidad=especialidad,
                    telefono=telefono,
                    direccion=direccion,
                    email=email,
                    estado=estado
                )
                print(f"Perfil de Docente creado: {docente}")

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Error al decodificar JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Error al crear el usuario: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)




# aqui lista los estudiantes por curso 
def EstudiantesPorCurso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes = Estudiante.objects.filter(curso=curso).order_by('apellido_Paterno', 'apellido_Materno', 'primer_nombre', 'segundo_nombre')

    context = {
        'estudiantes': estudiantes,
        'curso': curso
    }
    return render(request, '../templates/Docente/listadoEstudiantesCurso.html', context)

# aqui lista los docentes
def listadoDocentes(request):
    docentes = Docente.objects.all()  # Obtener todos los docentes
    
    context = {
        'docentes': docentes
    }
    return render(request, '../templates/Administrador/listadoDocente.html', context)

def obtenerDocente(request, id):
    try:
        docente = Docente.objects.get(id=id)
        data = {
            "id": docente.id, #aqui solo creo variables
            "cedula": docente.cedula,
            "usuario": docente.usuario.username if docente.usuario else "No asignado",
            "primer_nombre": docente.primer_nombre,
            "segundo_nombre": docente.segundo_nombre,
            "apellido_Paterno": docente.apellido_Paterno,
            "apellido_Materno": docente.apellido_Materno,
            "especialidad": docente.especialidad,
            "telefono": docente.telefono,
            "direccion": docente.direccion,
            "email": docente.email,
            "estado": docente.estado
           
        }
        return JsonResponse(data)
    except Docente.DoesNotExist:
        return JsonResponse({"error": "Docente no encontrado"}, status=404)

@csrf_exempt
def actualizarDocente(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            docente = Docente.objects.get(id=id)

            # Validar que la nueva cédula no exista ya en otro docente
            nueva_cedula = data.get('cedula', docente.cedula)
            if (
                Docente.objects.filter(cedula=nueva_cedula).exclude(id=docente.id).exists() or
                Estudiante.objects.filter(cedula=nueva_cedula).exists() or
                Administrador.objects.filter(cedula=nueva_cedula).exists()
            ):
                return JsonResponse({"error": "La cédula ya está en uso por otro docente"}, status=400)

            # Actualizar datos del docente
            docente.cedula = nueva_cedula
            docente.primer_nombre = data.get ('primer_nombre',docente.primer_nombre) 
            docente.segundo_nombre = data.get ('segundo_nombre',docente.segundo_nombre)    
            docente.apellido_Paterno = data.get ('apellido_Paterno',docente.apellido_Paterno) 
            docente.apellido_Materno = data.get ('apellido_Materno',docente.apellido_Materno) 
            docente.especialidad = data.get('especialidad', docente.especialidad)
            docente.telefono = data.get('telefono', docente.telefono)
            docente.direccion = data.get ('direccion',docente.direccion) 
            docente.email = data.get('email', docente.email)
            docente.estado = data.get('estado', docente.estado)
            docente.save()
            # Actualizar datos del usuario asociado (si existe)
            usuario = docente.usuario
            if usuario:
                usuario.username = data.get('username', usuario.username)  # Actualizar el nombre de usuario si se proporciona
                new_password = data.get('password')
                if new_password:
                    usuario.set_password(new_password)
                
                usuario.save()
            
            
            
            return JsonResponse({"message": "Docente y usuario actualizados correctamente"})
        except Docente.DoesNotExist:
            return JsonResponse({"error": "Docente no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)


@receiver(post_delete, sender=Docente)
def eliminar_usuario_asociado(sender, instance, **kwargs):
    # Verifica si el usuario existe antes de intentar eliminarlo
    if instance.usuario:
        instance.usuario.delete()


def eliminarDocente(request, id):
    print(f'ID recibido para eliminación: {id}')  # Añadir para depuración
    if request.method == 'DELETE':
        try:
            docente = Docente.objects.get(id=id)
            usuario = docente.usuario
            docente.delete()
           
            # Puedes agregar lógica adicional aquí si es necesario, como verificar otras condiciones
            
            return JsonResponse({
                'estado': True,
                'mensaje': 'Docente eliminado exitosamente.'
            }, status=200)
        except Docente.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Docente no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    


