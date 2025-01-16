from decimal import Decimal
import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from ..models import CursoAsignatura, PeriodoAcademico,Docente,Aporte,PeriodoDivision,TipoEvaluacion,Matricula,Calificacion, UnidadTrimestral


# RENDERIZA LA PANTALLA
@login_required
def docenteHome(request):
    user = request.user
    print(f"Usuario autenticado: {user.username}")

    try:
        docente = user.docente  # Intentamos acceder al perfil de docente
        id_docente =  f' {docente.id}'
        nombre_docente = f' {docente.apellido_Paterno} {docente.apellido_Materno} {docente.primer_nombre} {docente.segundo_nombre}'
        print(f"Perfil de Docente encontrado: {nombre_docente}")
    except Docente.DoesNotExist:
        nombre_docente = user.username  # En caso de que no exista perfil de docente
        print("Perfil de Docente no encontrado.")
    
    context = {
        'nombre_docente': nombre_docente,
        'id_docente': id_docente,
        'docente': docente,  # También puedes pasar todo el objeto docente si necesitas más detalles
    }
    print(f"Contexto enviado a la plantilla: {context}")
    return render(request, '../templates/Docente/docenteHome.html', context)


# QUIERO AHORA LISTAR LOS PERIODOS ACADEMICOS 

def listarPeriodosDocente(request):
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

@login_required
def listarCursosDocente(request, periodo_id):
    usuario = request.user

    try:
        # Obtenemos el perfil de docente asociado al usuario
        docente = usuario.docente

        # Obtenemos el período académico
        periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)

        # Filtramos los registros de la tabla CursoAsignatura por el docente y el período académico
        cursos_asignaturas = CursoAsignatura.objects.filter(docente_id=docente, curso_id__periodoAcademico_id=periodo_academico)

        # Organizamos los cursos y asignaturas en un diccionario
        cursos_con_asignaturas = {}
        for ca in cursos_asignaturas:
            curso = ca.curso_id
            asignatura = ca.asignatura_id
            if curso not in cursos_con_asignaturas:
                cursos_con_asignaturas[curso] = []
            cursos_con_asignaturas[curso].append({'asignatura': asignatura, 'curso_asignatura_id': ca.id})

        context = {
            'docente': docente,
            'cursos_con_asignaturas': cursos_con_asignaturas,
            'periodo_academico': periodo_academico,
        }

        return render(request, '../templates/Docente/adminDocente.html', context)

    except Docente.DoesNotExist:
        # Si el usuario no tiene un perfil de docente, redirigir a una página de error o mostrar un mensaje adecuado
        return render(request, 'error.html', {'message': 'No tienes permisos para acceder a esta página.'})

    


        
        
# ahora para crear un aporte necesitamos elegir el trimestre y por ende el tipo de evaluacion 
def listarTrimestresTipo(request, periodo_id):
    trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_id)
    data = {
        'message': 'ok',
        'periodo_id':periodo_id,
        'trimestres': []
    }
    
    if trimestres.exists():
        for trimestre in trimestres:
            unidades = UnidadTrimestral.objects.filter(trimestre_id=trimestre.id).values()
            data['trimestres'].append({
                'id': trimestre.id,
                'nombre': trimestre.nombre,
                'unidades': list(unidades)
            })
    else:
        data = {'message': 'no hay datos'}
        
    return JsonResponse(data)

# ahora vamos a listar los tipos de evaluacion que hay en cada trimestre
def listartiposPorTrimestre(request, trimestre_id):
    # Filtra los periodos académicos que tienen el estado "ACTIVO"
    tipoEvaluacion = list(TipoEvaluacion.objects.filter(trimestre_id=trimestre_id).values())
    if(len(tipoEvaluacion)>0 ):
        data={
            'message': "ok",
            'tipoEvaluacion':tipoEvaluacion,
        }
    else:
        data={
            'message':"no hay datos"
        }  
    return JsonResponse(data)

# ahora la funcion para crear un aporte

