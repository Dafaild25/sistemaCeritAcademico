from django import template
from ..models import Matricula, PeriodoDivision, PromedioTrimestres, CursoAsignatura
from django.db.models import Sum

register = template.Library()

@register.filter
def calcular_promedio(matricula_id, trimestre_id):
    try:
        matricula = Matricula.objects.get(id=matricula_id)
        trimestre = PeriodoDivision.objects.get(id=trimestre_id)
        cantidad_decimales = trimestre.periodo_academico.cantidad

        promedios_trimestrales = PromedioTrimestres.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre
        )

        curso = matricula.curso_id
        numero_de_clases = CursoAsignatura.objects.filter(curso_id=curso).count()

        if not promedios_trimestrales.exists():
            return "No Disponible"

        suma_promedios = promedios_trimestrales.aggregate(suma=Sum('promedioTrimestral'))['suma'] or 0
        promedio_total = suma_promedios / numero_de_clases if numero_de_clases > 0 else 0

        return round(promedio_total, cantidad_decimales)
    except Exception as e:
        return "Error"
