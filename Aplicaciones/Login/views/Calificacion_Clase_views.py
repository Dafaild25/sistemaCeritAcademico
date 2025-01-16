from collections import defaultdict
from decimal import ROUND_DOWN, Decimal, InvalidOperation,ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db import transaction
from django.db.models import Avg,Count
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Aporte, Calificacion, CursoAsignatura, Matricula, PeriodoDivision, EquivalentesTipoEvaluacion, TipoEvaluacion, subpromedioTipoEvaluacion

def vistaTrabajoClase(request, clase_id):
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
    
    return render(request, '../templates/Docente/vistaTrabajoClase.html', context)




    

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
             # Manejar caso donde calificacion es None
            if calificacion is None:
                print(f"No se encontró calificación para Matrícula ID: {matricula.id}, Aporte ID: {aporte.id}")
                # Agregar un registro vacío o con valores por defecto
                calificaciones_list.append({
                    'id': None,  # No hay calificación, así que el ID es None
                    'matricula_id': matricula.id,
                    'aporte_id': aporte.id,
                    'nota': nota,
                    'observacion': ''  # No hay observación si no hay calificación
                })
            else:
                # Calificación encontrada, agregarla a la lista
                calificaciones_list.append({
                    'id': calificacion.id,  # Agregar el ID de la calificación
                    'matricula_id': matricula.id,
                    'aporte_id': aporte.id,
                    'nota': nota,
                    'observacion': calificacion.observacion if calificacion else ''
                })
    return calificaciones_list

def calcular_notas_ponderadas(matriculas, tipos_evaluacion, calificaciones, trimestre_id):
    notas_ponderadas = {}
    ponderaciones_tipo = {tipo.id: tipo.ponderacion for tipo in tipos_evaluacion}
    periodo_academico=None
    
    try:
        trimestre = PeriodoDivision.objects.get(id=trimestre_id)
        periodo_academico = trimestre.periodo_academico
        cantidad_decimales = periodo_academico.cantidad
    except PeriodoDivision.DoesNotExist:
        cantidad_decimales = 2  # Valor por defecto si no se encuentra el trimestre_id
        periodo_academico = None  # Aseguramos que periodo_academico sea None
    except AttributeError:  # Captura el error si periodo_academico es None
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


# guardar las notas promediadas 
def guardar_equivalentes_tipo_evaluacion(notas_ponderadas_list, trimestre_id):
    # Obtener la instancia de PeriodoDivision usando el ID
    trimestre_instance = get_object_or_404(PeriodoDivision, id=trimestre_id)
    
    for item in notas_ponderadas_list:
        matricula_id = item['matricula_id']
        
        try:
            # Obtener la instancia de Matricula usando el ID
            matricula_instance = Matricula.objects.get(id=matricula_id)
        except Matricula.DoesNotExist:
            print(f"Matricula con id {matricula_id} no existe.")
            continue  # Maneja el error de la forma que desees
        
        for tipo_id, promedioTipo in item['tipos'].items():
            try:
                # Obtener la instancia de TipoEvaluacion usando el ID
                tipo_evaluacion_instance = TipoEvaluacion.objects.get(id=tipo_id)
            except TipoEvaluacion.DoesNotExist:
                print(f"Tipo de evaluación con id {tipo_id} no existe.")
                continue  # Maneja el error de la forma que desees
            
            EquivalentesTipoEvaluacion.objects.update_or_create(
                matricula_id=matricula_instance,         # Pasamos la instancia de Matricula
                trimestre_id=trimestre_instance,         # Pasamos la instancia de PeriodoDivision
                tipoEvaluacion_id=tipo_evaluacion_instance,  # Pasamos la instancia de TipoEvaluacion
                defaults={'promedioTipo': promedioTipo}
            )
            
def guardar_promedios_tipo_estudiante(promedios_tipo_estudiante, trimestre_id):
    """
    Guarda o actualiza los promedios de tipo de evaluación de los estudiantes.
    
    Parameters:
    - promedios_tipo_estudiante: dict con los promedios calculados por tipo de evaluación para cada matrícula.
    - trimestre_id: ID del trimestre para el cual se están guardando los promedios.
    """
    for matricula_id, promedios in promedios_tipo_estudiante.items():
        for tipo_evaluacion_id, promedio in promedios.items():
            try:
                # Intenta obtener la instancia existente para actualizarla
                subpromedio = subpromedioTipoEvaluacion.objects.get(
                    matricula_id_id=matricula_id,
                    trimestre_id_id=trimestre_id,
                    tipoEvaluacion_id_id=tipo_evaluacion_id
                )
                # Actualiza el promedio si la instancia ya existe
                subpromedio.evaluacionPromedio = promedio
                subpromedio.save()

            except ObjectDoesNotExist:
                # Si no existe, crea una nueva instancia
                subpromedioTipoEvaluacion.objects.create(
                    matricula_id_id=matricula_id,
                    trimestre_id_id=trimestre_id,
                    tipoEvaluacion_id_id=tipo_evaluacion_id,
                    evaluacionPromedio=promedio,
                    observacion='NINGUNA'
                )
