from collections import defaultdict
from decimal import ROUND_DOWN, Decimal, InvalidOperation,ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db import transaction
from django.db.models import Avg,Count
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Aporte, Calificacion, CalificacionExamen, CursoAsignatura, ExamenTrimestral, Matricula, PeriodoDivision, EquivalentesTipoEvaluacion, PromedioTrimestres, PromedioUnidades, TipoEvaluacion, UnidadTrimestral, subpromedioTipoEvaluacion

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

def vistaCalificacionTrimestre(request, trimestre_id, clase_id):
    try:
        # Obtener el trimestre y la clase
        trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
        clase = get_object_or_404(CursoAsignatura, id=clase_id)

        # Obtener las matrículas de la clase
        matriculas = obtener_matriculas(clase)  # Asegúrate de que esta función esté bien definida

        # Obtener las unidades del trimestre utilizando el nombre correcto del campo
        unidades = UnidadTrimestral.objects.filter(trimestre_id=trimestre_id)
        
        examenes =ExamenTrimestral.objects.filter(trimestre_id=trimestre_id)
        promedios = PromedioTrimestres.objects.filter(trimestre_id=trimestre_id)

        # Pasar los datos al contexto del template
        context = {
            'trimestre': trimestre,
            'clase': clase,
            'matriculas': matriculas,
            'unidades': unidades,
            'examenes':examenes,
            'promedios':promedios,
            
        }

        return render(request, 'Docente/vistaCalificacionTrimestre.html', context)
    
    except Exception as e:
        print(f"Error en vistaCalificacionTrimestre: {e}")
        return HttpResponseServerError("Error en el servidor.")
    
def obtenerSubPromedioUnidad(request, unidad_id, matricula_id, trimestre_id,clase_id):
    try:
        # Obtener la calificación correspondiente a la unidad, matricula y trimestre
        calificacion = PromedioUnidades.objects.filter(
            unidad_id=unidad_id,
            matricula_id=matricula_id,
            trimestre_id=trimestre_id,
            curso_asignatura_id=clase_id
        ).first()

        # Si no existe la calificación, devolver un valor predeterminado
        subPromedio = calificacion.subPromedioUnidad if calificacion else 0
        
        # Obtener el trimestre y el periodo académico relacionado
        trimestre = PeriodoDivision.objects.filter(id=trimestre_id).first()
        if trimestre and trimestre.periodo_academico:
            decimales = trimestre.periodo_academico.cantidad
        else:
            # Valor predeterminado si no hay configuración en el periodo académico
            decimales = 2  
            
        # Ajustar el subPromedio a los decimales configurados
        subPromedio = Decimal(subPromedio).quantize(Decimal(f"1.{'0' * decimales}"), rounding=ROUND_DOWN)

        return JsonResponse({'subPromedio': subPromedio})
    
    except Exception as e:
        print(f"Error en obtenerSubPromedioUnidad: {e}")
        return JsonResponse({'error': 'Error al obtener la calificación'}, status=500)
    
