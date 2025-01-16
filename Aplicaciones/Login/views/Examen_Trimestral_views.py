#import pandas as pd
from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from ..models import Usuario,Administrador,PeriodoAcademico,Curso,PeriodoDivision,ExamenTrimestral
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

#primero debemos renderizar la vista 
def listarExamenesTrimestrales(request,periodo_id):   
    # Obtener el periodo académico
    periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)

    # Obtener todos los trimestres y sus exámenes trimestrales relacionados
    trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_academico).prefetch_related('examentrimestral_set')
    
    # Filtrar exámenes trimestrales correspondientes a esos trimestres
    examenes_trimestrales = ExamenTrimestral.objects.filter(trimestre_id__in=trimestres)
    
    # Pasar los datos al template
    context = {
        'periodo_academico': periodo_academico,
        'trimestres': trimestres,
        'examenes_trimestrales':examenes_trimestrales
        
    }
    
    return render(request,"../templates/ExamenTrimestral/vistaExamenTrimestral.html",context)


# ahora que ya cramo vamos a selecionar un t exmaen del trimestre
def selecionarExamenTrimestral(request, id):
    if request.method == 'GET':
        try:
            examen_trimestal = ExamenTrimestral.objects.get(id=id)
            data = {
                'id':examen_trimestal.id,
                'nombre': examen_trimestal.nombre,
                'ponderacion': examen_trimestal.ponderacion,
                'descripcion':examen_trimestal.descripcion,
                'estado':examen_trimestal.estado
                
                
            }
            return JsonResponse(data, status=200)
        except ExamenTrimestral.DoesNotExist:
            return JsonResponse({'error': 'Examen no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
def editarUnExamenTrimestral(request,id):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            examenTrimestral = ExamenTrimestral.objects.get(id=id)
            
            examenTrimestral.nombre = data['nombreExamen']
            examenTrimestral.ponderacion = data['ponderadoExamen']
            examenTrimestral.descripcion = data['descripcionExamen']
            # Validamos el estado
            estado_valido = data['estadoExamen'].upper()
            if estado_valido in ["ACTIVO", "INACTIVO"]:
                examenTrimestral.estado = estado_valido
            else:
                return JsonResponse({"error": "Estado no válido. Debe ser 'ACTIVO' o 'INACTIVO'."}, status=400)
            
            
            examenTrimestral.save()
            return JsonResponse({"message": "Tipo de Evaluación correctamente actualizado."}, status=200)
        except ExamenTrimestral.DoesNotExist:
            return JsonResponse({"error": "Tipo de Evaluación no encontrado."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en el formato JSON."}, status=400)
    return JsonResponse({"error": "Método no permitido."}, status=405)



def crearExamenTrimestral(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            nombreExamen = data.get("nombreExamen")
            ponderadoExamen = data.get("ponderadoExamen")
            descripcionExamen = data.get("descripcionExamen")
            estadoExamen = data.get("estadoExamen")
            trimestresLista= data.get('trimestres')
            
                        # Validación de campos requeridos
            if not all([nombreExamen, ponderadoExamen, trimestresLista]):
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'Todos los campos son obligatorios.'
                }, status=400)

            # Verificar que el estado esté en "ACTIVO" o "INACTIVO"
            if estadoExamen not in ["ACTIVO", "INACTIVO"]:
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El estado debe ser "ACTIVO" o "INACTIVO".'
                }, status=400)

            # Validación de tipo de `trimestresLista`
            if not isinstance(trimestresLista, list):
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El campo "trimestres" debe ser una lista.'
                }, status=400)

            # Convertir `ponderadoExamen` a Decimal
            try:
                ponderadoExamen = Decimal(ponderadoExamen)
            except (ValueError, TypeError):
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El campo "ponderadoExamen" debe ser un número decimal válido.'
                }, status=400)

            for trimestre_id in trimestresLista:
                try:
                    trimestre = PeriodoDivision.objects.get(id=trimestre_id)
                    # Crear el nuevo tipo de evaluación para cada trimestre
                    ExamenTrimestral.objects.create(
                        nombre=nombreExamen,
                        ponderacion=ponderadoExamen,
                        trimestre_id=trimestre,
                        descripcion = descripcionExamen,
                        estado=estadoExamen
                        
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
        
def eliminarUnExamenTrimestral(request, id):
    if request.method == 'DELETE':
        try:
            examen_trimestral = ExamenTrimestral.objects.get(id=id)
            examen_trimestral.delete()
            
            # Verificar si aún quedan tipos de evaluación en el trimestre correspondiente
            hay_examenes = ExamenTrimestral.objects.filter(trimestre_id=examen_trimestral.trimestre_id).exists()
            
            return JsonResponse({
                'estado': True, 
                'mensaje': 'Examen Trimestral eliminado exitosamente.',
                'hay_examenes': hay_examenes
            }, status=200)
        except ExamenTrimestral.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Examen Trimestral no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)