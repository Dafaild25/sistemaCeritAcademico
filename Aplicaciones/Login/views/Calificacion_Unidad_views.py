from collections import defaultdict
from decimal import ROUND_DOWN, Decimal, InvalidOperation,ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db import transaction
from django.db.models import Avg,Count
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Aporte, Calificacion, CursoAsignatura, Matricula, PeriodoDivision, EquivalentesTipoEvaluacion, TipoEvaluacion, UnidadTrimestral, subpromedioTipoEvaluacion


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

def obtener_aportes(trimestre_id, unidad_id, clase_id):
    # Filtra los aportes según el trimestre, la unidad y la clase
    return Aporte.objects.filter(
        tipo_id__trimestre_id=trimestre_id,
        unidad_id=unidad_id,
        cursoAsignatura_id=clase_id
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


def vistaCalificacionUnidad(request, unidad_id, clase_id):
    try:
    
        # Obtén la unidad y el trimestre asociado
        unidad = get_object_or_404(UnidadTrimestral, id=unidad_id)
        trimestre = unidad.trimestre_id  # Accede al trimestre relacionado
        clase = get_object_or_404(CursoAsignatura, id=clase_id)

        # Obtén los estudiantes matriculados en la clase
        matriculas = obtener_matriculas(clase)
        
        # Obtén los tipos de evaluación del trimestre
        tipos_evaluacion = obtener_tipos_evaluacion(trimestre)

        # Llama a la función para obtener los aportes relacionados con el trimestre, la unidad y la clase
        aportes = obtener_aportes(trimestre.id, unidad.id, clase_id)
        
        # Obtén las calificaciones para cada estudiante y cada aporte
        calificaciones = Calificacion.objects.filter(matricula_id__in=matriculas, aporte_id__in=aportes)
        
        # Crear diccionario y lista de calificaciones
        calificaciones_dict = crear_calificaciones_dict(calificaciones)
        calificaciones_list = crear_calificaciones_list(matriculas, aportes, calificaciones_dict,calificaciones)
    
        # Pasar los datos al template
        context = {
            'unidad': unidad,
            'trimestre': trimestre,
            'clase': clase,
            'matriculas': matriculas,
            'tipos_evaluacion': tipos_evaluacion,
            'aportes': aportes,
            'calificaciones_list': calificaciones_list,
        }

        return render(request, '../templates/Docente/vistaCalificacionUnidad.html', context)
    
    except Exception as e:
        print(f"Error en claseTrabajo: {e}")
        return HttpResponseServerError("Error en el servidor.")