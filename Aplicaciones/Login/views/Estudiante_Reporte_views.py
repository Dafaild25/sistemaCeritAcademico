from collections import defaultdict
import json
from logging import config
import tempfile

from django.db.models import Avg,Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from weasyprint import HTML,CSS
from ..models import Asignatura, Asistencia, CalificacionExamen, Curso, CursoAsignatura, Matricula, PeriodoAcademico, PeriodoDivision, PromedioTrimestres, PromedioTrimestresAsignatura, PromedioUnidades, Usuario, Estudiante,Administrador,Docente,AsistenciaTotal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from Aplicaciones.Login import models  # Asegúrate de importar settings



# despues de llamar al home estudiante

# procedemos a crear las vistas 

@login_required
def listarPeriodosEstudiantes(request):
    # Accede al usuario autenticado
    user = request.user
    try:
        # Intentamos obtener el estudiante
        estudiante = user.estudiante
        
    except Estudiante.DoesNotExist:
        return JsonResponse({'message': "Estudiante no encontrado"}, status=404)

    # Filtramos las matrículas activas del estudiante
    matriculas = Matricula.objects.filter(estudiante_id=estudiante).select_related('curso_id')

    # Obtenemos los periodos académicos en los que el estudiante está matriculado
    periodos = PeriodoAcademico.objects.filter(
        id__in=matriculas.values('curso_id__periodoAcademico_id'),
        estado='ACTIVO'
    ).values()

    if periodos:
        data = {
            'message': "okey",
            'periodos': list(periodos),
        }
    else:
        data = {
            'message': "no hay datos",
        }
    
    return JsonResponse(data)


@login_required
def listarTrimestresEstudiantes(request, periodo_id):
    trimestres = PeriodoDivision.objects.filter(periodo_academico=periodo_id)
    data = {
        'message': 'ok',
        'trimestres': []
    }
    
    if trimestres.exists():
        # Añadir solo los trimestres al JSON
        data['trimestres'] = [
            {
                'id': trimestre.id,
                'nombre': trimestre.nombre,
            }
            for trimestre in trimestres
        ]
    else:
        data = {'message': 'no hay datos'}
        
    return JsonResponse(data)


def obtener_estudiante_asociado(user):
    """Obtiene el estudiante asociado al usuario logueado."""
    try:
        return user.estudiante
    except Estudiante.DoesNotExist:
        return None

def obtener_periodo_academico(periodo_id):
    """Obtiene el periodo académico correspondiente al ID proporcionado."""
    return get_object_or_404(PeriodoAcademico, id=periodo_id)

def obtener_matricula(estudiante, periodo_id):
    """Obtiene la matrícula del estudiante en un curso asociado al periodo académico."""
    return Matricula.objects.filter(
        estudiante_id=estudiante,
        curso_id__periodoAcademico_id=periodo_id
    ).first()


def obtenerEstudiante(user):
    try:
        return user.estudiante
    except AttributeError:
        return JsonResponse({"error": "El usuario no es un estudiante."}, status=403)

def obtenerMatricula(estudiante, periodo_id):
    matricula = Matricula.objects.filter(
        estudiante_id=estudiante,
        curso_id__periodoAcademico_id=periodo_id
    ).first()
    if not matricula:
        return JsonResponse({"error": "El estudiante no está matriculado en este período académico."}, status=404)
    return matricula

def obtenerAsignaturas(curso_id):
    return CursoAsignatura.objects.filter(curso_id=curso_id)




