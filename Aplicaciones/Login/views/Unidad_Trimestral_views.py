#import pandas as pd
from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from ..models import Usuario,Administrador,PeriodoAcademico,Curso,PeriodoDivision,UnidadTrimestral
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

#primero debemos renderizar la vista 
def listarUnidadesTrimestrales(request,periodo_id):   
    # Obtener el periodo académico
    periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)

    # Obtener todos los trimestres y sus exámenes trimestrales relacionados
    trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_academico).prefetch_related('examentrimestral_set')
    
    # Filtrar exámenes trimestrales correspondientes a esos trimestres
    unidades_trimestrales = UnidadTrimestral.objects.filter(trimestre_id__in=trimestres)
    
    # Pasar los datos al template
    context = {
        'periodo_academico': periodo_academico,
        'trimestres': trimestres,
        'unidades_trimestrales':unidades_trimestrales
        
    }
    
    return render(request,"../templates/UnidadTrimestral/vistaUnidadTrimestral.html",context)

def selecionarUnidadTrimestral(request, id):
    if request.method == 'GET':
        try:
            unidad_trimestal = UnidadTrimestral.objects.get(id=id)
            data = {
                'id':unidad_trimestal.id,
                'nombre': unidad_trimestal.nombre,
                
            }
            return JsonResponse(data, status=200)
        except UnidadTrimestral.DoesNotExist:
            return JsonResponse({'error': 'Unidad no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    

def editarUnidadTrimestral(request,id):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unidadTrimestral = UnidadTrimestral.objects.get(id=id)
            
            unidadTrimestral.nombre = data['nombreUnidad']
        
            
            
            unidadTrimestral.save()
            return JsonResponse({"message": "Unidad Trimestral correctamente actualizado."}, status=200)
        except UnidadTrimestral.DoesNotExist:
            return JsonResponse({"error": "Unidad Trimestral no encontrado."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en el formato JSON."}, status=400)
    return JsonResponse({"error": "Método no permitido."}, status=405)


def crearUnidadTrimestral(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            nombreUnidad = data.get("nombreUnidad")
            trimestresLista= data.get('trimestres')
        
                        # Validación de campos requeridos
            if not all([nombreUnidad]):
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'Todos los campos son obligatorios.'
                }, status=400)

            
            for trimestre_id in trimestresLista:
                try:
                    trimestre = PeriodoDivision.objects.get(id=trimestre_id)
                    # Crear el nuevo tipo de evaluación para cada trimestre
                    UnidadTrimestral.objects.create(
                        nombre=nombreUnidad,                    
                        trimestre_id=trimestre,
                    
                        
                    )
                except PeriodoDivision.DoesNotExist:
                    return JsonResponse({
                        'estado': False,
                        'mensaje': f'El Trimestre con ID {trimestre_id} no existe.'
                    }, status=404)

            return JsonResponse({
                'estado': True,
                'mensaje': 'Tipos de Evaluación creados exitosamente.'
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
        
        
def eliminarUnidadTrimestral(request, id):
    if request.method == 'DELETE':
        try:
            unidad_trimestral = UnidadTrimestral.objects.get(id=id)
            unidad_trimestral.delete()
            return JsonResponse({'estado': True, 'mensaje': 'Unidad Trimestral eliminada exitosamente.'}, status=200)
        except UnidadTrimestral.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Unidad Trimestral no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)