# aqui termina las divisiones 


# aqui va el completo la funcion
def claseTrabajo(request, trimestre_id, clase_id):
    try:
        trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
        clase = get_object_or_404(CursoAsignatura, id=clase_id)
        
        print(f"Trimestre: {trimestre.id}, Clase: {clase.id}")
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
        
        # Llamar a la función para guardar los promedios
        guardar_equivalentes_tipo_evaluacion(notas_ponderadas_list, trimestre_id)
        guardar_promedios_tipo_estudiante(promedios_tipo_estudiante,trimestre_id)
        # Obtener los promedios guardados desde la base de datos
       
        # Obtener la cantidad de decimales desde el periodo académico
        cantidad_decimales = trimestre.periodo_academico.cantidad
        
        # Calcular promedios totales por matrícula
        promedios_totales = {}
        for matricula in matriculas:
            total_promedio = EquivalentesTipoEvaluacion.objects.filter(
                matricula_id=matricula,
                trimestre_id=trimestre
            ).aggregate(total=Sum('promedioTipo'))['total'] or Decimal('0.00')
            # Formatear el promedio total de acuerdo a la cantidad de decimales
            total_promedio = total_promedio.quantize(Decimal('1.' + '0' * cantidad_decimales), rounding=ROUND_DOWN)

            promedios_totales[matricula.id] = total_promedio
        
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
            
            'promedios_tipo_estudiante_list': promedios_tipo_estudiante_list,
            'promedios_totales': promedios_totales,
        }

        return render(request, '../templates/Docente/claseTrabajo.html', context)
    
    except Exception as e:
        print(f"Error en claseTrabajo: {e}")
        return HttpResponseServerError("Error en el servidor.")


def reporteTrimestral(request, trimestre_id, clase_id):
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
        
        # Obtener la cantidad de decimales desde el periodo académico
        cantidad_decimales = trimestre.periodo_academico.cantidad
        # Calcular promedios totales por matrícula
        promedios_totales = {}
        for matricula in matriculas:
            total_promedio = EquivalentesTipoEvaluacion.objects.filter(
                matricula_id=matricula,
                trimestre_id=trimestre
            ).aggregate(total=Sum('promedioTipo'))['total'] or Decimal('0.00')
            # Formatear el promedio total de acuerdo a la cantidad de decimales
            total_promedio = total_promedio.quantize(Decimal('1.' + '0' * cantidad_decimales), rounding=ROUND_DOWN)

            promedios_totales[matricula.id] = total_promedio

        # Pasar los datos al template
        context = {
            'trimestre': trimestre,
            'clase': clase,
            'matriculas': matriculas,
            'tipos_evaluacion': tipos_evaluacion,
            'aportes': aportes,
            'promedios_tipo_estudiante_list': promedios_tipo_estudiante_list,
            'promedios_totales': promedios_totales,
        }

        return render(request, '../templates/Docente/reporteTrimestral.html', context)
    
    except Exception as e:
        print(f"Error en reporteTrimestral: {e}")
        return HttpResponseServerError("Error en el servidor.")
    
