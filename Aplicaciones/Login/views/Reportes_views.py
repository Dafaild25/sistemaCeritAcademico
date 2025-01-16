from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseServerError, JsonResponse
from django.contrib.auth.decorators import login_required
import json
from ..models import Administrador,CursoAsignatura,Curso,Matricula,Aporte,Calificacion,PeriodoDivision,PeriodoAcademico, TipoEvaluacion, UnidadTrimestral

 
def reportes(request):  
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
        
    }
    print(f"Contexto enviado a la plantilla: {context}")
    return render(request,"../templates/Reportes/reportes.html",context)


# Necesito listar los periodos academicos para ver los cursos que tengo ahi 
def listarPeriodosAcademicosReportes(request):
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
def listarCursosReportes(request, periodo_id):
        # Obtenemos el período académico
        periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)

        # Filtramos los registros de la tabla CursoAsignatura por el docente y el período académico
        cursos_asignaturas = CursoAsignatura.objects.filter( curso_id__periodoAcademico_id=periodo_academico)

        # Organizamos los cursos y asignaturas en un diccionario
        cursos_con_asignaturas = {}
        for ca in cursos_asignaturas:
            curso = ca.curso_id
            asignatura = ca.asignatura_id
            if curso not in cursos_con_asignaturas:
                cursos_con_asignaturas[curso] = []
            cursos_con_asignaturas[curso].append({'asignatura': asignatura, 'curso_asignatura_id': ca.id})

        context = {
            
            'cursos_con_asignaturas': cursos_con_asignaturas,
            'periodo_academico': periodo_academico,
        }

        return render(request, '../templates/Reportes/listarCursosReportes.html', context)


def vistaTrimestresReportes(request, clase_id):
    # Obtener el objeto CursoAsignatura con el ID proporcionado
    curso_asignatura = get_object_or_404(CursoAsignatura, id=clase_id)
    
    # Obtener el curso y la asignatura relacionados
    curso = curso_asignatura.curso_id
    asignatura = curso_asignatura.asignatura_id
    
    # Pasar los datos al contexto para el template
    context = {
        'curso_asignatura': curso_asignatura,
        'curso': curso,
        'asignatura': asignatura,
    }
    
    return render(request, '../templates/Reportes/vistaTrimestres.html', context)

