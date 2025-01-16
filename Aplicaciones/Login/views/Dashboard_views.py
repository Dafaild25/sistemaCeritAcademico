from django.http import JsonResponse
from ..models import Estudiante,Docente,Administrador,TipoEvaluacion,Aporte

def obtener_datos_graficos(request):
     # Contar estudiantes activos e inactivos
    estudiantes_activos = Estudiante.objects.filter(estado='ACTIVO').count()
    estudiantes_inactivos = Estudiante.objects.filter(estado='INACTIVO').count()

    # Contar docentes activos e inactivos
    docentes_activos = Docente.objects.filter(estado='ACTIVO').count()
    docentes_inactivos = Docente.objects.filter(estado='INACTIVO').count()

    # Contar el total de administradores
    total_administradores = Administrador.objects.count()

    # Crear el diccionario de datos
    datos = {
        'estudiantes': [estudiantes_activos, estudiantes_inactivos],
        'docentes': [docentes_activos, docentes_inactivos],
        'administradores': [total_administradores, 0],  # Solo un dato, así que el segundo valor es 0
    }

    return JsonResponse(datos)

def obtener_tipos_evaluacion(request,curso_asignatura_id,trimestre):
    # Obtener todos los tipos de evaluación
    tipos_evaluacion = TipoEvaluacion.objects.filter(trimestre_id=trimestre)
    # Extraemos los nombres y ponderaciones
    labels = [tipo.nombre for tipo in tipos_evaluacion]
    data = [float(tipo.ponderacion) for tipo in tipos_evaluacion]
    colors = [tipo.color for tipo in tipos_evaluacion]  # Extraemos los colores

    # Contar los aportes por tipo de evaluación para la asignatura específica
    aportes_count = []
    for tipo in tipos_evaluacion:
        count = Aporte.objects.filter(tipo_id=tipo, cursoAsignatura_id=curso_asignatura_id).count()
        aportes_count.append(count)

    # Devolvemos los datos en formato JSON
    return JsonResponse({
        'labels': labels,
        'data': data,
        'colors': colors,
        'aportes_count': aportes_count  # Incluimos los conteos de aportes
    })