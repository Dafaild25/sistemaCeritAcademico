
from collections import defaultdict
from decimal import ROUND_DOWN, Decimal, InvalidOperation,ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db import IntegrityError, transaction
from django.db.models import Avg,Count
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Aporte, Calificacion, CalificacionExamen, CalificacionExamenSupletorio, CursoAsignatura, ExamenFinal, ExamenTrimestral, Matricula, PeriodoAcademico, PeriodoDivision, EquivalentesTipoEvaluacion, PromedioTrimestres, PromedioTrimestresAsignatura, PromedioUnidades, TipoEvaluacion, UnidadTrimestral, subpromedioTipoEvaluacion

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

def vistaCalificacionGeneral(request, periodo_id, clase_id):
    try:
        periodo = PeriodoAcademico.objects.get(id=periodo_id)
        # Obtener los trimestres asociados al periodo
        trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_id)
        
       
        # Verificar si hay trimestres disponibles
        if not trimestres.exists():
            return render(request, 'error.html', {'message': 'No hay trimestres asociados a este periodo.'})

        # Obtener la clase
        clase = get_object_or_404(CursoAsignatura, id=clase_id)
        
        examenesFinales = ExamenFinal.objects.filter(periodoAcademico_id = periodo_id)

        # Obtener las matrículas de la clase
        matriculas = obtener_matriculas(clase)
        promedioPorTrimestre = calcularPromedioClasePorTrimestre(clase_id,periodo_id)
        
        promedios = PromedioTrimestres.objects.filter(trimestre_id__in=trimestres, curso_asignatura_id=clase_id)

        # Contexto para la plantilla
        context = {
            'trimestres': trimestres,
            'clase': clase,
            'matriculas': matriculas,
            'promedios': promedios,
            'examenesFinales':examenesFinales,
            'promediosPorTrimestre':promedioPorTrimestre,
            'periodoGeneral':periodo,
        }

        return render(request, 'Docente/vistaCalificacionGeneral.html', context)

    except Exception as e:
        print(f"Error en vistaCalificacionGeneral: {e}")
        return HttpResponseServerError("Error en el servidor.")
    
def obtenerPromediosGeneralesTrimestrales(request, matricula_id, trimestre_id, clase_id, periodo_id):
    try:
        
        # Filtrar la calificación específica
        calificacion = PromedioTrimestres.objects.filter(
            matricula_id=matricula_id,
            trimestre_id=trimestre_id,
            curso_asignatura_id=clase_id
        ).first()

        # Si no existe la calificación, asignar valores predeterminados
        if not calificacion:
            print("Calificación no encontrada. Asignando valores predeterminados.")
            data = {
                'id': None,
                'matricula_id': matricula_id,
                'trimestre_id': trimestre_id,
                'nota': "0.00",  # Valor predeterminado
                'observacion': None,
                
            }
            return JsonResponse({'success': True, 'data': data})

        # Obtener la cantidad de decimales desde el periodo académico
        periodo_academico = PeriodoAcademico.objects.get(id=periodo_id)
        cantidad_decimal = periodo_academico.cantidad  # Este es el valor que necesitas
       
        # Si la calificación tiene un promedio trimestral, usarlo; de lo contrario, asignar 0.00
        promedioTrimestral = calificacion.promedioTrimestral if calificacion.promedioTrimestral is not None else Decimal('0.00')

        # Redondear el promedio según la cantidad de decimales configurada en el periodo académico
        promedioTrimestral = promedioTrimestral.quantize(Decimal('1.' + '0' * cantidad_decimal))

        # Preparar los datos de la calificación en formato JSON
        data = {
            'id': calificacion.id,
            'matricula_id': calificacion.matricula_id.id,
            'trimestre_id': calificacion.trimestre_id.id,
            'nota': str(promedioTrimestral),  
            'observacion': calificacion.observacion,
            
        }

        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        # Si hay un error, devolver un mensaje adecuado
        return JsonResponse({'success': False, 'error': str(e)})


