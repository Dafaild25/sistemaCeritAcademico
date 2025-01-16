from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
import json
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from ..models import PeriodoAcademico,Curso,Administrador,Matricula,Estudiante,Docente,CursoAsignatura
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings  # Asegúrate de importar settings
#from django.contrib.auth import login,authenticate

# Obtener correos válidos excluyendo 'NaN'
def obtener_emails_validos(*emails):
    # Filtrar solo correos que no son None o vacíos
    return [email for email in emails if email and email != 'nan']

def adminCurso (request):
    
    cursos = Curso.objects.all()
    matriculas = Matricula.objects.all()
    user = request.user
    print(f"Usuario autenticado: {user.username}")

    try:
        admin = user.admin  # Intentamos acceder al perfil de docente
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
        'matricula': matriculas
    }
    print(f"Contexto enviado a la plantilla: {context}")
    
    return render (request,'../templates/Matricula/adminCurso.html',context)


# Necesito listar los periodos academicos para ver los cursos que tengo ahi 
def listarPeriodosAcademicos(request):
    # Filtra los periodos académicos que tienen el estado "ACTIVO"
    periodos = list(PeriodoAcademico.objects.filter(estado='ACTIVO').values())
    if(len(periodos)>0 ):
        data={
            'message': "okey",
            'periodos':periodos,
        }
    else:
        data={
            'message':"no hay datos"
        }  
    return JsonResponse(data)

# Necesito listar aqui los cursos pero una ves selecionado el periodo
def listarCursosPeriodo(request,periodo_id):   
    cursos=list(Curso.objects.filter(periodoAcademico_id=periodo_id).values())
    return render(request,"../templates/Matricula/listarCursosPeriodo.html",{'cursos': cursos})

def listarEstudiantes(request):
    curso_id = request.GET.get('curso_id')  # Obteniendo curso_id del parámetro de consulta
    if not curso_id:
        return JsonResponse({'success': False, 'error': 'ID de curso no proporcionado'}, status=400)

    

    curso = get_object_or_404(Curso, id=curso_id)
    
    matriculas = Matricula.objects.filter(curso_id=curso)
    estudiantes = matriculas.values_list('estudiante_id', flat=True)
    estudiantes = Estudiante.objects.filter(id__in=estudiantes).order_by('apellido_Paterno', 'primer_nombre')

    return render(request, "../templates/Matricula/matriculasEstudiantes.html", {'estudiantes': estudiantes, 'curso': curso})



@login_required
def datosEstudiantes(request):
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
    return render(request, '../templates/Matricula/datosEstudiantes.html', context)


@csrf_exempt
def actualizarDatosEstudiante(request, id):
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


def eliminarMatricula(request, id):
    print(f'ID recibido para eliminación de matrícula: {id}')  # Añadir para depuración
    if request.method == 'DELETE':
        
        try:
            # Obtener la matrícula por ID
            matricula = Matricula.objects.get(id=id)
            
            # Eliminar la matrícula
            matricula.delete()
            
            # Retornar una respuesta exitosa
            return JsonResponse({
                'estado': True,
                'mensaje': 'Matrícula eliminada exitosamente.'
            }, status=200)
            
        except Matricula.DoesNotExist:
            # Retornar una respuesta si la matrícula no existe
            return JsonResponse({'estado': False, 'mensaje': 'Matrícula no encontrada.'}, status=404)
            
        except Exception as e:
            # Capturar cualquier otra excepción y retornar un mensaje de error del servidor
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
            
    else:
        # Retornar una respuesta si el método HTTP no es DELETE
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    


#Necesito cargar los estudiantes en el select para la matricula individual
def cargarEstudiantes_MatriculaIndividual(request):
    estudiantes = Estudiante.objects.all().values('id', 'cedula',  'apellido_Paterno', 'apellido_Materno' ,'primer_nombre', 'segundo_nombre').order_by('apellido_Paterno', 'primer_nombre')
    estudiantes_list = list(estudiantes)
    return JsonResponse(estudiantes_list, safe=False)


