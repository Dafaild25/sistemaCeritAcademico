from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import logout
from ..models import *
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import json

# no la  uso 

def listarPeriodoParaVariables(request):
    # Filtra los periodos académicos que tienen el estado "ACTIVO"
    periodos = list(PeriodoAcademico.objects.filter(estado='ACTIVO').values())
    if(len(periodos)>0 ):
        data={
            'message': "okey",
            'periodos':periodos,
        }
    else:
        data={
            'message':"no hay datos"
        }  
    return JsonResponse(data)



@login_required
def vistaVariablesGlobales(request):
    user = request.user
    try:
        admin = user.admin  # Suponiendo que `user` tiene una relación con `admin`.
        nombre_admin = f'{admin.apellido_Paterno} {admin.apellido_Materno} {admin.primer_nombre} {admin.segundo_nombre}'
        print(f"Perfil de Administrador encontrado: {nombre_admin}")
    except AttributeError:
        admin = None
        nombre_admin = user.username  # En caso de que no exista perfil de administrador.
        print("Perfil de Administrador no encontrado.")
    
    # Definir el contexto correctamente
    context = {
        'admin': admin,
        'nombre_admin': nombre_admin,
    }
    
    return render(request, 'Variables/vistaVariablesGlobales.html', context)





@login_required
def registrarEscuela(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            direccion = request.POST.get('direccion')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            rector = request.POST.get('rector')
            fundacion = request.POST.get('fundacion')
            vision = request.POST.get('vision')
            mision = request.POST.get('mision')
            logo = request.FILES.get('logo')

            if not nombre:
                return JsonResponse({'success': False, 'error': "El campo 'nombre' es obligatorio."}, status=400)

            escuela = Escuela.objects.first()

            if escuela:
                # Actualizar
                escuela.nombre = nombre
                escuela.direccion = direccion
                escuela.telefono = telefono
                escuela.email = email
                escuela.rector = rector
                escuela.fundacion = fundacion
                escuela.vision = vision
                escuela.mision = mision
                if logo:
                    escuela.logo = logo
                escuela.save()
                return JsonResponse({'success': True, 'message': 'Datos de la institución actualizados correctamente.'})

            else:
                # Crear
                Escuela.objects.create(
                    nombre=nombre,
                    direccion=direccion,
                    telefono=telefono,
                    email=email,
                    rector=rector,
                    fundacion=fundacion,
                    vision=vision,
                    mision=mision,
                    logo=logo,
                )
                return JsonResponse({'success': True, 'message': 'Institución registrada correctamente.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Error al guardar: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)




def obtenerEscuela(request):
    try:
        escuela = Escuela.objects.first()
        if not escuela:
            return JsonResponse({'success': False, 'error': 'No hay datos registrados de la institución.'}, status=404)

        data = {
            'nombre': escuela.nombre,
            'direccion': escuela.direccion,
            'telefono': escuela.telefono,
            'email': escuela.email,
            'rector': escuela.rector,
            'fundacion': escuela.fundacion,
            'vision': escuela.vision,
            'mision': escuela.mision,
            'logo_url': escuela.logo.url if escuela.logo else None,
        }
        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
