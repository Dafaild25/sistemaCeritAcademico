
from django.http import JsonResponse
from datetime import datetime
import logging
import openpyxl
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from ..models import Usuario, Docente,Matricula,Curso,Estudiante,CursoAsignatura,Asignatura
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings  # Asegúrate de importar settings

# Configuración del logger
logger = logging.getLogger(__name__)

# Obtener correos válidos excluyendo 'NaN'
def obtener_emails_validos(*emails):
    # Filtrar solo correos que no son None o vacíos
    return [email for email in emails if email and email != 'nan']


def importar_docentes(request):
    if request.method == 'POST':
        archivo_excel = request.FILES.get('archivo_excel')

        if not archivo_excel:
            return JsonResponse({'message': 'Archivo Excel no proporcionado.'}, status=400)

        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo_excel, engine='openpyxl', dtype={'Cedula': str, 'Telefono':str })

            for _, row in df.iterrows():
                cedula = str(row.get('Cedula'))
                primer_nombre = row.get('Primer Nombre')
                segundo_nombre = row.get('Segundo Nombre')
                apellido_Paterno = row.get('Apellido Paterno')
                apellido_Materno = row.get('Apellido Materno')
                telefono = row.get('Telefono')
                email = row.get('Email')
                especialidad = row.get('Especialidad')
                

                # Verifica los datos del docente
                if Usuario.objects.filter(username=cedula).exists():
                    continue  # Si el usuario ya existe, lo ignoramos

                usuario = Usuario.objects.create_user(
                    username=cedula,
                    tipo_usuario='docente',
                    password=str(cedula)  # Usa la cédula como contraseña o ajusta según tus necesidades
                )

                Docente.objects.create(
                    usuario=usuario,
                    cedula=cedula,
                    primer_nombre=primer_nombre,
                    segundo_nombre=segundo_nombre,
                    apellido_Paterno=apellido_Paterno,
                    apellido_Materno=apellido_Materno,
                    telefono=telefono,
                    email=email,
                    especialidad=especialidad,

                )

            return JsonResponse({'message': 'Docentes importados correctamente.'})

        except Exception as e:
            return JsonResponse({'message': f'Error al importar el archivo: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Método no permitido.'}, status=405)