# ahora para crear un aporte necesitamos elegir el trimestre Y EN ESTE CASO HABRA UNA UNIDAD 
def listarTrimestresReportes(request, periodo_id):
    trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_id)
    data = {
        'message': 'ok',
        'periodo_id': periodo_id,   
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
    

# aqui aumento lo que deseo 

# aqui vamos a dividir las funciones 
def obtener_matriculas(clase):
    return Matricula.objects.filter(
        curso_id=clase.curso_id,
        estado='ACTIVO'
    ).select_related('estudiante_id').order_by(
        'estudiante_id__apellido_Paterno',
        'estudiante_id__apellido_Materno',
        'estudiante_id__primer_nombre',
        'estudiante_id__segundo_nombre'
    )

def obtener_tipos_evaluacion(trimestre):
    return TipoEvaluacion.objects.filter(trimestre_id=trimestre)

def obtener_aportes(clase, trimestre):
    return Aporte.objects.filter( 
        cursoAsignatura_id=clase,
        tipo_id__trimestre_id=trimestre
    )

def obtener_calificaciones(matriculas, aportes):
    return Calificacion.objects.filter(
        matricula_id__in=matriculas,
        aporte_id__in=aportes
    ).select_related('matricula_id', 'aporte_id')

def crear_calificaciones_dict(calificaciones):
    calificaciones_dict = {}
    for calificacion in calificaciones:
        matricula_id = calificacion.matricula_id_id
        aporte_id = calificacion.aporte_id_id
        if matricula_id not in calificaciones_dict:
            calificaciones_dict[matricula_id] = {}
        calificaciones_dict[matricula_id][aporte_id] = calificacion.nota
    return calificaciones_dict

def crear_calificaciones_list(matriculas, aportes, calificaciones_dict,calificaciones):
    calificaciones_list = []
    for matricula in matriculas:
        for aporte in aportes:
            nota = calificaciones_dict.get(matricula.id, {}).get(aporte.id, '0')
            calificacion = next(
                (c for c in calificaciones
                if c.matricula_id_id == matricula.id and c.aporte_id_id == aporte.id), 
                None
            )
            calificaciones_list.append({
                'matricula_id': matricula.id,
                'aporte_id': aporte.id,
                'nota': nota,
                'id': calificacion.id if calificacion else None,
                'observacion': calificacion.observacion if calificacion else ''
            })
    return calificaciones_list

def calcular_notas_ponderadas(matriculas, tipos_evaluacion, calificaciones, trimestre_id):
    notas_ponderadas = {}
    ponderaciones_tipo = {tipo.id: tipo.ponderacion for tipo in tipos_evaluacion}
    
    
    try:
        trimestre = PeriodoDivision.objects.get(id=trimestre_id)
        periodo_academico = trimestre.periodo_academico
        cantidad_decimales = periodo_academico.cantidad
    except PeriodoDivision.DoesNotExist:
        cantidad_decimales = 2  # Valor por defecto si no se encuentra el trimestre_id
    except periodo_academico.DoesNotExist:
        cantidad_decimales = 2  # Valor por defecto si no se encuentra el periodo_academico
    
    # Definir el formato de decimales con la cantidad indicada
    formato_decimales = Decimal('1.' + '0' * cantidad_decimales)
    
    for matricula in matriculas:
        matricula_id = matricula.id
        notas_ponderadas[matricula_id] = {}
        
        # Inicializar acumuladores de calificaciones ponderadas y conteo de notas
        ponderado_total = {tipo_id: Decimal('0.00') for tipo_id in ponderaciones_tipo}
        conteo_notas = {tipo_id: 0 for tipo_id in ponderaciones_tipo}
        
        # Agrupar las calificaciones por tipo de evaluación
        calificaciones_tipo = [calificacion for calificacion in calificaciones
                            if calificacion.matricula_id.id == matricula_id]
        
        
        
        for calificacion in calificaciones_tipo:
            tipo_id = calificacion.aporte_id.tipo_id.id
            ponderacion = ponderaciones_tipo.get(tipo_id, Decimal('0.00'))
            
            # Multiplicar la calificación por la ponderación
            ponderado = calificacion.nota * (ponderacion / Decimal('100.00'))
            
            # Sumar el ponderado
            ponderado_total[tipo_id] += ponderado
            conteo_notas[tipo_id] += 1
        
        # Calcular el promedio ponderado para cada tipo de evaluación
        promedio_ponderado = {}
        for tipo_id in ponderaciones_tipo:
            if conteo_notas[tipo_id] > 0:
                promedio_ponderado[tipo_id] = (ponderado_total[tipo_id] / conteo_notas[tipo_id]).quantize(formato_decimales, rounding=ROUND_HALF_UP)
            else:
                promedio_ponderado[tipo_id] = Decimal('0.00').quantize(formato_decimales, rounding=ROUND_HALF_UP)
        
        notas_ponderadas[matricula_id] = promedio_ponderado

    return notas_ponderadas

def calcular_promedios_tipo_estudiante(matriculas, tipos_evaluacion, calificaciones_list,trimestre_id):
    promedios_tipo_estudiante = {}
    #Obtener el periodo académico desde la primera calificación para obtener la cantidad de decimales
    # Obtener la cantidad de decimales desde el trimestre_id
    try:
        trimestre = PeriodoDivision.objects.get(id=trimestre_id)
        periodo_academico = trimestre.periodo_academico
        cantidad_decimales = periodo_academico.cantidad
    except PeriodoDivision.DoesNotExist:
        cantidad_decimales = 2  # Valor por defecto si no se encuentra el trimestre_id
    except periodo_academico.DoesNotExist:
        cantidad_decimales = 2  # Valor por defecto si no se encuentra el periodo_academico
    
    # Definir el formato de decimales con la cantidad indicada
    formato_decimales = Decimal('1.' + '0' * cantidad_decimales)
    
    
    for matricula in matriculas:
        promedios_tipo_estudiante[matricula.id] = {}
       
        #promedios_tipo_estudiante[matricula.id] = {}
        for tipo in tipos_evaluacion:
            tipo_id = tipo.id
            notas_tipo = [Decimal(calificacion['nota']) for calificacion in calificaciones_list if Aporte.objects.get(id=calificacion['aporte_id']).tipo_id_id == tipo_id and calificacion['matricula_id'] == matricula.id]
            promedio_tipo = sum(notas_tipo) / len(notas_tipo) if notas_tipo else Decimal('0.00')
            promedios_tipo_estudiante[matricula.id][tipo_id] = promedio_tipo.quantize(formato_decimales, rounding=ROUND_HALF_UP)
    return promedios_tipo_estudiante

# aqui termina las divisiones 




def reportesTrimestrales(request, trimestre_id, clase_id):
    try:
        trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
        clase = get_object_or_404(CursoAsignatura, id=clase_id)

        # Obtener matrículas, tipos de evaluación, aportes y calificaciones
        matriculas = obtener_matriculas(clase)
        tipos_evaluacion = obtener_tipos_evaluacion(trimestre)
        aportes = obtener_aportes(clase, trimestre)
        calificaciones = obtener_calificaciones(matriculas, aportes)
        
        # Crear diccionario y lista de calificaciones
        calificaciones_dict = crear_calificaciones_dict(calificaciones)
        calificaciones_list = crear_calificaciones_list(matriculas, aportes, calificaciones_dict,calificaciones)
        
        # Calcular las notas ponderadas y los promedios por tipo de evaluación
        notas_ponderadas = calcular_notas_ponderadas(matriculas, tipos_evaluacion, calificaciones,trimestre_id)
        promedios_tipo_estudiante = calcular_promedios_tipo_estudiante(matriculas, tipos_evaluacion, calificaciones_list, trimestre_id)

        # Convertir las estructuras de datos a listas para enviarlas al template
        notas_ponderadas_list = [
            {
                'matricula_id': matricula_id,
                'tipos': {
                    tipo_id: str(notas_ponderadas[matricula_id].get(tipo_id, Decimal('0.00')))
                    for tipo_id in tipos_evaluacion.values_list('id', flat=True)
                }
            }
            for matricula_id in notas_ponderadas
        ]
        
        
        promedios_tipo_estudiante_list = [
            {
                'matricula_id': matricula_id,
                'tipos': {
                    tipo_id: str(promedios_tipo_estudiante[matricula_id].get(tipo_id, Decimal('0.00')))
                    for tipo_id in tipos_evaluacion.values_list('id', flat=True)
                }
            }
            for matricula_id in promedios_tipo_estudiante
        ]
        

        # Pasar los datos al template
        context = {
            'trimestre': trimestre,
            'clase': clase,
            'matriculas': matriculas,
            'tipos_evaluacion': tipos_evaluacion,
            'aportes': aportes,
            'calificaciones_list': calificaciones_list,
            'notas_ponderadas_list': notas_ponderadas_list,
            'promedios_tipo_estudiante_list': promedios_tipo_estudiante_list
        }

        return render(request, '../templates/Reportes/reportesTrimestrales.html', context)
    
    except Exception as e:
        print(f"Error en reportesTrimestrales: {e}")
        return HttpResponseServerError("Error en el servidor.")



# vamos a crear un aporte para un administrador 
@login_required
def crearAporteAdmin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombreAporte = data.get("nombreAporte")
            cursoAsignaturaId = data.get("cursoAsignatura_id")
            fechaAporte = data.get("fechaAporte")
            unidad_id = data.get("unidad_id")
            tipoEvaluacionId = data.get("cboAporteTrimestral")
            matriculas = data.get("matriculas", [])

            # Obtener el objeto CursoAsignatura a partir del cursoAsignaturaId
            cursoAsignatura = CursoAsignatura.objects.get(id=cursoAsignaturaId)

            # Obtener el objeto TipoEvaluacion a partir del tipoEvaluacionId
            tipoEvaluacion = TipoEvaluacion.objects.get(id=tipoEvaluacionId)

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


@login_required
def selecionarUnAporteAdmin(request, aporte_id):
    aporte = get_object_or_404(Aporte, id=aporte_id)
    tipo_evaluacion = aporte.tipo_id
    

    data = {
        'nombreAporteAdmin': aporte.nombre,
        'fechaAdmin': aporte.fecha.strftime('%Y-%m-%d'),
        'tipoEvaluacionAdmin': tipo_evaluacion.id,
        
    }
    
    return JsonResponse({'message': 'ok', 'aporte': data})


# vamos a guardar el aporte editado 
@login_required
def editarAporteAdmin(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            aporte = get_object_or_404(Aporte, id=id)

            # Actualizar los datos del aporte
            aporte.nombre = data.get('nombreAporteActualizarAdmin', aporte.nombre)
            aporte.fecha = data.get('fechaActualizarAdmin', aporte.fecha)
            tipo_id = data.get('cboTipoActualizarAdmin')

            if tipo_id:
                tipo_evaluacion = TipoEvaluacion.objects.get(id=tipo_id)
                aporte.tipo_id = tipo_evaluacion

            aporte.save()

            return JsonResponse({"message": "Aporte actualizado correctamente"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

# Eliminar aporte por parte del admin
def eliminarAporteAdmin(request, id):
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
    
    
    
# aqui vamos a guardar calificaciones 
def calificacionAporteTrimestralAdmin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calificaciones = data.get('calificaciones', [])
            trimestre_id = data.get('trimestre_id')
            clase_id = data.get('clase_id')
        

            for calificacion_data in calificaciones:
                matricula_id = calificacion_data.get('matricula_id')
                aporte_id = calificacion_data.get('aporte_id')
                nota = calificacion_data.get('nota')
                
                

                # Convertir nota a Decimal y manejar valores vacíos
                if nota == '':
                    nota = None  # Si el campo está vacío, lo guardamos como None para usar el valor por defecto
                else:
                    try:
                        nota = Decimal(nota)
                    except (ValueError, InvalidOperation):
                        return JsonResponse({'success': False, 'error': 'El valor de la nota no es válido.'})

                matricula = Matricula.objects.get(id=matricula_id)
                aporte = Aporte.objects.get(id=aporte_id)

                # Actualizar o crear la calificación
                Calificacion.objects.update_or_create(
                    matricula_id=matricula,
                    aporte_id=aporte,
                    defaults={'nota': nota if nota is not None else Decimal('0.00')}
                )
                
                # desde aqui mejoramos el codigo 
                
                

            return JsonResponse({
                'success': True,
                
            })
        except Exception as e:
            
            print('Error:', str(e))  # Agregar esto para depuración en el servidor
            return JsonResponse({'success': False, 'error': str(e)})
        
    
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



# este no ocupo 
def listar_estudiantes(request, curso_id):
    # Filtrar las matriculas por curso
    matriculas = Matricula.objects.filter(curso_id=curso_id, estado='ACTIVO')
    # Obtener los estudiantes relacionados
    estudiantes = [matricula.estudiante_id for matricula in matriculas]
    
    # Pasar el nombre del curso a la plantilla también
    curso = Curso.objects.get(id=curso_id)
    
    return render(request, '../templates/Reportes/listarEstudiantes.html', {
        'estudiantes': estudiantes,
        'curso': curso
    })



