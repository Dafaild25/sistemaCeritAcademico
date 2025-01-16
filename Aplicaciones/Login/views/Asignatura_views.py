import json
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,authenticate
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from ..models import Administrador,PeriodoAcademico,Asignatura,Curso,Docente,CursoAsignatura
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def asignatura(request):
    asignaturas = Asignatura.objects.all()
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
        'asignaturas':asignaturas

    }
    print(f"Contexto enviado a la plantilla: {context}")

    return render(request, '../templates/Asignatura/asignatura.html',context)

@csrf_exempt
def guardar_asignatura(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            nivel = data.get('nivel')

            subnivel = data.get('subnivel')

            # Validar los datos (opcional)
            if not nombre or not nivel or not subnivel:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios'}, status=400)

            # Crear y guardar la nueva asignatura
            asignatura = Asignatura(nombre=nombre, nivel=nivel, subnivel=subnivel)
            asignatura.save()

            response = {
                'status': 'success',
                'message': 'Asignatura guardada correctamente'
            }
            return JsonResponse(response)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Error al decodificar JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



# OTRO METODO PARA GUARDAR
@csrf_exempt
def guardarAsignatura(request):
    if request.method == 'POST':
        try:
            # Extrae los datos del request
            data = json.loads(request.body)
            nombre = data.get('nombre')
            nivel = data.get('nivel')
            descripcion = data.get('descripcion')
            estado = data.get('estado', 'ACTIVO')

            # Validar los datos
            if not nombre or not nivel or not descripcion:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'}, status=400)

            # Crea la asignatura
            Asignatura.objects.create(nombre=nombre, nivel=nivel, descripcion=descripcion,estado=estado)

            # Responde con un JSON de éxito
            return JsonResponse({'status': 'success', 'message': 'Asignatura creada exitosamente.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Error al decodificar JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)




def listar_asignaturas(request):
    asignaturas = Asignatura.objects.all()
    context = {
        'asignaturas_inicial': asignaturas.filter(nivel='INICIAL'),
        'asignaturas_basico': asignaturas.filter(nivel='BASICO'),
        'asignaturas_bachillerato': asignaturas.filter(nivel='BACHILLERATO'),
    }

    # Comprobar si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, '../templates/Asignatura/listadoAsignaturas.html', context)
    else:
        return render(request, '../templates/Asignatura/asignatura.html', context)



#OBTENER
def obtenerAsignatura(request, id):
    try:
        asignatura = Asignatura.objects.get(id=id)
        data = {
            "id": asignatura.id,
            "nombre": asignatura.nombre,
            "nivel": asignatura.nivel,
            "descripcion": asignatura.descripcion,
            "estado": asignatura.estado


        }
        return JsonResponse(data)
    except Asignatura.DoesNotExist:
        return JsonResponse({"error": "Asignatura no encontrado"}, status=404)


@csrf_exempt
def actualizarAsignatura(request, id):
    if request.method == 'POST':
        try:
            asignatura = Asignatura.objects.get(pk=id)
            data = json.loads(request.body)
            asignatura.nombre = data.get('nombre', asignatura.nombre)
            asignatura.nivel = data.get('nivel', asignatura.nivel)

            asignatura.descripcion = data.get('descripcion', asignatura.descripcion)
            asignatura.estado = data.get('estado', asignatura.estado)

            asignatura.save()
            return JsonResponse({'status': 'success', 'message': 'Asignatura actualizada correctamente'})
        except Asignatura.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Asignatura no encontrada'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



def eliminarAsignatura(request, id):
    if request.method == 'DELETE':
        try:
            asignatura = Asignatura.objects.get(id=id)
            asignatura.delete()
            
            # Puedes agregar lógica adicional aquí si es necesario, como verificar otras condiciones
            
            return JsonResponse({
                'estado': True,
                'mensaje': 'Asignatura eliminada exitosamente.'
            }, status=200)
        except Asignatura.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Asignatura no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    
    
    
# crearemos un listado de cursos pero en formatojson 
def listarCursosClase(request, periodo_id):
    cursos=list(Curso.objects.filter(periodoAcademico_id = periodo_id).values())
    if(len(cursos)>0):
        data={'message': "ok", 'cursos':cursos}
    else:
        data={'message':"no hay datos"}
    return JsonResponse(data)

def listarAsignaturasClase(request):
    asignaturas=list(Asignatura.objects.values())
    if(len(asignaturas)>0):
        data={'message': "ok", 'asignaturas':asignaturas}
    else:
        data={'message':"no hay datos"}
    return JsonResponse(data)



def listarDocentesClase(request):
    docentes=list(Docente.objects.values())
    if(len(docentes)>0):
        data={'message': "ok", 'docentes':docentes}
    else:
        data={'message':"no hay datos"}
    return JsonResponse(data)


# Funcion para guardar

def guardarCursoAsignatura(request):
    if request.method == 'POST':
        try:
            # Cargar los datos JSON
            data = json.loads(request.body)
            
            curso_id = data.get('curso_id')
            asignatura_id = data.get('asignatura_id')
            docente_id = data.get('docente_id')
            
            # Validar que los IDs no sean None
            if curso_id and asignatura_id and docente_id:
                curso = Curso.objects.get(id=curso_id)
                asignatura = Asignatura.objects.get(id=asignatura_id)
                docente = Docente.objects.get(id=docente_id)
                
                # Crear un nuevo registro en CursoAsignatura
                curso_asignatura, created = CursoAsignatura.objects.get_or_create(
                    curso_id=curso, 
                    asignatura_id=asignatura, 
                    docente_id=docente
                )
                
                if created:
                    data = {'status': 'success', 'message': 'CursoAsignatura guardado correctamente'}
                else:
                    data = {'status': 'error', 'message': 'Esta asignatura ya está asociada con el curso'}
            else:
                data = {'status': 'error', 'message': 'Faltan datos para procesar la solicitud'}
        except json.JSONDecodeError:
            data = {'status': 'error', 'message': 'Error al procesar el JSON'}
        except Curso.DoesNotExist:
            data = {'status': 'error', 'message': 'Curso no encontrado'}
        except Asignatura.DoesNotExist:
            data = {'status': 'error', 'message': 'Asignatura no encontrada'}
        except Docente.DoesNotExist:
            data = {'status': 'error', 'message': 'Docente no encontrado'}
        except Exception as e:
            data = {'status': 'error', 'message': str(e)}
    else:
        data = {'status': 'error', 'message': 'Método no permitido'}
    
    return JsonResponse(data)




# ahora primero quiero que me renderize solo la vista 
def vistaClases(request):
    return render(request,'../templates/Asignatura/listarClases.html')

# ahora quiero que me listen las clases de ese curso
def listarCursosAsignatura(request, periodo_id):
    try:
        # Obtén el período académico
        periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)
        
        # Obtén los cursos asociados a ese período
        cursos_asignaturas = CursoAsignatura.objects.filter(curso_id__periodoAcademico_id=periodo_academico)
        
        # Renderiza la plantilla con los cursos
        return render(request, "Asignatura/listarClases.html", {
            'cursoClase': cursos_asignaturas,
            'periodoClase': periodo_academico
        })
    except Exception as e:
        print(f"Error al listar cursos y asignaturas: {e}")
        return render(request, "Asignatura/listarClases.html", {
            'cursoClase': [],
            'periodoClase': None,
            'error': 'Hubo un error al procesar la solicitud.'
        })
        
def eliminarCursoAsigantura(request, id):
    if request.method == 'DELETE':
        try:
            clase = CursoAsignatura.objects.get(id=id)
            clase.delete()
            
            # Puedes agregar lógica adicional aquí si es necesario, como verificar otras condiciones
            
            return JsonResponse({
                'estado': True,
                'mensaje': 'clase eliminada exitosamente.'
            }, status=200)
        except Asignatura.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'clase no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    

