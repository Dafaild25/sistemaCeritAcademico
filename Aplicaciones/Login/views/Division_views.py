#import pandas as pd
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from ..models import ExamenTrimestral, Usuario,Administrador,PeriodoAcademico,Curso,PeriodoDivision,TipoEvaluacion, UnidadTrimestral
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction


#ahora vamos con los trimestres
#  primero mandemos a listar
def listarTrimestres(request,periodo_id):   
    periodo_academico = get_object_or_404(PeriodoAcademico, id=periodo_id)
    trimestres=list(PeriodoDivision.objects.filter(periodo_academico=periodo_id).values())
    return render(request,"../templates/DivisionAcademica/listarTrimestres.html",{'trimestres': trimestres,'periodo_academico': periodo_academico})


# ahora si vamos  a crear un trimestre

def crearTrimestre(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            nombrePeriodo = data.get("nombreTri")
            periodo_id = data.get("periodoTri")
            fechaInicio = data.get("fechaInicioTri")
            fechaFin = data.get("fechaFinTri")
            
            # Obtén el objeto PeriodoAcademico a partir del periodo_id
            periodo_academico = PeriodoAcademico.objects.get(id=periodo_id)

            # Crear el nuevo trimestre
            nuevoTrimestre = PeriodoDivision.objects.create(
                nombre=nombrePeriodo, 
                fecha_inicio=fechaInicio, 
                fecha_fin=fechaFin,
                periodo_academico=periodo_academico  # Usar la instancia aquí
            )
            
            
            # para crear automaticamente los tipos de  evaluaciones
            # Crear automáticamente tipos de evaluación predeterminados
            # Tipos de evaluación predeterminados con colores y ponderaciones
            evaluaciones_predeterminadas = [
                {"nombre": "DEBER", "ponderacion": 10, "color": "#FFFF00"},  # Amarillo
                {"nombre": "TRABAJO GRUPAL", "ponderacion": 10, "color": "#008000"},  # Verde
                {"nombre": "TRABAJO INDIVIDUAL", "ponderacion": 10, "color": "#90EE90"},  # Verde claro
                {"nombre": "LECCION", "ponderacion": 10, "color": "#0000FF"},  # Azul
                {"nombre": "PRUEBA", "ponderacion": 20, "color": "#FFA500"},  # Naranja
                {"nombre": "EXAMEN TRIMESTRAL", "ponderacion": 20, "color": "#00FFFF"},  # Celeste
                {"nombre": "PROYECTOS", "ponderacion": 20, "color": "#FF69B4"},  # Color personalizado (rosa)
            ]
            for eval_data in evaluaciones_predeterminadas:
                if not TipoEvaluacion.objects.filter(
                    nombre=eval_data["nombre"], 
                    trimestre_id=nuevoTrimestre
                ).exists():
                    TipoEvaluacion.objects.create(
                        nombre=eval_data["nombre"], 
                        ponderacion=eval_data["ponderacion"], 
                        color=eval_data["color"],
                        trimestre_id=nuevoTrimestre
                    )
            # Crear unidades predeterminadas para el trimestre
            unidades_predeterminadas = ["Unidad 1", "Unidad 2"]
            for unidad_nombre in unidades_predeterminadas:
                UnidadTrimestral.objects.create(
                    nombre=unidad_nombre,
                    trimestre_id=nuevoTrimestre
                )
            # Crear exámenes predeterminados para el trimestre
            examenes_predeterminados = [
                {"nombre": "Examen Trimestral", "descripcion": nombrePeriodo, "ponderacion": 30},
               
            ]
            for examen_data in examenes_predeterminados:
                ExamenTrimestral.objects.create(
                    nombre=examen_data["nombre"],
                    trimestre_id=nuevoTrimestre,
                    descripcion=examen_data["descripcion"],
                    ponderacion=examen_data["ponderacion"]
                )   
                
                
            return JsonResponse({
                'estado': True,
                'mensaje': 'Trimestre creado exitosamente y tipos de evaluación creados exitosamente.'
            }, status=201)
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({
                'estado': False,
                'mensaje': 'El periodo académico no existe.'
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
        
        
        
# ahora que ya cramo vamos a selecionar un trimestre
def selecionarUnTrimestre(request, id):
    if request.method == 'GET':
        try:
            trimestre = PeriodoDivision.objects.get(id=id)
            data = {
                'id':trimestre.id,
                'nombre': trimestre.nombre,
                'fecha_inicio': trimestre.fecha_inicio,
                'fecha_fin': trimestre.fecha_fin,
                
            }
            return JsonResponse(data, status=200)
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({'error': 'Trimestre no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
    
# ahora que podemos selecionar podemos guardar los cambios
def editarUnTrimestre(request, id):
    data = json.loads(request.body)
    if request.method == 'POST':
        try:
            Trimestre = PeriodoDivision.objects.get(id=id)
            
            Trimestre.nombre = data['nombreTrimestreActualizado']
            Trimestre.fecha_inicio = data['fechaTrimestreInicio']
            Trimestre.fecha_fin = data['fechaTrimestreFin']
            Trimestre.save()
            return JsonResponse({"message": "Periodo actualizado correctamente"})
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({"error": "trimestre no encontrado"}, status=404)
    return JsonResponse({"erro": "Metodo non Permitido"}, status= 405)

#ahora podemos eliminar un tRIMESTRE
def eliminarUnTrimestre(request, id):
    if request.method == 'DELETE':
        try:
            with transaction.atomic():  # Usar una transacción para garantizar que todas las eliminaciones ocurran juntas
                trimestre = PeriodoDivision.objects.get(id=id)
                periodo_academico_id = trimestre.periodo_academico.id

                # Eliminar las relaciones asociadas
                TipoEvaluacion.objects.filter(trimestre_id=trimestre).delete()
                UnidadTrimestral.objects.filter(trimestre_id=trimestre).delete()
                ExamenTrimestral.objects.filter(trimestre_id=trimestre).delete()
                
                # Luego, eliminar el trimestre
                trimestre.delete()

            # Verificar si aún quedan trimestres para el período académico
            hay_trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_academico_id).exists()
            
            return JsonResponse({
                'estado': True, 
                'mensaje': 'Trimestre eliminado exitosamente.',
                'hay_trimestres': hay_trimestres
            }, status=200)
        
        except PeriodoDivision.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Trimestre no encontrado.'}, status=404)
        except Exception as e:
            # Registrar el error para depuración
            print(f"Error al eliminar el trimestre: {e}")
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)