@login_required
def listarCalificacionesPorPeriodo(request, periodo_id):
    user = request.user
    estudiante = obtener_estudiante_asociado(user)
    
    if not estudiante:
        return render(request, 'error.html', {'message': 'No se ha encontrado el estudiante asociado a este usuario.'})
    
    periodo_academico = obtener_periodo_academico(periodo_id)
    matricula = obtener_matricula(estudiante, periodo_id)
    
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    cantidad_decimales = periodo.cantidad
    
    asignaturas = obtenerAsignaturas(matricula.curso_id)

    # Obtener las divisiones del periodo académico (por ejemplo, los trimestres)
    periodo_divisiones = PeriodoDivision.objects.filter(periodo_academico=periodo_academico)
    
    # Calcular el promedio general de todas las asignaturas usando la función auxiliar
    
   
    
    # Obtener los promedios trimestrales para cada asignatura y cada trimestre
    asignaturas_matriculadas = []
    suma_total_promedios = 0
    total_asignaturas = 0
    
   
    
    
    for asignatura in asignaturas:
        curso_asignatura_id = asignatura["id"] if isinstance(asignatura, dict) else asignatura.id
        total_asignaturas += 1
        promedios_trimestrales = []
        for trimestre in periodo_divisiones:
            promedio_trimestral = PromedioTrimestres.objects.filter(
                matricula_id=matricula,
                trimestre_id=trimestre.id,  # Filtramos por el trimestre actual
                curso_asignatura_id=curso_asignatura_id
            ).first()
            
            # Redondear el promedio trimestral
            if promedio_trimestral and promedio_trimestral.promedioTrimestral is not None:
                promedio_trimestral.promedioTrimestral = round(promedio_trimestral.promedioTrimestral, cantidad_decimales)
            
            promedios_trimestrales.append(promedio_trimestral)
            
            
         
        # Obtener el promedio general de la asignatura
        promedio_general_asignatura = PromedioTrimestresAsignatura.objects.filter(
            matricula_id=matricula,
            curso_asignatura_id=curso_asignatura_id
        ).first()
        
        # Redondear el promedio general de la asignatura
        if promedio_general_asignatura and promedio_general_asignatura.promedioTrimestral is not None:
            promedio_general_asignatura.promedioTrimestral = round(promedio_general_asignatura.promedioTrimestral, cantidad_decimales)
            suma_total_promedios += promedio_general_asignatura.promedioTrimestral
            

        asignaturas_matriculadas.append({
            "nombre": asignatura["nombre"] if isinstance(asignatura, dict) else asignatura.asignatura_id.nombre,
            "promedios_trimestrales": promedios_trimestrales,
            "promedio_general_asignatura": promedio_general_asignatura.promedioTrimestral if promedio_general_asignatura else None,
        })
    
    # Calcular el promedio general de todas las asignaturas
    promedio_general_todas_asignaturas = suma_total_promedios / total_asignaturas if total_asignaturas > 0 else 0
    promedio_general_todas_asignaturas = round(promedio_general_todas_asignaturas, cantidad_decimales)
    

    # Preparar el contexto para el template
    context = {
        "estudiante": {
            "nombre": f"{estudiante.primer_nombre} {estudiante.segundo_nombre} {estudiante.apellido_Paterno} {estudiante.apellido_Materno}",
            "cedula": estudiante.cedula,
        },
        "curso": {
            "nombre": matricula.curso_id.nombre,
            "nivel": matricula.curso_id.paralelo,
        },
        "periodo": periodo,
        "asignaturas_matriculadas": asignaturas_matriculadas,
        "periodo_divisiones": periodo_divisiones,  
        "promedio_general_todas_asignaturas": promedio_general_todas_asignaturas,
        "matricula": matricula,
        
    }

    # Renderizar el template con el contexto
    return render(request, 'Estudiante/reportePeriodical.html', context)




