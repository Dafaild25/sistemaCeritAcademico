from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from ..models import CursoAsignatura,Matricula,PeriodoDivision,Asistencia,AsistenciaTotal
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime,date
from django.db.models import  Q, Sum

from weasyprint import CSS, HTML
from django.template.loader import render_to_string 


def obtener_trimestres(request,periodo_id):
    # Filtra los periodos académicos que tienen el estado "ACTIVO"
    trimestres = list(PeriodoDivision.objects.filter(periodo_academico=periodo_id).values())
    if(len(trimestres)>0 ):
        data={
            'message': "ok",
            'trimestres':trimestres,
        }
    else:
        data={
            'message':"no hay datos"
        }  
    return JsonResponse(data)


def vistaAsistencias(request, clase_id):
    # Obtener el objeto CursoAsignatura con el ID proporcionado
    curso_asignatura = get_object_or_404(CursoAsignatura, id=clase_id)
    
    # Obtener el curso y la asignatura relacionados
    curso = curso_asignatura.curso_id
    asignatura = curso_asignatura.asignatura_id
    
    # Pasar los datos al contexto para el template
    context = {
        'curso_asignatura': curso_asignatura,
        'curso': curso,
        'asignatura': asignatura,
    }
    
    return render(request, '../templates/Docente/asistencias.html', context)


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

def listar_asistencias(request, trimestre_id, clase_id):
    # Obtener el trimestre y clase
    trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
    clase = get_object_or_404(CursoAsignatura, id=clase_id)
    
    # Obtener las matrículas asociadas a la clase
    matriculas = obtener_matriculas(clase)

     # Obtener las asistencias del trimestre
    asistencia_totales = AsistenciaTotal.objects.filter(
        periodo_division_id=trimestre_id,
        clase_id=clase_id
    )

    # Enlazar datos de asistencias a cada matrícula
    for matricula in matriculas:
        totales = asistencia_totales.filter(matricula=matricula).first()
        matricula.asistencias_count = totales.total_asistencias if totales else 0
        matricula.atrasos_count = totales.total_atrasos if totales else 0
        matricula.faltas_justificadas_count = totales.total_faltas_justificadas if totales else 0
        matricula.faltas_injustificadas_count = totales.total_faltas_injustificadas if totales else 0
        matricula.total_asistencias_completas_count = totales.total_asistencias_completas if totales else 0
        matricula.total_faltas_count = totales.total_faltas if totales else 0

    
    # Contexto para la plantilla
    context = {
        'clase': clase,
        'trimestre': trimestre,
        'curso': clase.curso_id,
        'asignatura': clase.asignatura_id,
        'matriculas': matriculas,
    }
    
    return render(request, '../templates/Docente/tablaAsistencias.html', context)