def obtenerPromediosGenerales(request, matricula_id, clase_id, periodo_id):
    try:
        # Filtrar la calificación específica
        calificacion = PromedioTrimestresAsignatura.objects.filter(
            matricula_id=matricula_id,
            curso_asignatura_id=clase_id

        ).first()

        # Si no existe la calificación, asignar valores predeterminados
        if not calificacion:
            print("Calificación no encontrada. Asignando valores predeterminados.")
            data = {
                'id': None,
                'matricula_id': matricula_id,
                'nota': "0.00",  # Valor predeterminado
                'observacion': None
            }
            return JsonResponse({'success': True, 'data': data})
        periodo_academico = PeriodoAcademico.objects.get(id=periodo_id)
        cantidad_decimal = periodo_academico.cantidad  # Este es el valor que necesitas
        # Si la calificación tiene un promedio trimestral, usarlo; de lo contrario, asignar 0.00
        promedioTrimestralAsignatura = calificacion.promedioTrimestral if calificacion.promedioTrimestral is not None else Decimal('0.00')

        promedioRedondeado = promedioTrimestralAsignatura.quantize(Decimal('1.' + '0' * cantidad_decimal))
        # Preparar los datos de la calificación en formato JSON
        data = {
            'id': calificacion.id,
            'matricula_id': calificacion.matricula_id.id,
            'nota': str(promedioRedondeado),  
            'observacion': calificacion.observacion
        }

        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        # Si hay un error, devolver un mensaje adecuado
        return JsonResponse({'success': False, 'error': str(e)})


# Promedios  totales de las columnas del promedio general 
def calcularPromedioClaseGeneral(request, clase_id):
    
    datos = PromedioTrimestresAsignatura.objects.filter(
        curso_asignatura_id=clase_id,
        matricula_id__estado='ACTIVO'  # Filtro para matrícula activa
    )
    suma_total = datos.aggregate(suma=Sum('promedioTrimestral'))['suma'] or 0
    cantidad = datos.aggregate(cuenta=Count('id'))['cuenta']
    
    # Calcular el promedio o devolver 0 si no hay datos
    promedio = suma_total / cantidad if cantidad > 0 else 0 
    # Recuperar el número de decimales desde el PeriodoAcademico
    periodo = datos.first().periodoAcademico_id if datos.exists() else None
    decimales = periodo.cantidad if periodo and periodo.cantidad else 2  

    # Formatear el promedio con el número de decimales especificado
    promedio_formateado = round(promedio, decimales)

    # Retornar el promedio en formato JSON
    return JsonResponse({'curso_asignatura_id': clase_id, 'promedio': promedio_formateado})

def calcularPromedioClasePorTrimestre(clase_id, periodo_id):
    # Filtrar los datos por curso_asignatura_id y periodo_id
    datos = PromedioTrimestres.objects.filter(
        curso_asignatura_id=clase_id,
        matricula_id__estado='ACTIVO'
    )
    
    # Filtrar los trimestres por periodo_id
    trimestres = PeriodoDivision.objects.filter(periodo_academico_id=periodo_id)
    
    # Crear una lista para almacenar los resultados con los promedios redondeados
    promedios = []
    
    # Obtener el número de decimales directamente desde el PeriodoAcademico
    periodo_academico = PeriodoAcademico.objects.get(id=periodo_id)
    cantidad_decimales = periodo_academico.cantidad
    
    # Recorrer todos los trimestres asociados al periodo académico
    for trimestre in trimestres:
        # Calcular el promedio para el trimestre actual
        promedio_trimestre = datos.filter(trimestre_id=trimestre.id).aggregate(
            promedio=Avg('promedioTrimestral')
        )['promedio']
        
        # Si no se encuentra un promedio, asignar 0.00
        if promedio_trimestre is None:
            promedio_trimestre = 0.00
        
        # Redondear el promedio al número de decimales indicado
        promedio_redondeado = round(promedio_trimestre, cantidad_decimales)
        
        # Agregar el resultado a la lista
        promedios.append({
            'trimestre_id': trimestre.id,
            'promedio': promedio_redondeado
        })
    
    return promedios



def obtenerMatriculasParaSupletorio(request, clase_id, matricula_id):
    try:
        # Filtrar los registros con el curso_asignatura_id y matricula_id especificados
        promedios = PromedioTrimestresAsignatura.objects.filter(curso_asignatura_id=clase_id, matricula_id=matricula_id)

        # Verificar si existen registros
        if not promedios.exists():
            print("No se encontraron registros para la clase o matrícula proporcionada.")
            return JsonResponse({'success': True, 'data': []})

        # Preparar los datos de cada registro
        data = []
        for promedio in promedios:
            # Obtener el promedio trimestral o asignar 0.00 si es None
            promedio_trimestral = promedio.promedioTrimestral if promedio.promedioTrimestral is not None else Decimal('0.00')

            # Redondear el promedio a los decimales configurados en el periodo académico
            cantidad_decimal = promedio.periodoAcademico_id.cantidad
            promedio_trimestral = promedio_trimestral.quantize(Decimal('1.' + '0' * cantidad_decimal))

            # Determinar si el campo debe estar habilitado o no
            enabled = promedio_trimestral < Decimal('7.00')

            # Añadir el registro al resultado
            data.append({
                'id': promedio.id,
                'matricula_id': promedio.matricula_id.id,
                'curso_asignatura_id': promedio.curso_asignatura_id.id,
                'periodoAcademico_id': promedio.periodoAcademico_id.id,
                'nota': str(promedio_trimestral),
                'observacion': promedio.observacion,
                'enabled': enabled,  # Nuevo campo para indicar si se habilita o no
            })

        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        # Si hay un error, devolver un mensaje adecuado
        return JsonResponse({'success': False, 'error': str(e)})