@login_required
def listarCalificacionesPorTrimestre(request, periodo_id, trimestre_id):
    # Verificar si el usuario autenticado está relacionado con un estudiante
    estudiante = obtenerEstudiante(request.user)
    if isinstance(estudiante, JsonResponse):
        return estudiante  # Retorna el error si no es estudiante

    # Verificar si el estudiante tiene matrícula en el período académico
    matricula = obtenerMatricula(estudiante, periodo_id)
    if isinstance(matricula, JsonResponse):
        return matricula  # Retorna el error si no tiene matrícula
    
    # Obtener las asistencias del trimestre para la matrícula del estudiante
    asistencia_totales = AsistenciaTotal.objects.filter(
        matricula=matricula,
        periodo_division_id=trimestre_id
    )

    # Crear un diccionario para mapear asistencias con su clase
    asistencias_data = {}
    for asistencia in asistencia_totales:
        clase_id = asistencia.clase_id.id  # ID de la clase
        asistencias_data[clase_id] = {
            "total_asistencias": asistencia.total_asistencias,
            "total_atrasos": asistencia.total_atrasos,
            "total_faltas_justificadas": asistencia.total_faltas_justificadas,
            "total_faltas_injustificadas": asistencia.total_faltas_injustificadas,
            "total_asistencias_completas": asistencia.total_asistencias_completas,
            "total_faltas": asistencia.total_faltas,
        }

    # Obtener las asignaturas asociadas al curso
    asignaturas = obtenerAsignaturas(matricula.curso_id)
    
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    cantidad_decimales = periodo.cantidad
    trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)

    # Preparar datos de calificaciones para cada asignatura
    asignaturas_matriculadas = []
    for asignatura in asignaturas:
        curso_asignatura_id = asignatura["id"] if isinstance(asignatura, dict) else asignatura.id

        promedio_unidad = PromedioUnidades.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre_id,
            curso_asignatura_id=curso_asignatura_id
        ).aggregate(models.Avg('subPromedioUnidad'))['subPromedioUnidad__avg']
        
        # Redondear promedio_unidad a la cantidad de decimales del periodo
        if promedio_unidad is not None:
            promedio_unidad = round(promedio_unidad, cantidad_decimales)

        examen = CalificacionExamen.objects.filter(
            matricula_id=matricula,
            examen_id__trimestre_id=trimestre_id,
            curso_asignatura_id=curso_asignatura_id
        ).first()
        
        # Redondear la calificación del examen
        if examen and examen.nota is not None:
            examen.nota = round(examen.nota, cantidad_decimales)

        promedio_trimestral = PromedioTrimestres.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre_id,
            curso_asignatura_id=curso_asignatura_id
        ).first()
        
        # Redondear el promedio trimestral
        if promedio_trimestral and promedio_trimestral.promedioTrimestral is not None:
            promedio_trimestral.promedioTrimestral = round(promedio_trimestral.promedioTrimestral, cantidad_decimales)

        # Recuperar la asistencia específica de esta asignatura
        asistencia = asistencias_data.get(curso_asignatura_id, {
            "total_asistencias": 0,
            "total_atrasos": 0,
            "total_faltas_justificadas": 0,
            "total_faltas_injustificadas": 0,
            "total_asistencias_completas": 0,
            "total_faltas": 0,
        })

        asignaturas_matriculadas.append({
            "nombre": asignatura["nombre"] if isinstance(asignatura, dict) else asignatura.asignatura_id.nombre,
            "promedio_unidad": promedio_unidad,
            "examen": examen.nota if examen else None,
            "promedio_trimestral": promedio_trimestral.promedioTrimestral if promedio_trimestral else None,
            "asistencia": asistencia,  # Aquí se asigna correctamente
        })

    # Preparar el contexto para el template
    context = {
        "estudiante": {
            "nombre_completo": f"{estudiante.primer_nombre} {estudiante.segundo_nombre} {estudiante.apellido_Paterno} {estudiante.apellido_Materno}",
            "cedula": estudiante.cedula,
        },
        "curso": {
            "nombre": matricula.curso_id.nombre,
            "nivel": matricula.curso_id.paralelo,
        },
        "periodo": periodo,
        "trimestre": trimestre,
        "asignaturas_matriculadas": asignaturas_matriculadas,
        "clases": asignaturas,  # No se modifica, pero se pasa como estaba
    }

    # Renderizar el template con el contexto
    return render(request, 'Estudiante/reporteTrimestral.html', context)






