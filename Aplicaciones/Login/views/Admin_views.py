#import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models.signals import post_delete
from django.dispatch import receiver
import json
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from ..models import Usuario,Administrador,Docente,Estudiante
from django.contrib.auth import login,authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def adminHome(request):
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
        'admin': admin,  # También puedes pasar todo el objeto docente si necesitas más detalles
    }
    print(f"Contexto enviado a la plantilla: {context}")
    return render(request, '../templates/Administrador/adminHome.html', context)

@csrf_exempt
def registroAdmin(request):
    if request.method == 'POST':
        try:
            # Leer los datos JSON del cuerpo de la solicitud
            data = json.loads(request.body)

            cedula = data.get('cedula_admin')
            primer_nombre = data.get('primer_nombre_admin')
            segundo_nombre = data.get('segundo_nombre_admin')
            apellido_Paterno = data.get('apellido_Paterno_admin')
            apellido_Materno = data.get('apellido_Materno_admin')
            telefono = data.get('telefono_admin')
            direccion = data.get('direccion_admin')
            email = data.get('email_admin')
            tipo_usuario = data.get('usuarioAdmin')

            # Validaciones
            if not cedula or not primer_nombre or not segundo_nombre or not apellido_Paterno or not apellido_Materno or not telefono or not direccion or not email or not tipo_usuario:
                return JsonResponse({'success': False, 'error': "Todos los campos son obligatorios"}, status=400)

            if len(cedula) != 10 or not cedula.isdigit():
                return JsonResponse({'success': False, 'error': "La cédula debe tener exactamente 10 dígitos numéricos"}, status=400)

            if len(telefono) != 10 or not telefono.isdigit():
                return JsonResponse({'success': False, 'error': "El teléfono debe tener exactamente 10 dígitos numéricos"}, status=400)

            if Usuario.objects.filter(username=cedula).exists():
                return JsonResponse({'success': False, 'error': "El nombre de usuario ya está en uso"}, status=400)

            # Crear el usuario
            password = cedula  # La contraseña es igual a la cédula
            user = Usuario.objects.create_user(username=cedula, tipo_usuario=tipo_usuario, password=password)
            user.save()

            if tipo_usuario == 'admin':
                Administrador.objects.create(
                    usuario=user,
                    cedula=cedula,
                    primer_nombre=primer_nombre,
                    segundo_nombre=segundo_nombre,
                    apellido_Paterno=apellido_Paterno,
                    apellido_Materno=apellido_Materno,
                    telefono=telefono,
                    direccion=direccion,
                    email=email
                )

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Error al decodificar JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Error al crear el usuario: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)



# aqui lista los administradores
def listadoAdministrador(request):
    administrador = Administrador.objects.all()  # Obtener todos los docentes
    
    context = {
        'administradores': administrador
    }
    return render(request, '../templates/Administrador/listadoAdministrador.html', context)


@receiver(post_delete, sender=Administrador)
def eliminar_usuario_asociado(sender, instance, **kwargs):
    # Verifica si el usuario existe antes de intentar eliminarlo
    if instance.usuario:
        instance.usuario.delete()


def eliminarAdministrador(request, id):
    print(f'ID recibido para eliminación: {id}')  # Añadir para depuración
    if request.method == 'DELETE':
        try:
            administrador = Administrador.objects.get(id=id)
            usuario = administrador.usuario
            administrador.delete()
           
            # Puedes agregar lógica adicional aquí si es necesario, como verificar otras condiciones
            
            return JsonResponse({
                'estado': True,
                'mensaje': 'Administrador eliminado exitosamente.'
            }, status=200)
        except Administrador.DoesNotExist:
            return JsonResponse({'estado': False, 'mensaje': 'Administrador no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'estado': False, 'mensaje': f'Error del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'estado': False, 'mensaje': 'Método no permitido.'}, status=405)
    


def obtenerAdministrador(request, id):
    try:
        administrador = Administrador.objects.get(id=id)
        data = {
            "id": administrador.id, #aqui solo creo variables
            "cedula": administrador.cedula,
            "direccion": administrador.direccion,
            "usuario": administrador.usuario.username if administrador.usuario else "No asignado",
            "primer_nombre": administrador.primer_nombre,
            "segundo_nombre": administrador.segundo_nombre,
            "apellido_Paterno": administrador.apellido_Paterno,
            "apellido_Materno": administrador.apellido_Materno,
            "telefono": administrador.telefono,
            "email": administrador.email,
           
        }
        return JsonResponse(data)
    except Administrador.DoesNotExist:
        return JsonResponse({"error": "Docente no encontrado"}, status=404)
    

@csrf_exempt
def actualizarAdministrador(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            administrador = Administrador.objects.get(id=id)

            # Validar que la nueva cédula no exista ya en otro docente
            nueva_cedula = data.get('cedula', administrador.cedula)
            if (
                Administrador.objects.filter(cedula=nueva_cedula).exclude(id=administrador.id).exists() or
                Estudiante.objects.filter(cedula=nueva_cedula).exists() or
                Docente.objects.filter(cedula=nueva_cedula).exists()
            ):
                return JsonResponse({"error": "La cédula ya está en uso por otro docente"}, status=400)

            # Actualizar datos del docente
            administrador.cedula = nueva_cedula
            administrador.primer_nombre= data.get('primer_nombre',administrador.primer_nombre)
            administrador.segundo_nombre= data.get('segundo_nombre',administrador.segundo_nombre) 
            administrador.apellido_Paterno= data.get('apellido_Paterno',administrador.apellido_Paterno)   
            administrador.apellido_Materno= data.get('apellido_Materno',administrador.apellido_Materno)            
            administrador.telefono = data.get('telefono', administrador.telefono)
            administrador.direccion = data.get('direccion',administrador.direccion)
            administrador.email = data.get('email', administrador.email)
            administrador.save()
            # Actualizar datos del usuario asociado (si existe)
            usuario = administrador.usuario
            if usuario:
                usuario.username = data.get('username', usuario.username)  # Actualizar el nombre de usuario si se proporciona
                new_password = data.get('password')
                if new_password:
                    usuario.set_password(new_password)
                
                usuario.save()
            
            
            
            return JsonResponse({"message": "Administrador y usuario actualizados correctamente"})
        except Docente.DoesNotExist:
            return JsonResponse({"error": "Administrador no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)