def guardarExamenSupletorio(request):
    if request.method == "POST":
        # Obtener los datos del formulario
        matricula_id = request.POST.get('matricula_id')
        examen_id = request.POST.get('examen_id')
        curso_asignatura_id = request.POST.get('curso_asignatura_id', None)
        nota = request.POST.get('nota')
        observacion = request.POST.get('observacion', 'NINGUNA')

        # Validar que la nota no esté vacía o sea None
        if not nota:
            return JsonResponse({"success": False, "message": "La calificación no puede estar vacía."})

        # Validar que la nota esté en el rango de 0 a 10
        try:
            nota = Decimal(nota)
            if nota < 0 or nota > 10:
                return JsonResponse({"success": False, "message": "La calificación debe estar entre 0 y 10."})
        except (ValueError, InvalidOperation):
            return JsonResponse({"success": False, "message": "La calificación no es válida."})

        # Validar que los campos obligatorios no estén vacíos
        if not matricula_id or not examen_id:
            return JsonResponse({"success": False, "message": "Todos los campos son obligatorios."})

        try:
            # Obtener las instancias relacionadas
            matricula = Matricula.objects.get(id=matricula_id)
            examen = ExamenFinal.objects.get(id=examen_id)
            curso_asignatura = CursoAsignatura.objects.get(id=curso_asignatura_id) if curso_asignatura_id else None

            # Verificar si ya existe una calificación para este examen, matrícula y curso
            calificacion_registro = CalificacionExamenSupletorio.objects.filter(
                matricula_id=matricula,
                examen_id=examen,
                curso_asignatura_id=curso_asignatura
            ).first()

            if calificacion_registro:
                # Si ya existe, actualizar el registro
                calificacion_registro.nota = nota
                calificacion_registro.observacion = observacion
                calificacion_registro.save()
                return JsonResponse({"success": True, "message": "Calificación actualizada correctamente."})
            else:
                # Si no existe, crear un nuevo registro
                calificacion_registro = CalificacionExamenSupletorio(
                    matricula_id=matricula,
                    examen_id=examen,
                    curso_asignatura_id=curso_asignatura,
                    nota=nota,
                    observacion=observacion
                )
                calificacion_registro.save()
                return JsonResponse({"success": True, "message": "Calificación guardada correctamente."})

        except Matricula.DoesNotExist:
            return JsonResponse({"success": False, "message": "Matrícula no encontrada."})
        except ExamenFinal.DoesNotExist:
            return JsonResponse({"success": False, "message": "Examen no encontrado."})
        except CursoAsignatura.DoesNotExist:
            return JsonResponse({"success": False, "message": "Curso o asignatura no encontrado."})
        except IntegrityError:
            return JsonResponse({"success": False, "message": "Error al guardar o actualizar la calificación."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

def obtenerCalificacionSupletorio(request, examen_id, matricula_id, clase_id):
    # Recuperar las calificaciones para el examen, matrícula y clase dados
    calificaciones = CalificacionExamenSupletorio.objects.filter(
        examen_id=examen_id,
        matricula_id=matricula_id,
        curso_asignatura_id=clase_id
    )

    # Crear una lista para almacenar los datos que devolveremos
    calificaciones_data = []

    # Iterar sobre las calificaciones y preparar los datos para la respuesta
    for calificacion in calificaciones:
        calificaciones_data.append({
            'matricula_id': calificacion.matricula_id.id,
            'clase_id': calificacion.curso_asignatura_id.id,
            'nota': calificacion.nota,
            'observacion': calificacion.observacion,
        })

    # Devolver los datos en formato JSON
    return JsonResponse({'calificaciones': calificaciones_data})