def crearAporteDocente(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombreAporte = data.get("nombreAporte")
            cursoAsignaturaId = data.get("cursoAsignatura_id")
            fechaAporte = data.get("fechaAporte")
            unidad_id = data.get("unidad_id")
            tipoEvaluacionId = data.get("cboAporteTrimestral")
            matriculas = data.get("matriculas", [])
            # Imprime las matrículas para depurar
            

            cursoAsignatura = CursoAsignatura.objects.get(id=cursoAsignaturaId)  # Asegúrate de obtener la instancia

            tipoEvaluacion = TipoEvaluacion.objects.get(id=tipoEvaluacionId)  # Asegúrate de obtener la instancia
            
            unidadTrimestral = UnidadTrimestral.objects.get(id=unidad_id)


            # Crear el nuevo aporte
            try:
                nuevoAporte = Aporte.objects.create(
                nombre=nombreAporte,
                cursoAsignatura_id=cursoAsignatura,  # Asegúrate de que sea una instancia
                fecha=fechaAporte,
                tipo_id=tipoEvaluacion ,
                unidad_id=unidadTrimestral
            )
            except Exception as e:
                return JsonResponse({
                    'estado': False,
                    'mensaje': f'Error al crear el aporte: {str(e)}'
                }, status=500)
            
            # Aquí puedes agregar la lógica para crear una calificación predeterminada
            for matricula_id in matriculas:
                print(f'Intentando crear calificación para matrícula ID: {matricula_id}')
                try:
                    matricula = Matricula.objects.get(id=matricula_id)  # Obtén el objeto Matricula
                    Calificacion.objects.create(
                        matricula_id=matricula,  # Asigna el objeto Matricula en lugar del ID
                        aporte_id=nuevoAporte,    # ID del nuevo aporte
                        nota=0,                # Valor predeterminado
                        observacion='NINGUNA'  # Observación predeterminada
                    )
                except Matricula.DoesNotExist:
                        print(f'Matrícula con ID {matricula_id} no existe.')
                except Exception as e:
                        print(f'Error al crear calificación para matrícula {matricula_id}: {str(e)}')

            return JsonResponse({
                'estado': True,
                'mensaje': 'Aporte creado exitosamente.'
            }, status=201)
        except CursoAsignatura.DoesNotExist:
            return JsonResponse({
                'estado': False,
                'mensaje': 'El curso asignatura no existe.'
            }, status=404)
        except TipoEvaluacion.DoesNotExist:
            return JsonResponse({
                'estado': False,
                'mensaje': 'El tipo de evaluación no existe.'
            }, status=404)
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
        
#  falta editar y eliminar

    
# ahora viene algo complicaso para editar para ello vamos a selecionar un aporte ya realizado
@login_required
def selecionarUnAporte(request, aporte_id):
    aporte = get_object_or_404(Aporte, id=aporte_id)
    tipo_evaluacion = aporte.tipo_id
    

    data = {
        'nombre': aporte.nombre,
        'fecha': aporte.fecha.strftime('%Y-%m-%d'),
        'tipo_evaluacion_id': tipo_evaluacion.id,
        
    }
    
    return JsonResponse({'message': 'ok', 'aporte': data})


# ahora vamos a actualizar un aporte
@login_required
def editarAporte(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            aporte = get_object_or_404(Aporte, id=id)

            # Actualizar los datos del aporte
            aporte.nombre = data.get('nombreAporteActualizar', aporte.nombre)
            aporte.fecha = data.get('fechaActualizar', aporte.fecha)
            tipo_id = data.get('cboTipoActualizar')

            if tipo_id:
                tipo_evaluacion = TipoEvaluacion.objects.get(id=tipo_id)
                aporte.tipo_id = tipo_evaluacion

            aporte.save()

            return JsonResponse({"message": "Aporte actualizado correctamente"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

def eliminarAporte(request, id):
    if request.method == 'DELETE':
        try:
            aporte = get_object_or_404(Aporte, id=id)
            aporte.delete()

            return JsonResponse({
                'estado': True,
                'mensaje': 'Aporte eliminado exitosamente.'
            }, status=200)
        except Aporte.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Aporte no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    
