#import pandas as pd
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from ..models import Usuario,Administrador,PeriodoAcademico,Curso,PeriodoDivision,TipoEvaluacion
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required




# primero debemos renderizar la vista 
def listarTiposEvaluacion(request,periodo_id):   
    # Obtener el periodo académico
    periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)

    # Obtener los trimestres asociados a ese periodo académico
    trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_id)
    
    # Obtener los tipos de evaluación para cada trimestre
    tipos_evaluacion = TipoEvaluacion.objects.filter(trimestre_id__in=trimestres)
    
    # Pasar los datos al template
    context = {
        'periodo_academico': periodo_academico,
        'trimestres': trimestres,
        'tipos_evaluacion': tipos_evaluacion,
        
    }
    
    return render(request,"../templates/TipoEvaluacion/vistaTipoEvaluacion.html",context)


# aqui vamos a crear un tipo de evaluacion pero puede ser multiple
def crearTipoEvaluacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            nombreEvaluacion = data.get("nombreTipo")
            ponderadoTipo = data.get("ponderadoTipo")
            colorTipo = data.get("colorTipo")
            trimestresLista= data.get('trimestres')
            
            if not isinstance(trimestresLista, list):
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El campo "trimestres" debe ser una lista.'
                }, status=400)

            for trimestre_id in trimestresLista:
                try:
                    trimestre = PeriodoDivision.objects.get(id=trimestre_id)
                    # Crear el nuevo tipo de evaluación para cada trimestre
                    TipoEvaluacion.objects.create(
                        nombre=nombreEvaluacion,
                        ponderacion=ponderadoTipo,
                        trimestre_id=trimestre,
                        color=colorTipo,
                        
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
        
# ahora que ya cramo vamos a selecionar un trimestre
def selecionarUnTipoEvaluacion(request, id):
    if request.method == 'GET':
        try:
            tipoEvaluacion = TipoEvaluacion.objects.get(id=id)
            data = {
                'id':tipoEvaluacion.id,
                'nombre': tipoEvaluacion.nombre,
                'ponderacion': tipoEvaluacion.ponderacion,
                'color':tipoEvaluacion.color,
                
                
            }
            return JsonResponse(data, status=200)
        except TipoEvaluacion.DoesNotExist:
            return JsonResponse({'error': 'Tipo de evaluacion no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    


def editarUnTipoEvaluacion(request, id):
    if request.method == 'POST':
        tipoEvaluacion = TipoEvaluacion.objects.get(id=id)
        
        tipoEvaluacion.nombre = request.POST.get('nombreEvaluacion')
        tipoEvaluacion.ponderacion = request.POST.get('ponderadoEvaluacion')
        tipoEvaluacion.color = request.POST.get('colorEvaluacion')
        
        tipoEvaluacion.save()
        
        return JsonResponse({"message": "Tipo de Evaluación actualizado correctamente"})
    return JsonResponse({"error": "Método no permitido"}, status=405)


def eliminarUnTipoEvaluacion(request, id):
    if request.method == 'DELETE':
        try:
            tipoEvaluacion = TipoEvaluacion.objects.get(id=id)
            tipoEvaluacion.delete()
            
            # Verificar si aún quedan tipos de evaluación en el trimestre correspondiente
            hay_tipos_evaluacion = TipoEvaluacion.objects.filter(trimestre_id=tipoEvaluacion.trimestre_id).exists()
            
            return JsonResponse({
                'estado': True, 
                'mensaje': 'Tipo de evaluación eliminado exitosamente.',
                'hay_tipos_evaluacion': hay_tipos_evaluacion
            }, status=200)
        except TipoEvaluacion.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Tipo de evaluación no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    

