#import pandas as pd
from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from ..models import ExamenFinal, Usuario,Administrador,PeriodoAcademico
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def listarExamenFinal(request,id):  
    # Obtener el periodo académico
    periodo_academico = get_object_or_404(PeriodoAcademico, id=id)

    examenes_finales= ExamenFinal.objects.filter(periodoAcademico_id=periodo_academico)
    
    # Pasar los datos al template
    context = {
        'periodo': periodo_academico,
        'examenes_finales':examenes_finales
        
    }
    return render(request,"../templates/ExamenFinal/vistaExamenFinal.html",context)

# ahora que ya cramo vamos a selecionar un t exmaen del trimestre
def selecionarExamenFinal(request, id):
    if request.method == 'GET':
        try:
            examen_final = ExamenFinal.objects.get(id=id)
            data = {
                'id':examen_final.id,
                'nombre': examen_final.nombre,
                'ponderacion': examen_final.ponderacion,
                'descripcion':examen_final.descripcion,
                'estado':examen_final.estado
                
                
            }
            return JsonResponse(data, status=200)
        except ExamenFinal.DoesNotExist:
            return JsonResponse({'error': 'Examen Final no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
def editarUnExamenFinal(request,id):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            examen_final = ExamenFinal.objects.get(id=id)
            
            examen_final.nombre = data['nombreExamenFinal']
            examen_final.ponderacion = data['ponderadoExamenFinal']
            examen_final.descripcion = data['descripcionExamenFinal']
            # Validamos el estado
            estado_valido = data['estadoExamenFinal'].upper()
            if estado_valido in ["ACTIVO", "INACTIVO"]:
                examen_final.estado = estado_valido
            else:
                return JsonResponse({"error": "Estado no válido. Debe ser 'ACTIVO' o 'INACTIVO'."}, status=400)
            
            
            examen_final.save()
            return JsonResponse({"message": "Examen finalizado correctamente actualizado."}, status=200)
        except ExamenFinal.DoesNotExist:
            return JsonResponse({"error": "Tipo de Evaluación no encontrado."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en el formato JSON."}, status=400)
    return JsonResponse({"error": "Método no permitido."}, status=405)

def crearExamenFinal(request,periodo_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            nombreExamenFinal = data.get("newNombreExamenFinal")
            ponderadoExamenFinal = data.get("newPonderadoExamenFinal")
            descripcionExamenFinal = data.get("newDescripcionExamenFinal")
            estadoExamenFinal = data.get("newEstadoExamenFinal")
           
            
            # Verificar que el estado esté en "ACTIVO" o "INACTIVO"
            if estadoExamenFinal not in ["ACTIVO", "INACTIVO"]:
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El estado debe ser "ACTIVO" o "INACTIVO".'
                }, status=400)

            

            # Convertir `ponderadoExamen` a Decimal
            try:
                ponderadoExamenFinal = Decimal(ponderadoExamenFinal)
            except (ValueError, TypeError):
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El campo "ponderadoExamen" debe ser un número decimal válido.'
                }, status=400)
                
            # Obtener el periodo académico
            try:
                periodo = PeriodoAcademico.objects.get(id=periodo_id)
            except PeriodoAcademico.DoesNotExist:
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'El periodo académico especificado no existe.'
                }, status=404)
                
            # Crear el examen final
            examen_final = ExamenFinal.objects.create(
                nombre=nombreExamenFinal,
                ponderacion=ponderadoExamenFinal,
                descripcion=descripcionExamenFinal,
                estado=estadoExamenFinal,
                periodoAcademico_id =periodo
            )

        
            return JsonResponse({
                'estado': True,
                'mensaje': 'Examenes finales creados exitosamente.'
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
        
def eliminarUnExamenFinal(request, id):
    if request.method == 'DELETE':
        try:
            # Obtener el examen final
            examen_final = ExamenFinal.objects.get(id=id)
            
            
            
            # Eliminar el examen final
            examen_final.delete()
            
           
            
            return JsonResponse({
                'estado': True, 
                'mensaje': 'Examen Final eliminado exitosamente.',
                
            }, status=200)
        except ExamenFinal.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Examen Final no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)