# AQUI QUIERO GUARDAR LAS CALIFICACIONES 
def calificacionExamenTrimestral(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calificaciones = data.get('calificaciones', [])

            for calificacion_data in calificaciones:
                matricula_id = calificacion_data.get('matricula_id')
                examen_id = calificacion_data.get('examen_id')
                curso_asignatura_id=calificacion_data.get('clase_id')
                nota = calificacion_data.get('nota')

                print(f"matricula_id: {matricula_id}, examen_id: {examen_id}, nota: {nota}")  # Para depuración

                # Validar los IDs de matrícula y examen
                if matricula_id is None or examen_id is None:
                    return JsonResponse({'success': False, 'error': 'ID de matrícula o examen no puede ser None.'})

                # Obtener la matrícula y el examen
                matricula = get_object_or_404(Matricula, id=matricula_id)
                examen = get_object_or_404(ExamenTrimestral, id=examen_id)
                clase=get_object_or_404(CursoAsignatura, id=curso_asignatura_id)

                # Validar y convertir nota a Decimal
                if isinstance(nota, (int, float, str)):
                    try:
                        nota = Decimal(str(nota).strip())
                        if nota < Decimal('0.00') or nota > Decimal('10.00'):
                            return JsonResponse({'success': False, 'error': 'La nota debe estar entre 0.00 y 10.00.'})
                    except (ValueError, InvalidOperation):
                        return JsonResponse({'success': False, 'error': 'El valor de la nota no es válido.'})
                else:
                    return JsonResponse({'success': False, 'error': 'El valor de la nota debe ser un número.'})

                # Crear o actualizar la calificación del examen trimestral
                CalificacionExamen.objects.update_or_create(
                    matricula_id=matricula,  # Asegúrate de que estas claves coincidan con tu modelo
                    examen_id=examen,
                    curso_asignatura_id=clase,
                    defaults={
                        'nota': nota,
                        'observacion': 'NINGUNA'  # Cambiar según sea necesario
                    }
                )

            return JsonResponse({'success': True, 'message': 'Calificaciones guardadas exitosamente.'})

        except Exception as e:
            print('Error:', str(e))  # Agrega aquí un log más detallado si es necesario
            return JsonResponse({'success': False, 'error': 'Ocurrió un error al procesar la solicitud.'})

    return JsonResponse({'success': False, 'error': 'Método de solicitud inválido'})


#Funcion para listar las calificaciones  de los examenes trimestrales 
def obtenerCalificacionExamenTrimestral(request, matricula_id, examen_id, clase_id):
    try:
        
        
        # Filtrar la calificación específica
        calificacion = CalificacionExamen.objects.filter(
            matricula_id=matricula_id,
            examen_id=examen_id,
            curso_asignatura_id=clase_id
        ).first()

        # Si no existe la calificación, asignar valores predeterminados
        if not calificacion:
            print("Calificación no encontrada. Asignando valores predeterminados.")
            data = {
                'id': None,
                'matricula_id': matricula_id,
                'examen_id': examen_id,
                'nota': "0.00",  # Valor predeterminado
                'observacion': None
            }
            return JsonResponse({'success': True, 'data': data})

        # Si la nota no está presente, asignar 0.00
        nota = calificacion.nota if calificacion.nota is not None else Decimal('0.00')

        # Preparar los datos de la calificación en formato JSON
        data = {
            'id': calificacion.id,
            'matricula_id': calificacion.matricula_id.id,
            'examen_id': calificacion.examen_id.id,
            'nota': str(nota),
            'observacion': calificacion.observacion
        }

        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        
        return JsonResponse({'success': False, 'error': str(e)})
    
def obtenerPromedioTrimestral(request, matricula_id, trimestre_id, clase_id):
    try:
        print(f"Solicitud recibida: matricula_id={matricula_id}, trimestre_id={trimestre_id}, clase_id={clase_id}")
        
        # Verificar si el trimestre existe
        trimestre = PeriodoDivision.objects.filter(id=trimestre_id).select_related('periodo_academico').first()
        if not trimestre:
            print("Trimestre no encontrado.")
            return JsonResponse({'success': False, 'error': 'Trimestre no encontrado.'})

        # Obtener la cantidad de decimales configurada en el periodo académico
        decimales = trimestre.periodo_academico.cantidad if trimestre.periodo_academico else 2

        # Buscar el promedio trimestral
        try:
            promedio = PromedioTrimestres.objects.get(
                matricula_id=matricula_id,
                trimestre_id=trimestre_id,
                curso_asignatura_id=clase_id
            )
            promedio_valor = promedio.promedioTrimestral
            observacion = promedio.observacion
        except PromedioTrimestres.DoesNotExist:
            print("Promedio no encontrado en la base de datos. Se asigna 0.00.")
            promedio_valor = Decimal('0.00')
            observacion = "Sin datos"

        # Ajustar el promedio a los decimales configurados
        promedio_ajustado = Decimal(promedio_valor).quantize(
            Decimal(f"1.{'0' * decimales}"), rounding=ROUND_DOWN
        )

        print(f"Promedio encontrado o asignado: {promedio_valor}, Ajustado: {promedio_ajustado}")

        # Preparar los datos para la respuesta
        data = {
            'id': promedio.id if 'promedio' in locals() else None,
            'matricula_id': matricula_id,
            'trimestre_id': trimestre_id,
            'nota': str(promedio_ajustado),
            'observacion': observacion
        }
        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        print(f"Error inesperado: {e}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor.'})
    
    
# funcion para  obtener una calificaciones
def obtenerObservacionExamen(request, calificacion_id):
    try:
        # Obtener la calificación por su ID
        calificacion = CalificacionExamen.objects.get(id=calificacion_id)
        # Retornar la observación en un JsonResponse
        return JsonResponse({
            'observacion': calificacion.observacion,
        })
    except Calificacion.DoesNotExist:
        return JsonResponse({
            'error': 'Calificación no encontrada'
        }, status=404)
        
def editarObservacionExamen(request, calificacion_id):
    if request.method == 'POST':
        try:
            calificacion = CalificacionExamen.objects.get(id=calificacion_id)
            observacion = request.POST.get('observacion', '')
            calificacion.observacion = observacion
            calificacion.save()
            return JsonResponse({'status': 'success'})
        except Calificacion.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Calificación no encontrada'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        JsonResponse({'status': 'error', 'message': 'Método no permitido'})