# ESTA FUNCION GUARDA LAS NOTAS     
def calificacionAporteTrimestral(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calificaciones = data.get('calificaciones', [])
            trimestre_id = int(data.get('trimestre_id'))  # Convertir a entero
            clase_id = int(data.get('clase_id'))  # Convertir a entero
            
            clase = get_object_or_404(CursoAsignatura, id=clase_id)
            trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
            trimestre_id = trimestre.id
           
            for calificacion_data in calificaciones:
                matricula_id = int(calificacion_data.get('matricula_id'))  # Convertir a entero
                aporte_id = int(calificacion_data.get('aporte_id'))  # Convertir a entero
                nota = calificacion_data.get('nota')
                
                # Validar los IDs
                if matricula_id is None or aporte_id is None:
                    return JsonResponse({'success': False, 'error': 'ID de matrícula o aporte no puede ser None.'})

                try:
                    matricula = Matricula.objects.get(id=matricula_id)
                except Matricula.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Matrícula con ID {matricula_id} no encontrada.'})

                try:
                    aporte = Aporte.objects.get(id=aporte_id)
                except Aporte.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Aporte con ID {aporte_id} no encontrado.'})

                

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
                
                
            return JsonResponse({
                'success': True,
                
            })
        except Exception as e:
            
            print('Error:', str(e))  # Agregar esto para depuración en el servidor
            return JsonResponse({'success': False, 'error': str(e)})
        
    
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


# funcion para  obtener una calificaciones
def obtenerObservacion(request, calificacion_id):
    try:
        # Obtener la calificación por su ID
        calificacion = Calificacion.objects.get(id=calificacion_id)
        # Retornar la observación en un JsonResponse
        return JsonResponse({
            'observacion': calificacion.observacion,
        })
    except Calificacion.DoesNotExist:
        return JsonResponse({
            'error': 'Calificación no encontrada'
        }, status=404)
        
def editarObservacion(request, calificacion_id):
    if request.method == 'POST':
        try:
            calificacion = Calificacion.objects.get(id=calificacion_id)
            observacion = request.POST.get('observacion', '')
            calificacion.observacion = observacion
            calificacion.save()
            return JsonResponse({'status': 'success'})
        except Calificacion.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Calificación no encontrada'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
    
# aqui voy a obtener las calificaciones 
def obtenerCalificaciones(request, matricula_id, aporte_id, calificacion_id):
    try:
        # Filtrar por matricula_id, aporte_id y calificacion_id (obligatorio)
        calificaciones = Calificacion.objects.filter(
            matricula_id=matricula_id,
            aporte_id=aporte_id,
            id=calificacion_id  # Filtrar por el ID de calificación
        )

        # Verificar si se encontró la calificación
        if not calificaciones.exists():
            return JsonResponse({'success': False, 'error': 'No se encontró la calificación solicitada.'})

        # Retornar las calificaciones en formato JSON
        data = {
            'calificaciones': [{'id': c.id, 'nota': str(c.nota)} for c in calificaciones]
        }

        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        print(f"Error en obtenerCalificaciones: {e}")
        return JsonResponse({'success': False, 'error': str(e)})



#  aqui voy aobtener los promedios de cada tipo de evaluacion de cada estudiante 
def obtenerEquivalentesTipos(request, tipo_id, matricula_id, trimestre_id):
    try:
        # Buscar la instancia de EwuivalentesTipoEvaluacion con los parámetros dados
        promedio = get_object_or_404(
            EquivalentesTipoEvaluacion, 
            tipoEvaluacion_id=tipo_id, 
            matricula_id=matricula_id, 
            trimestre_id=trimestre_id
        )
        
        # Devolver el promedio y la observación como JSON
        return JsonResponse({
            'success': True,
            'promedioTipo': str(promedio.promedioTipo),
            'observacion': promedio.observacion or 'NINGUNA'
        })

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'success': False, 'error': 'Error al obtener el promedio.'})
    


def obtenerSubpromediosTipos (request, tipo_id, matricula_id, trimestre_id): 
    try:
        # Buscar la instancia de EwuivalentesTipoEvaluacion con los parámetros dados
        subpromedio = get_object_or_404(
            subpromedioTipoEvaluacion, 
            tipoEvaluacion_id=tipo_id, 
            matricula_id=matricula_id, 
            trimestre_id=trimestre_id
        )
        
        # Devolver el promedio y la observación como JSON
        return JsonResponse({
            'success': True,
            'subpromedioTipo': str(subpromedio.evaluacionPromedio),
            'observacion': subpromedio.observacion or 'NINGUNA'
        })

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'success': False, 'error': 'Error al obtener el promedio.'})
    
      
def obtenerAportesTrimestrales(request, claseId, TrimestreId):
    try:
        # Filtra los aportes según la clase y el trimestre
        aportes = obtener_aportes(claseId,TrimestreId)
        
        # Convierte el QuerySet a una lista de diccionarios
        aportes_data = list(aportes.values('id', 'nombre', 'cursoAsignatura_id', 'fecha', 'tipo_id'))  # Cambia los campos según el modelo

        return JsonResponse({'success': True, 'aportes': aportes_data})

    except Exception as e:
        print(f"Error al obtener aportes: {e}")
        return JsonResponse({'success': False, 'error': str(e)})