@csrf_exempt
def registrar_asistencia(request):
    if request.method == 'POST':
        try:
            # Datos del frontend
            data = json.loads(request.body)

            if not isinstance(data, list):
                return JsonResponse({'status': 'error', 'message': 'El formato de los datos no es válido.'}, status=400)

            for asistencia_data in data:
                # Debugging: imprime los datos
                print("Procesando asistencia:", asistencia_data)

                # Datos necesarios
                fecha = asistencia_data.get('fecha')
                estado = asistencia_data.get('estado')
                matricula_id = asistencia_data.get('matricula_id')
                periodo_division_id = asistencia_data.get('periodo_division_id')
                clase_id = asistencia_data.get('clase_id')

                # Validación básica
                if not fecha or not estado or not matricula_id or not periodo_division_id:
                    print("Datos incompletos:", asistencia_data)
                    return JsonResponse({'status': 'error', 'message': 'Datos incompletos.'}, status=400)

                # Verificar que los objetos existen
                try:
                    matricula = Matricula.objects.get(id=matricula_id)
                    periodo_division = PeriodoDivision.objects.get(id=periodo_division_id)
                    clase = CursoAsignatura.objects.get(id=clase_id)
                except Matricula.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Matrícula {matricula_id} no encontrada'}, status=404)
                except PeriodoDivision.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'PeriodoDivision {periodo_division_id} no encontrado'}, status=404)
                except CursoAsignatura.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Clase {clase_id} no encontrada'}, status=404)

                # Procesar la asistencia
                Asistencia.objects.update_or_create(
                    matricula=matricula,
                    periodo_division=periodo_division,
                    fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
                    clase_id=clase,
                    defaults={'estado': estado}
                )

            return JsonResponse({'status': 'success', 'message': 'Asistencias registradas correctamente.'})

        except Exception as e:
            print("Error inesperado:", str(e))
            return JsonResponse({'status': 'error', 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def obtener_asistencia(request, fecha):
    if request.method == "GET":
        try:
            # Consulta las asistencias para la fecha proporcionada
            asistencias = Asistencia.objects.filter(fecha=fecha).values(
                'matricula_id', 'periodo_division_id', 'clase_id', 'estado'
            )
            
            # Imprime los datos obtenidos en la consola para depuración
            print(f"Asistencias obtenidas para la fecha {fecha}: {list(asistencias)}")
            
            # Devuelve los datos como JSON
            return JsonResponse({'status': 'success', 'data': list(asistencias)})
        except Exception as e:
            # Si ocurre un error, imprime el error y devuelve un mensaje al cliente
            print(f"Error al obtener asistencias para la fecha {fecha}: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    # Si no es un método GET
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



def obtener_asistencias_por_mes(request, clase_id, trimestre_id,fecha_mes):
    try:
        # Validar que la clase existe
        clase = get_object_or_404(CursoAsignatura, id=clase_id)
        trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
        
        # Filtrar asistencias por clase y mes
        asistencias = Asistencia.objects.filter(
            periodo_division=trimestre,
            clase_id=clase,
            fecha__startswith=fecha_mes
        ).values('fecha')

        # Extraer solo los días con asistencias
        dias_con_asistencia = [asistencia['fecha'].day for asistencia in asistencias]

        return JsonResponse({
            "status": "success",
            "diasConAsistencia": dias_con_asistencia
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error al obtener asistencias: {str(e)}"
        })


def obtener_dias_estado(request, estado, matricula_id, trimestre_id):
    try:
        # Filtrar las asistencias según los parámetros
        asistencias = Asistencia.objects.filter(
            matricula=matricula_id,
            periodo_division=trimestre_id,
            estado=estado.upper()  # Asegurarse de comparar con el formato correcto
        ).values("fecha")  # Solo necesitamos las fechas

        # Convertir a lista para JSON
        dias = list(asistencias)

        # Log para depuración
        print("Días encontrados:", dias)

        return JsonResponse(dias, safe=False)
    except Exception as e:
        print("Error en obtener_dias_estado:", e)
        return JsonResponse([], safe=False)





def resumen_asistencias(request, clase_id):
    # Obtener la clase
    clase = get_object_or_404(CursoAsignatura, id=clase_id)

    # Obtener los trimestres
    trimestres = PeriodoDivision.objects.all()

    # Obtener las matrículas asociadas a la clase
    matriculas = obtener_matriculas(clase)

    # Obtener las asistencias de todos los estudiantes en la clase y los trimestres
    asistencia_totales = AsistenciaTotal.objects.filter(
        clase_id=clase_id
    )

    # Asociar los datos de asistencia a cada matrícula y trimestre
    for matricula in matriculas:
        matricula.asistencias_por_trimestre = []
        
        # Inicializar variables para los totales de asistencias y faltas
        total_asistencias = 0
        total_faltas = 0
        
        for trimestre in trimestres:
            totales = asistencia_totales.filter(
                matricula=matricula,
                periodo_division=trimestre
            ).first()
            
            if totales:
                # Sumar las asistencias (asistencias + atrasos)
                asistencias = totales.total_asistencias + totales.total_atrasos
                # Sumar las faltas (faltas justificadas + faltas injustificadas)
                faltas = totales.total_faltas_justificadas + totales.total_faltas_injustificadas
                
                # Agregar los datos al trimestre
                matricula.asistencias_por_trimestre.append({
                    'asistencias': totales.total_asistencias,
                    'atrasos': totales.total_atrasos,
                    'faltas_justificadas': totales.total_faltas_justificadas,
                    'faltas_injustificadas': totales.total_faltas_injustificadas,
                })
            else:
                # Si no hay datos, asignar 0 a las asistencias y faltas
                matricula.asistencias_por_trimestre.append({
                    'asistencias': 0,
                    'atrasos': 0,
                    'faltas_justificadas': 0,
                    'faltas_injustificadas': 0,
                })
                asistencias = 0
                faltas = 0

            # Sumar los valores a los totales
            total_asistencias += asistencias
            total_faltas += faltas

        # Añadir los totales de asistencias y faltas a la matrícula
        matricula.total_asistencias = total_asistencias
        matricula.total_faltas = total_faltas

    # Renderizar el template con los datos
    return render(request, 'Docente/resumenAsistencias.html', {
        'clase': clase,
        'trimestres': trimestres,
        'matriculas': matriculas,
    })




def generar_pdf_asistencias(request, clase_id):
     # Obtener la clase
    clase = get_object_or_404(CursoAsignatura, id=clase_id)

    # Obtener los trimestres
    trimestres = PeriodoDivision.objects.all()

    # Obtener las matrículas asociadas a la clase
    matriculas = obtener_matriculas(clase)

    # Obtener las asistencias de todos los estudiantes en la clase y los trimestres
    asistencia_totales = AsistenciaTotal.objects.filter(
        clase_id=clase_id
    )

    # Asociar los datos de asistencia a cada matrícula y trimestre
    for matricula in matriculas:
        matricula.asistencias_por_trimestre = []
        
        # Inicializar variables para los totales de asistencias y faltas
        total_asistencias = 0
        total_faltas = 0
        
        for trimestre in trimestres:
            totales = asistencia_totales.filter(
                matricula=matricula,
                periodo_division=trimestre
            ).first()
            
            if totales:
                # Sumar las asistencias (asistencias + atrasos)
                asistencias = totales.total_asistencias + totales.total_atrasos
                # Sumar las faltas (faltas justificadas + faltas injustificadas)
                faltas = totales.total_faltas_justificadas + totales.total_faltas_injustificadas
                
                # Agregar los datos al trimestre
                matricula.asistencias_por_trimestre.append({
                    'asistencias': totales.total_asistencias,
                    'atrasos': totales.total_atrasos,
                    'faltas_justificadas': totales.total_faltas_justificadas,
                    'faltas_injustificadas': totales.total_faltas_injustificadas,
                })
            else:
                # Si no hay datos, asignar 0 a las asistencias y faltas
                matricula.asistencias_por_trimestre.append({
                    'asistencias': 0,
                    'atrasos': 0,
                    'faltas_justificadas': 0,
                    'faltas_injustificadas': 0,
                })
                asistencias = 0
                faltas = 0

            # Sumar los valores a los totales
            total_asistencias += asistencias
            total_faltas += faltas

        # Añadir los totales de asistencias y faltas a la matrícula
        matricula.total_asistencias = total_asistencias
        matricula.total_faltas = total_faltas

    fecha = date.today().strftime("%d/%m/%Y")
    año = date.today().year

    # Renderizar el template HTML
    html_string = render_to_string('Docente/resumen_asistencia_pdf.html', { # type: ignore
        'clase': clase,
        'trimestres': trimestres,
        'matriculas': matriculas,
        'fecha': fecha,
        'año': año,
    })

   # Generar PDF con orientación horizontal (landscape)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    # Aplicar la orientación horizontal en el CSS
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; margin: 0; }')])

    # Crear la respuesta con el PDF generado
    response = HttpResponse(pdf, content_type='application/pdf')

    # Verificar si el parámetro 'download' está presente en la URL
    if 'download' in request.GET:
        # Si 'download' está presente, forzamos la descarga
        response['Content-Disposition'] = 'attachment; filename="reporte_asistencias.pdf"'
    else:
        # De lo contrario, mostramos el PDF en línea
        response['Content-Disposition'] = 'inline; filename="reporte_asistencias.pdf"'

    return response




def generar_pdf_asistencias_trimestre(request, clase_id,trimestre_id):
    # Obtener el trimestre y clase
    trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
    clase = get_object_or_404(CursoAsignatura, id=clase_id)
    
    # Obtener las matrículas asociadas a la clase
    matriculas = obtener_matriculas(clase)

    # Obtener las asistencias del trimestre
    asistencia_totales = AsistenciaTotal.objects.filter(
        periodo_division_id=trimestre_id,
        clase_id=clase_id
    )

    # Enlazar datos de asistencias a cada matrícula
    for matricula in matriculas:
        totales = asistencia_totales.filter(matricula=matricula).first()
        matricula.asistencias_count = totales.total_asistencias if totales else 0
        matricula.atrasos_count = totales.total_atrasos if totales else 0
        matricula.faltas_justificadas_count = totales.total_faltas_justificadas if totales else 0
        matricula.faltas_injustificadas_count = totales.total_faltas_injustificadas if totales else 0
        matricula.total_asistencias_completas_count = totales.total_asistencias_completas if totales else 0
        matricula.total_faltas_count = totales.total_faltas if totales else 0

    fecha = date.today().strftime("%d/%m/%Y")
    año = date.today().year

    # Renderizar el template HTML
    html_string = render_to_string('../templates/Docente/resumen_asistencia_trimestre_pdf.html', { # type: ignore
        'clase': clase,
        'trimestre': trimestre,
        'curso': clase.curso_id,
        'asignatura': clase.asignatura_id,
        'matriculas': matriculas,
        'fecha': fecha,
        'año': año,
    })

   # Generar PDF con orientación horizontal (landscape)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    # Aplicar la orientación horizontal en el CSS
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; margin: 0; }')])

    # Crear la respuesta con el PDF generado
    response = HttpResponse(pdf, content_type='application/pdf')

    # Verificar si el parámetro 'download' está presente en la URL
    if 'download' in request.GET:
        # Si 'download' está presente, forzamos la descarga
        response['Content-Disposition'] = 'attachment; filename="reporte_asistencias_trimestre.pdf"'
    else:
        # De lo contrario, mostramos el PDF en línea
        response['Content-Disposition'] = 'inline; filename="reporte_asistencias_trimestre.pdf"'

    return response
