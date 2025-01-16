#import pandas as pd
from django.contrib import messages
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from ..models import ExamenFinal, Usuario,Administrador,PeriodoAcademico,Curso
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def vistaPeriodo(request):
    
    cursos = Curso.objects.all()
    periodos =PeriodoAcademico.objects.all()
    
    user = request.user
    print(f"Usuario autenticado: {user.username}")

    try:
        admin = user.admin  # Intentamos acceder al perfil de docente
        nombre_admin = f' {admin.apellido_Paterno} {admin.apellido_Materno} {admin.primer_nombre} {admin.segundo_nombre}'
        print(f"Perfil de Administrador encontrado: {nombre_admin}")
    except Administrador.DoesNotExist:
        admin = None
        nombre_admin = user.username  # En caso de que no exista perfil de docente
        print("Perfil de Administrador no encontrado.")
    
    context = {
        'nombre_admin': nombre_admin,
        'admin': admin,  
        'cursos': cursos,
        'periodos':periodos
    }
    print(f"Contexto enviado a la plantilla: {context}")
    return render(request,'../templates/PeriodosAcademicos/vistaPeriodo.html',context)

#  crear un periodo academico
def crearPeriodo(request):
    if request.method =='POST':
        try:
            data=json.loads(request.body) 
            nombrePeriodo = data.get("nombrePeriodo")
            descripcion = data.get("descripcion")
            cantidad = data.get("decimasPeriodo")
            fechaInicio = data.get("fechaInicio")
            fechaFin =data.get("fechaFin")
            estado =data.get("estado")
            
            
            # Validar que no exista un período activo en las mismas fechas
            if PeriodoAcademico.objects.filter(
                fecha_inicio__lte=fechaFin,
                fecha_fin__gte=fechaInicio,
                estado='ACTIVO'
            ).exists():
                return JsonResponse({
                    'estado': False,
                    'mensaje': 'Ya existe un período académico activo en el rango de fechas proporcionado.'
                }, status=400)
            
            
            

            # Crear el nuevo período académico
            nuevoPeriodo = PeriodoAcademico.objects.create(
                nombre=nombrePeriodo, 
                descripcion=descripcion,
                cantidad=cantidad,
                fecha_inicio=fechaInicio,
                fecha_fin=fechaFin,
                estado=estado
            )
            
            # Crear automáticamente los cursos asociados al nuevo período académico
            cursos_predefinidos = [
                {"nombre": "Inicial 1", "paralelo": "A"},
                {"nombre": "Inicial 2", "paralelo": "A"},
                {"nombre": "Primero", "paralelo": "A"},
                {"nombre": "Segundo", "paralelo": "A"},
                {"nombre": "Tercero", "paralelo": "A"},
                {"nombre": "Cuarto", "paralelo": "A"},
                {"nombre": "Quinto", "paralelo": "A"},
                {"nombre": "Sexto", "paralelo": "A"},
                {"nombre": "Septimo", "paralelo": "A"},
                {"nombre": "Octavo", "paralelo": "A"},
                {"nombre": "Noveno", "paralelo": "A"},
                {"nombre": "Decimo", "paralelo": "A"},
            ]
            
            for curso in cursos_predefinidos:
                Curso.objects.create(
                    nombre=curso['nombre'],
                    paralelo=curso['paralelo'],
                    periodoAcademico_id=nuevoPeriodo,
                    estado='ACTIVO',
                    descripcion=f"Curso de {curso['nombre']} para el período {nombrePeriodo}"
                )
            
             # Crear los exámenes finales por defecto
            examenes_nombres = ['Supletorio', 'Remedial', 'Gracia']
            for nombre_examen in examenes_nombres:
                ExamenFinal.objects.create(
                    nombre=nombre_examen,
                    periodoAcademico_id=nuevoPeriodo,
                    descripcion='Examen creado automáticamente',
                    ponderacion=10.0,  # Ponderación solicitada
                    estado='ACTIVO'  # Estado "ACTIVO" por defecto
                )
            
            return JsonResponse({
                'estado': True,
                'mensaje': 'Periodo Academico creado exitosamente.'
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({
                'estado': False,
                'mensaje': 'Error en el formato del JSON.'
            },status=400)
        except Exception as e:
            return JsonResponse({
                'estado': False,
                'mensaje': f'Error: {str(e)}'
            }, status =500)
    else:
        return JsonResponse({
            'estado': False,
            'mensaje': 'Método no permitido.'
        },status=405)
        
# listar todos los periodos
def listarPeriodo(request):
    if request.method == 'GET':
        try:
            periodos = PeriodoAcademico.objects.all()
            return render(request,'../templates/PeriodosAcademicos/listarPeriodo.html', {'periodos': periodos})
        # tener en cuenta para los cambios 
        except Exception as e:
            return JsonResponse({
                'estado': False,
                'mensaje': f'Error: {str(e)}'}, status=500
            )
# seleccionar un periodo
def selecionarUnPeriodo(request, id):
    if request.method == 'GET':
        try:
            periodo = PeriodoAcademico.objects.get(id=id)
            data = {
                'id':periodo.id,
                'nombre': periodo.nombre,
                'descripcion': periodo.descripcion,
                'cantidad':periodo.cantidad,
                'fecha_inicio': periodo.fecha_inicio,
                'fecha_fin': periodo.fecha_fin,
                'estado': periodo.estado,
            }
            return JsonResponse(data, status=200)
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({'error': 'Periodo no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
    
# editar un periodo academico
def editarUnPeriodo(request, id):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            periodo = PeriodoAcademico.objects.get(id=id)
            

                
            # Verificar si hay conflictos de fechas
            fecha_inicio = data.get('fechaInicioActualizado')
            fecha_fin = data.get('fechaFinActualizado')
            if PeriodoAcademico.objects.exclude(id=id).filter(
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio,
                estado='ACTIVO'
            ).exists():
                return JsonResponse({
                    'error': 'Ya existe un período académico activo en el rango de fechas proporcionado.'
                }, status=400)
                
            # Actualizar los campos del período académico
            periodo.nombre = data['nombrePeriodoActualizado']
            periodo.descripcion= data['descripcion']
            periodo.cantidad = data['decimasPeriodoActualizado']
            periodo.fecha_inicio = data['fechaInicioActualizado']
            periodo.fecha_fin = data['fechaFinActualizado']
            periodo.estado = data['estadoActualizado']
            periodo.save()
            
            return JsonResponse({"message": "Período actualizado correctamente"})
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({"error": "Período no encontrado o ya ha sido eliminado"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Error en el formato del JSON.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Error del servidor: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)


#funcion para eliminar periodo
def eliminarUnPeriodo(request, id):
    if request.method == 'DELETE':
        try:
            periodo = PeriodoAcademico.objects.get(id=id)
            periodo.delete()
            return JsonResponse({'estado': True, 'mensaje': 'Periodo académico eliminado exitosamente.'}, status=200)
        except PeriodoAcademico.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Periodo académico no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
