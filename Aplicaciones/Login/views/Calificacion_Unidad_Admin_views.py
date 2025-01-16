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


# aqui voy a obtener las calificaciones 
def obtenerCalificacionesUnidadAdmin(request, matricula_id, aporte_id, calificacion_id):
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


def obtenerObservacionUnidadAdmin(request, calificacion_id):
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
    
        
def editarObservacionUnidadAdmin(request, calificacion_id):
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
    