@csrf_exempt
def importarEstudiantes(request):
    if request.method == 'POST':
        if 'archivo_excel' not in request.FILES or 'curso_id' not in request.POST:
            return JsonResponse({'success': False, 'error': 'Archivo o ID de curso no proporcionados'}, status=400)

        archivo_excel = request.FILES['archivo_excel']
        curso_id = request.POST.get('curso_id', '').strip()

        if not curso_id.isdigit():
            return JsonResponse({'success': False, 'error': 'ID de curso inválido'}, status=400)

        curso_id = int(curso_id)

        try:
            # Buscar la instancia del curso
            curso = Curso.objects.get(id=curso_id)

            # Leer el archivo Excel
            # Añadir dtype para asegurarse de que las cédulas y otros números se lean como cadenas
            df = pd.read_excel(archivo_excel, engine='openpyxl', dtype={'Cedula': str, 'Telefono':str , 'Cedula R1': str, 'Celular R1':str ,'Cedula R2': str, 'Celular R2':str ,'Cedula R3': str, 'Celular R3':str ,})

            # Asegúrate de que 'Fecha de Nacimiento' esté en formato de fecha
            df['Fecha Nacimiento'] = pd.to_datetime(df['Fecha Nacimiento'], errors='coerce')

            # Verifica si hay fechas nulas
            if df['Fecha Nacimiento'].isnull().any():
                raise ValueError("Hay fechas de nacimiento inválidas en el archivo.")

            for _, row in df.iterrows():
                # Convertir todos los valores a cadenas para evitar errores
                cedula = str(row.get('Cedula', '')).strip()
                primer_nombre = str(row.get('Primer Nombre', '')).strip()
                segundo_nombre = str(row.get('Segundo Nombre', '')).strip()
                apellido_Paterno = str(row.get('Apellido Paterno', '')).strip()
                apellido_Materno = str(row.get('Apellido Materno', '')).strip()
                
                # Validar y convertir fecha
                fecha_nacimiento = row.get('Fecha Nacimiento', None)
                if fecha_nacimiento:
                    # Intentar convertir la fecha
                    try:
                        fecha_nacimiento = pd.to_datetime(fecha_nacimiento, errors='coerce').date()
                    except Exception as e:
                        logger.warning(f"Error al convertir fecha: {fecha_nacimiento} - {str(e)}")
                        fecha_nacimiento = None  # Establecer a None si la conversión falla
                
                telefono = str(row.get('Telefono', '')).strip()
                ciudad = str(row.get('Ciudad', '')).strip()
                direccion = str(row.get('Direccion', '')).strip()
                email = str(row.get('Email', '')).strip() if str(row.get('Email', '')).strip() else None
                tipo_usuario = 'estudiante'

                # Datos de los representantes (pueden ser vacíos)
                cedula_R1 = str(row.get('Cedula R1', '')).strip()
                nombres_R1 = str(row.get('Nombres R1', '')).strip()
                apellido_paterno_R1 = str(row.get('Apellido Paterno R1', '')).strip()
                apellido_materno_R1 = str(row.get('Apellido Materno R1', '')).strip()
                celular_R1 = str(row.get('Celular R1', '')).strip()
                email_R1 = str(row.get('Email R1', '')).strip() if str(row.get('Email R1', '')).strip() else None
                parentesco_R1 = str(row.get('Parentesco R1', '')).strip()

                cedula_R2 = str(row.get('Cedula R2', '')).strip()
                nombres_R2 = str(row.get('Nombres R2', '')).strip()
                apellido_paterno_R2 = str(row.get('Apellido Paterno R2', '')).strip()
                apellido_materno_R2 = str(row.get('Apellido Materno R2', '')).strip()
                celular_R2 = str(row.get('Celular R2', '')).strip()
                email_R2 = str(row.get('Email R2', '')).strip() if str(row.get('Email R2', '')).strip() else None
                parentesco_R2 = str(row.get('Parentesco R2', '')).strip()

                cedula_R3 = str(row.get('Cedula R3', '')).strip()
                nombres_R3 = str(row.get('Nombres R3', '')).strip()
                apellido_paterno_R3 = str(row.get('Apellido Paterno R3', '')).strip()
                apellido_materno_R3 = str(row.get('Apellido Materno R3', '')).strip()
                celular_R3 = str(row.get('Celular R3', '')).strip()
                email_R3 = str(row.get('Email R3', '')).strip() if str(row.get('Email R3', '')).strip() else None
                parentesco_R3 = str(row.get('Parentesco R3', '')).strip()

                if not cedula:
                    continue

                user, created = Usuario.objects.get_or_create(username=cedula, defaults={'tipo_usuario': tipo_usuario, 'password': cedula})
                if created:
                    user.set_password(cedula)  # En caso de que el usuario sea creado, establecer la contraseña
                    user.save()
                    print(f"Usuario creado: {user}")
                else:
                    print(f"Usuario existente: {user}")

                estudiante, created = Estudiante.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'cedula': cedula,
                        'primer_nombre': primer_nombre,
                        'segundo_nombre': segundo_nombre,
                        'apellido_Paterno': apellido_Paterno,
                        'apellido_Materno': apellido_Materno,
                        'fecha_nacimiento': fecha_nacimiento,
                        'telefono': telefono,
                        'ciudad': ciudad,
                        'direccion': direccion,
                        'email': email,
                        'cedula_R1': cedula_R1,
                        'nombres_R1': nombres_R1,
                        'apellido_paterno_R1': apellido_paterno_R1,
                        'apellido_materno_R1': apellido_materno_R1,
                        'celular_R1': celular_R1,
                        'email_R1': email_R1,
                        'parentesco_R1': parentesco_R1,
                        'cedula_R2': cedula_R2,
                        'nombres_R2': nombres_R2,
                        'apellido_paterno_R2': apellido_paterno_R2,
                        'apellido_materno_R2': apellido_materno_R2,
                        'celular_R2': celular_R2,
                        'email_R2': email_R2,
                        'parentesco_R2': parentesco_R2,
                        'cedula_R3': cedula_R3,
                        'nombres_R3': nombres_R3,
                        'apellido_paterno_R3': apellido_paterno_R3,
                        'apellido_materno_R3': apellido_materno_R3,
                        'celular_R3': celular_R3,
                        'email_R3': email_R3,
                        'parentesco_R3': parentesco_R3
                    }
                )
                if created:
                    print(f"Estudiante creado: {estudiante}")
                else:
                    print(f"Estudiante existente: {estudiante}")

                
                if not Matricula.objects.filter(estudiante_id=estudiante, curso_id=curso).exists():
                    # Verificar si el estudiante está matriculado en otro curso
                    if Matricula.objects.filter(estudiante_id=estudiante).exists():
                        # Aquí podrías registrar un mensaje en el log o almacenar información sobre el conflicto
                        logger.info(f"El estudiante {estudiante.cedula} ya está matriculado en otro curso.")
                        continue
                    
                    Matricula.objects.create(
                        estudiante_id=estudiante,
                        curso_id=curso,
                        estado= 'ACTIVO'
                    
                
                    )
                    print(f"Registro de matrícula creado para el curso ID {curso_id}")
                    
                else:
                    logger.info(f"El estudiante {estudiante.cedula} ya está matriculado en el curso ID {curso_id}.")

                # Obtener el nombre del estudiante matriculado
                nombre_estudiante = f"{estudiante.primer_nombre} {estudiante.segundo_nombre} {estudiante.apellido_Paterno} {estudiante.apellido_Materno}"



                # Obtener el nombre del curso para usarlo en el correo
                nombre_curso = curso.nombre

                # Obtener las asignaturas del curso y el docente que las imparte
                asignaturas_docentes = CursoAsignatura.objects.filter(curso_id=curso).select_related('asignatura_id', 'docente_id')
                lista_asignaturas_docentes = [
                    {
                        'asignatura': asignatura_docente.asignatura_id.nombre,
                        'docente': f"{asignatura_docente.docente_id.primer_nombre} {asignatura_docente.docente_id.apellido_Paterno}"
                    }
                    for asignatura_docente in asignaturas_docentes
                ]

                # Imprimir para depuración
                print("Lista de asignaturas y docentes:", lista_asignaturas_docentes)

                # Enviar correo de bienvenida
                emails = obtener_emails_validos(email, email_R1, email_R2, email_R3)

                for recipient_email in emails:
                    if recipient_email:
                        email_enviado = False
                        if recipient_email == email:
                            nombre_para_correo = f"{apellido_Paterno} {apellido_Materno} {primer_nombre} {segundo_nombre}"
                            email_enviado = estudiante.email_enviado
                        elif recipient_email == email_R1:
                            nombre_para_correo = f"{apellido_paterno_R1} {apellido_materno_R1} {nombres_R1}"
                            email_enviado = estudiante.email_enviado_R1
                        elif recipient_email == email_R2:
                            nombre_para_correo = f"{apellido_paterno_R2} {apellido_materno_R2} {nombres_R2}"
                            email_enviado = estudiante.email_enviado_R2
                        elif recipient_email == email_R3:
                            nombre_para_correo = f"{apellido_paterno_R3} {apellido_materno_R3} {nombres_R3}"
                            email_enviado = estudiante.email_enviado_R3

                        if not email_enviado:
                            # Renderizar el contenido del correo con el nombre del curso y las asignaturas con docentes
                            html_content = render_to_string('../templates/Administrador/email.html', {
                                'nombre_estudiante' : nombre_estudiante,
                                'nombre': nombre_para_correo,
                                'curso': nombre_curso,  # Añadir el nombre del curso
                                'lista_asignaturas_docentes': lista_asignaturas_docentes  # Añadir las asignaturas y docentes
                            })

                            # Verificar el contenido renderizado para depuración
                            print("Contenido del correo HTML:", html_content)

                            email_message = EmailMessage(
                                'Bienvenido a nuestro sistema académico',
                                html_content,
                                settings.EMAIL_HOST_USER,
                                [recipient_email]
                            )
                            email_message.content_subtype = 'html'
                            email_message.send()
                            print(f"Correo enviado a {recipient_email}")

                            if recipient_email == email:
                                estudiante.email_enviado = True
                            elif recipient_email == email_R1:
                                estudiante.email_enviado_R1 = True
                            elif recipient_email == email_R2:
                                estudiante.email_enviado_R2 = True
                            elif recipient_email == email_R3:
                                estudiante.email_enviado_R3 = True
                            
                            estudiante.save()

            return JsonResponse({'success': True, 'message': 'Importación completada exitosamente'})

        except Exception as e:
            logger.error(f"Error al procesar el archivo Excel: {e}")
            return JsonResponse({'success': False, 'error': f'Error al procesar el archivo Excel: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)



@csrf_exempt
def importar_clases(request):
    if request.method == 'POST' and 'archivoImportar' in request.FILES:
        archivo_excel = request.FILES['archivoImportar']

        try:
            df = pd.read_excel(archivo_excel)

            # Recorre cada fila del DataFrame y busca o crea las instancias necesarias
            for _, row in df.iterrows():

                # Convertir el nombre del docente a mayúsculas
                nombre_completo = row['docente'].split()
                if len(nombre_completo) < 4:
                    return JsonResponse({'success': False, 'message': 'El nombre completo del docente no está bien formateado.'})
                
                apellido_Paterno = nombre_completo[0].upper()
                apellido_Materno = nombre_completo[1].upper() if len(nombre_completo) > 2 else ''
                primer_nombre = nombre_completo[-2].upper()
                segundo_nombre = nombre_completo[-1].upper()

                try:
                    docente = Docente.objects.get(
                        apellido_Paterno=apellido_Paterno,
                        apellido_Materno=apellido_Materno,
                        primer_nombre=primer_nombre,
                        segundo_nombre=segundo_nombre
                    )
                except Docente.DoesNotExist:
                    return JsonResponse({'success': False, 'message': f'El docente {row["docente"]} no existe en la base de datos.'})

                # Convertir el nombre del curso y asignatura a mayúsculas
                curso_nombre = row['curso'].upper()
                try:
                    curso = Curso.objects.get(nombre=curso_nombre)
                except Curso.DoesNotExist:
                    return JsonResponse({'success': False, 'message': f'El curso {row["curso"]} no existe en la base de datos.'})

                # Convertir el nombre de la asignatura a mayúsculas
                asignatura_nombre = row['asignatura'].upper()
                asignaturas = Asignatura.objects.filter(nombre=asignatura_nombre)

                if asignaturas.exists():
                    asignatura = asignaturas.first()
                else:
                    return JsonResponse({'success': False, 'message': f'La asignatura {row["asignatura"]} no existe en la base de datos.'})

                # Crear la relación en CursoAsignatura
                CursoAsignatura.objects.get_or_create(
                    asignatura_id=asignatura,
                    docente_id=docente,
                    curso_id=curso
                )

            return JsonResponse({'success': True, 'message': 'Clases importadas correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al importar las clases: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido o archivo no proporcionado.'})


@csrf_exempt
def importar_asignaturas(request):
    if request.method == 'POST' and 'archivoImportarAsignatura' in request.FILES:
        archivo_excel = request.FILES['archivoImportarAsignatura']

        try:
            df = pd.read_excel(archivo_excel)

            # Recorre cada fila del DataFrame y busca o crea las instancias necesarias
            for _, row in df.iterrows():
                
               # Buscar o crear la asignatura por nombre
                Asignatura.objects.get_or_create(
                    nombre=row['nombre'],
                    nivel=row['nivel'],
                    descripcion=row['descripcion']
                )
                

            return JsonResponse({'success': True, 'message': 'Asignaturas importadas correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al importar las asignaturas: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido o archivo no proporcionado.'})