@csrf_exempt
def matriculaIndividual(request):
    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante')
        estado = request.POST.get('estado_matricula')
        curso_id = request.POST.get('curso_id')

        if not estudiante_id or not estado or not curso_id:
            return JsonResponse({'success': False, 'message': 'Datos incompletos.'})

        try:
            estudiante = Estudiante.objects.get(id=estudiante_id)
            curso = Curso.objects.get(id=curso_id)

            # Verificar si el estudiante ya está matriculado en otro curso
            if Matricula.objects.filter(estudiante_id=estudiante).exists():
                return JsonResponse({'success': False, 'message': 'El estudiante ya está matriculado en otro curso.'})

            # Crear o actualizar el registro de matrícula
            matricula, created = Matricula.objects.get_or_create(
                estudiante_id=estudiante,
                curso_id=curso,
                defaults={'estado': estado}
            )

            # Actualizar el estado si el registro ya existía
            if not created:
                matricula.estado = estado
                matricula.save()

            
            # Obtener las asignaturas del curso y el docente que las imparte
            asignaturas_docentes = CursoAsignatura.objects.filter(curso_id=curso).select_related('asignatura_id', 'docente_id')
            lista_asignaturas_docentes = [
                {
                    'asignatura': asignatura_docente.asignatura_id.nombre,
                    'docente': f"{asignatura_docente.docente_id.primer_nombre} {asignatura_docente.docente_id.apellido_Paterno}"
                }
                for asignatura_docente in asignaturas_docentes
            ]

            # Imprimir para depuración
            print("Lista de asignaturas y docentes:", lista_asignaturas_docentes)

            # Extraer los emails y el estado de "enviado"
            emails = {
                'estudiante': {'email': estudiante.email, 'enviado': estudiante.email_enviado},
                'representante_1': {'email': estudiante.email_R1, 'enviado': estudiante.email_enviado_R1},
                'representante_2': {'email': estudiante.email_R2, 'enviado': estudiante.email_enviado_R2},
                'representante_3': {'email': estudiante.email_R3, 'enviado': estudiante.email_enviado_R3},
            }

            # Obtener el nombre completo del estudiante
            nombre_estudiante = f"{estudiante.primer_nombre} {estudiante.segundo_nombre} {estudiante.apellido_Paterno} {estudiante.apellido_Materno}"


            # Función para obtener el nombre correcto para el correo
            def obtener_nombre_para_correo(key, estudiante):
                if key == 'estudiante':
                    return f"{estudiante.apellido_Paterno} {estudiante.apellido_Materno} {estudiante.primer_nombre} {estudiante.segundo_nombre}"
                elif key == 'representante_1':
                    return f"{estudiante.apellido_paterno_R1} {estudiante.apellido_materno_R1} {estudiante.nombres_R1}"
                elif key == 'representante_2':
                    return f"{estudiante.apellido_paterno_R2} {estudiante.apellido_materno_R2} {estudiante.nombres_R2}"
                elif key == 'representante_3':
                    return f"{estudiante.apellido_paterno_R3} {estudiante.apellido_materno_R3} {estudiante.nombres_R3}"

            # Función para actualizar el estado de "enviado"
            def actualizar_estado_enviado(key, estudiante):
                if key == 'estudiante':
                    estudiante.email_enviado = True
                elif key == 'representante_1':
                    estudiante.email_enviado_R1 = True
                elif key == 'representante_2':
                    estudiante.email_enviado_R2 = True
                elif key == 'representante_3':
                    estudiante.email_enviado_R3 = True

            # Enviar correos a los destinatarios que no hayan recibido el correo previamente
            for key, value in emails.items():
                email = value['email']
                
                # Verificar que el correo no esté vacío o que no sea "nan"
                if email and email.lower() != "nan" and not value['enviado']:  

                    # Determinar el nombre adecuado para el correo según el destinatario
                    nombre_para_correo = obtener_nombre_para_correo(key, estudiante)

                    # Renderizar el contenido del correo
                    html_content = render_to_string('../templates/Administrador/email.html', 
                    {
                        'nombre_estudiante' : nombre_estudiante,
                        'nombre': nombre_para_correo,
                        'curso': curso.nombre,  # Añadir el nombre del curso
                        'lista_asignaturas_docentes': lista_asignaturas_docentes  # Añadir las asignaturas y docentes

                    })
                    email_message = EmailMessage(
                        'Bienvenido a nuestro sistema académico',  # Asunto
                        html_content,  # Cuerpo del mensaje
                        settings.EMAIL_HOST_USER,  # Remitente
                        [email]  # Destinatario actual
                    )
                    email_message.content_subtype = 'html'  # Asegura que el contenido es HTML
                    email_message.send()

                    print(f"Correo enviado a {email}")

                    # Marcar como enviado en el modelo correspondiente
                    actualizar_estado_enviado(key, estudiante)

            # Guardar los cambios en el modelo del estudiante
            estudiante.save()

            return JsonResponse({'success': True, 'message': 'Estudiante matriculado y correos enviados correctamente.'})

        except Estudiante.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Estudiante no encontrado.'})

        except Curso.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Curso no encontrado.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})



def obtener_matricula(request):
    matricula_id = request.GET.get('id')
    if not matricula_id or not matricula_id.isdigit():
        return JsonResponse({'error': 'ID de matrícula no válido'}, status=400)
    
    try:
        matricula = Matricula.objects.get(id=int(matricula_id))
        data = {
            'id': matricula.id,
            'estudiante_id': matricula.estudiante_id.id,
            'curso_id': matricula.curso_id.id,
            'estado': matricula.estado,
        }
        return JsonResponse(data)
    except ValueError:
        return JsonResponse({'error': 'ID de matrícula no válido'}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Matrícula no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
def actualizar_matricula(request):
    if request.method == 'POST':
        matricula_id = request.POST.get('matricula_id')
        estado = request.POST.get('estado')

        try:
            matricula = Matricula.objects.get(id=matricula_id)
            matricula.estado = estado
            matricula.save()

            return JsonResponse({'success': True, 'message': 'Matrícula actualizada correctamente.'})

        except Matricula.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Matrícula no encontrada.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})