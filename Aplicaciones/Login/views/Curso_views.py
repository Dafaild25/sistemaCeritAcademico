from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
import json
from ..models import PeriodoAcademico,Curso,CursoAsignatura
#from django.contrib.auth import login,authenticate


    

def listarCursos(request,periodo_id):   
    periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)
    cursos=list(Curso.objects.filter(periodoAcademico_id=periodo_id).values())
    return render(request,"../templates/Curso/listarCursos.html",{'cursos': cursos,'periodo_academico': periodo_academico})


# AHORA VAMOS A CREAR  UN NUEVO  CURSO 
def crearCurso(request):
    if request.method == 'POST':
        try:
            # Cargar los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            nombre = data.get("nombre")
            paralelo = data.get("paralelo")
            periodoAcademico_id = data.get("periodoAcademico_id")
            descripcion = data.get("descripcion")
            estado = data.get("estado", "ACTIVO")  # Predeterminado a 'ACTIVO' si no se proporciona

            # Validar que todos los campos requeridos estén presentes
            if not nombre or not paralelo or not periodoAcademico_id:
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'Faltan campos obligatorios.'
                }, status=400)

            # Obtener el periodo académico correspondiente
            try:
                periodo_academico = PeriodoAcademico.objects.get(id=periodoAcademico_id)
            except PeriodoAcademico.DoesNotExist:
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El periodo académico no existe.'
                }, status=404)

            # Crear el nuevo curso
            nuevo_curso = Curso.objects.create(
                nombre=nombre,
                paralelo=paralelo,
                periodoAcademico_id=periodo_academico,
                descripcion=descripcion,
                estado=estado
            )

            return JsonResponse({
                'estado': True,
                'mensaje': 'Curso creado exitosamente.',
                
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({
                'estado': False,
                'mensaje': 'Error en el formato del JSON.'
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'estado': False,
                'mensaje': f'Error: {str(e)}'
            }, status=500)

    else:
        return JsonResponse({
            'estado': False,
            'mensaje': 'Método no permitido.'
        }, status=405)
        

# ahora vamos a selecionar un curso
def selecionarUnCurso(request,id):
    if request.method == 'GET':
        try:
            unCurso = Curso.objects.get(id=id)
            data = {
                'id':unCurso.id,
                'nombreCurso': unCurso.nombre,
                'paraleloCurso': unCurso.paralelo,
                'descripcionCurso': unCurso.descripcion,
                'estadoCurso': unCurso.estado,    
                
            }
            return JsonResponse(data, status=200)
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({'error': 'Curso no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
#ahora vamos a editar un Curso+

def editarUnCurso(request, id):
    data = json.loads(request.body)
    if request.method == 'POST':
        try:
            cursoEditado = Curso.objects.get(id=id)
            
            cursoEditado.nombre = data['nombreCursoActualizar']
            cursoEditado.paralelo = data['paraleloCursoActualizar']
            cursoEditado.descripcion = data['descripcionCursoActualizar']
            cursoEditado.estado = data['estadoCursoActualizar']
            cursoEditado.save()
            return JsonResponse({"message": "Curso actualizado correctamente"})
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({"error": "Curso no encontrado"}, status=404)
    return JsonResponse({"erro": "Metodo non Permitido"}, status= 405)

#ahora podemos eliminar un tRIMESTRE
def eliminarUnCurso(request, id):
    if request.method == 'DELETE':
        try:
            curso = Curso.objects.get(id=id)
            periodo_academico_id = curso.periodoAcademico_id
            curso.delete()
            
            # Verificar si aún quedan trimestres para el período académico
            hay_Cursos = Curso.objects.filter(periodoAcademico_id=periodo_academico_id).exists()
            
            return JsonResponse({
                'estado': True, 
                'mensaje': 'Curso  eliminado exitosamente.',
                'hay_Cursos': hay_Cursos
            }, status=200)
        except Curso.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Curso  no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)