def reportePeriodicalEstudiante(request, periodo_id):
    user = request.user
    estudiante = obtener_estudiante_asociado(user)
    
    if not estudiante:
        return render(request, 'error.html', {'message': 'No se ha encontrado el estudiante asociado a este usuario.'})
    
    periodo_academico = obtener_periodo_academico(periodo_id)
    matricula = obtener_matricula(estudiante, periodo_id)
    
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    cantidad_decimales = periodo.cantidad
    
    asignaturas = obtenerAsignaturas(matricula.curso_id)

    # Obtener las divisiones del periodo académico (por ejemplo, los trimestres)
    periodo_divisiones = PeriodoDivision.objects.filter(periodo_academico=periodo_academico)
    
    asignaturas_matriculadas = []
    suma_total_promedios = 0
    total_asignaturas = 0
    
    
    
    # Obtener los promedios trimestrales para cada asignatura y cada trimestre
    asignaturas_matriculadas = []
    for asignatura in asignaturas:
        curso_asignatura_id = asignatura["id"] if isinstance(asignatura, dict) else asignatura.id
        total_asignaturas += 1
        promedios_trimestrales = []
        for trimestre in periodo_divisiones:
            promedio_trimestral = PromedioTrimestres.objects.filter(
                matricula_id=matricula,
                trimestre_id=trimestre.id,  # Filtramos por el trimestre actual
                curso_asignatura_id=curso_asignatura_id
            ).first()
            
            # Redondear el promedio trimestral
            if promedio_trimestral and promedio_trimestral.promedioTrimestral is not None:
                promedio_trimestral.promedioTrimestral = round(promedio_trimestral.promedioTrimestral, cantidad_decimales)
            
            promedios_trimestrales.append(promedio_trimestral)

        # Obtener el promedio general de la asignatura
        promedio_general_asignatura = PromedioTrimestresAsignatura.objects.filter(
            matricula_id=matricula,
            curso_asignatura_id=curso_asignatura_id
        ).first()
        
        # Redondear el promedio general de la asignatura
        if promedio_general_asignatura and promedio_general_asignatura.promedioTrimestral is not None:
            promedio_general_asignatura.promedioTrimestral = round(promedio_general_asignatura.promedioTrimestral, cantidad_decimales)
            suma_total_promedios += promedio_general_asignatura.promedioTrimestral
    
        asignaturas_matriculadas.append({
            "nombre": asignatura["nombre"] if isinstance(asignatura, dict) else asignatura.asignatura_id.nombre,
            "promedios_trimestrales": promedios_trimestrales,
            "promedio_general_asignatura": promedio_general_asignatura.promedioTrimestral if promedio_general_asignatura else None,
        })
    
    # Calcular el promedio general de todas las asignaturas
    promedio_general_todas_asignaturas = suma_total_promedios / total_asignaturas if total_asignaturas > 0 else 0
    promedio_general_todas_asignaturas = round(promedio_general_todas_asignaturas, cantidad_decimales)
    
    
    # Preparar el contexto para el template
    context = {
        "estudiante": {
            "nombre": f"{estudiante.primer_nombre} {estudiante.segundo_nombre} {estudiante.apellido_Paterno} {estudiante.apellido_Materno}",
            "cedula": estudiante.cedula,
        },
        "curso": {
            "nombre": matricula.curso_id.nombre,
            "nivel": matricula.curso_id.paralelo,
        },
        "periodo": periodo,
        "asignaturas_matriculadas": asignaturas_matriculadas,
        "periodo_divisiones": periodo_divisiones,
        "promedio_general_todas_asignaturas": promedio_general_todas_asignaturas,
        "matricula": matricula,
        # Añadimos las divisiones del periodo académico (trimestres)
    }

    # Renderizar el HTML del template
    html_string = render_to_string('pdf_templates/pdf_reporteGeneralPorAsignatura.html', context)
    
    # Generar el PDF con la orientación horizontal
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    # Generar el PDF con la configuración de tamaño de página A4 en horizontal
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; }')])

    # Crear una respuesta con el archivo PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte-periodical.pdf"'

    return response



