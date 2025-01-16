from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import PeriodoAcademico,Curso,CursoAsignatura
#from django.contrib.auth import login,authenticate


def adminCurso (request):
    return render (request,'../templates/Curso/adminCurso.html')

# Necesito listar los periodos academicos para ver los cursos que tengo ahi 
def listarPeriodosAcademicos(request):
    periodos=list(PeriodoAcademico.objects.values())
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
    return render(request,"../templates/Curso/listarCursosPeriodo.html",{'cursos': cursos})

def listarCursoAsignatura(request,curso_id):
    
    # Obtiene el curso por su ID
    curso = get_object_or_404(Curso, id=curso_id)
    # Obtiene todas las relaciones de asignaturas y docentes para el curso dado
    curso_asignaturas = CursoAsignatura.objects.filter(curso_id=curso)
    asignaturas_docentes = [
        {
            'asignatura': ca.asignatura_id,
            'docente': ca.docente_id
        }
        for ca in curso_asignaturas
    ]
    
    return render(request,"../templates/Curso/cursoAsignatura.html",{ 'curso': curso,
        'asignaturas_docentes': asignaturas_docentes,})
    
@csrf_exempt
def crear_curso(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            paralelo = request.POST.get('paralelo')
            periodo_id = request.POST.get('periodo')
            estado = request.POST.get('estado')
            descripcion = request.POST.get('descripcion')

            if not all([nombre, paralelo, periodo_id, estado, descripcion]):
                return JsonResponse({'success': False, 'error': 'Todos los campos son requeridos.'})

            # Verificar que el periodo académico existe
            periodo = PeriodoAcademico.objects.get(id=periodo_id)

            # Crear y guardar el curso
            curso = Curso(
                nombre=nombre,
                paralelo=paralelo,
                periodoAcademico_id=periodo,
                estado=estado,
                descripcion=descripcion
            )
            curso.save()

            return JsonResponse({'success': True})

        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Periodo académico no encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido.'})