def reporteTrimestralEstudiante(request, periodo_id, trimestre_id):
    # Verificar si el usuario autenticado está relacionado con un estudiante
    estudiante = obtenerEstudiante(request.user)
    if isinstance(estudiante, JsonResponse):
        return estudiante  # Retorna el error si no es estudiante

    # Verificar si el estudiante tiene matrícula en el período académico
    matricula = obtenerMatricula(estudiante, periodo_id)
    if isinstance(matricula, JsonResponse):
        return matricula  # Retorna el error si no tiene matrícula

    # Obtener las asistencias del trimestre para la matrícula del estudiante
    asistencia_totales = AsistenciaTotal.objects.filter(
        matricula=matricula,
        periodo_division_id=trimestre_id
    )
    
    # Crear un diccionario para mapear asistencias con su clase
    asistencias_data = {}
    for asistencia in asistencia_totales:
        clase_id = asistencia.clase_id.id  # ID de la clase
        asistencias_data[clase_id] = {
            "total_asistencias": asistencia.total_asistencias,
            "total_atrasos": asistencia.total_atrasos,
            "total_faltas_justificadas": asistencia.total_faltas_justificadas,
            "total_faltas_injustificadas": asistencia.total_faltas_injustificadas,
            "total_asistencias_completas": asistencia.total_asistencias_completas,
            "total_faltas": asistencia.total_faltas,
        }
    
    # Obtener las asignaturas asociadas al curso
    asignaturas = obtenerAsignaturas(matricula.curso_id)
    
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    cantidad_decimales = periodo.cantidad
    trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)

    # Preparar datos de calificaciones para cada asignatura
    asignaturas_matriculadas = []
    for asignatura in asignaturas:
        curso_asignatura_id = asignatura["id"] if isinstance(asignatura, dict) else asignatura.id

        promedio_unidad = PromedioUnidades.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre_id,
            curso_asignatura_id=curso_asignatura_id
        ).aggregate(models.Avg('subPromedioUnidad'))['subPromedioUnidad__avg']
        
        # Redondear promedio_unidad a la cantidad de decimales del periodo
        if promedio_unidad is not None:
            promedio_unidad = round(promedio_unidad, cantidad_decimales)

        examen = CalificacionExamen.objects.filter(
            matricula_id=matricula,
            examen_id__trimestre_id=trimestre_id,
            curso_asignatura_id=curso_asignatura_id
        ).first()
        
        # Redondear la calificación del examen
        if examen and examen.nota is not None:
            examen.nota = round(examen.nota, cantidad_decimales)

        promedio_trimestral = PromedioTrimestres.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre_id,
            curso_asignatura_id=curso_asignatura_id
        ).first()
        
        # Redondear el promedio trimestral
        if promedio_trimestral and promedio_trimestral.promedioTrimestral is not None:
            promedio_trimestral.promedioTrimestral = round(promedio_trimestral.promedioTrimestral, cantidad_decimales)

        asignaturas_matriculadas.append({
            "nombre": asignatura["nombre"] if isinstance(asignatura, dict) else asignatura.asignatura_id.nombre,
            "promedio_unidad": promedio_unidad,
            "examen": examen.nota if examen else None,
            "promedio_trimestral": promedio_trimestral.promedioTrimestral if promedio_trimestral else None,
            "asistencia": asistencia,
        })

    # Preparar el contexto para el template
    context = {
        "estudiante": {
            "nombre_completo": f"{estudiante.primer_nombre} {estudiante.segundo_nombre} {estudiante.apellido_Paterno} {estudiante.apellido_Materno}",
            "cedula": estudiante.cedula,
        },
        "curso": {
            "nombre": matricula.curso_id.nombre,
            "nivel": matricula.curso_id.paralelo,
        },
        "periodo": matricula.curso_id.periodoAcademico_id.nombre,
        "trimestre": trimestre,
        "asignaturas_matriculadas": asignaturas_matriculadas,
    }

    html_string = render_to_string('pdf_templates/pdf_reporteTrimestral.html', context)
    html=HTML(string=html_string,base_url=request.build_absolute_uri('/'))
    pdf=html.write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; }')])
    response=HttpResponse(pdf,content_type='application/pdf')
    response['Content-Disposition']='attachment; filename="reporte_trimestral.pdf"'
    return response





# davdi
def calcularPromedioTrimestralEstudiante(request, matricula_id, trimestre_id):
    # Obtener la matrícula y el trimestre a partir de los IDs
    matricula = get_object_or_404(Matricula, id=matricula_id)
    trimestre = get_object_or_404(PeriodoDivision, id=trimestre_id)
    
    cantidad_decimales = trimestre.periodo_academico.cantidad
    # Filtrar los promedios trimestrales para la matrícula y trimestre especificados
    promedios_trimestrales = PromedioTrimestres.objects.filter(
        matricula_id=matricula,
        trimestre_id=trimestre
    )
    
    curso = matricula.curso_id
    
    # Contar cuántas asignaturas tiene ese curso
    numeroDeClases = CursoAsignatura.objects.filter(curso_id=curso).count()
    
    # Si no hay promedios para ese trimestre, retornamos un mensaje
    if not promedios_trimestrales.exists():
        return JsonResponse({'message': 'No se encontraron promedios para esta matrícula y trimestre.'}, status=404)
    
    # Sumar los promedios trimestrales
    suma_promedios = promedios_trimestrales.aggregate(suma=Sum('promedioTrimestral'))['suma']
    
    # Si no hay suma de promedios, asignar un valor de 0
    if suma_promedios is None:
        suma_promedios = 0
    
    # Si hay clases, calcular el promedio total
    if numeroDeClases > 0:
        promedio_total = suma_promedios / numeroDeClases
    else:
        promedio_total = 0
    
    # Redondear el promedio total a 2 decimales
    promedio_total = round(promedio_total, cantidad_decimales)
    
    # Preparar la respuesta en formato JSON
    data = {
        'matricula_id': matricula.id,
        'trimestre_id': trimestre.id,
        'promedio_total': promedio_total,
    }
    
    # Retornamos la respuesta JSON
    return JsonResponse(data)
