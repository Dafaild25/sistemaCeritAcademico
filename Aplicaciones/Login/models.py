
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import cast
from datetime import date
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
from django.db.models import UniqueConstraint,Sum
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ 
from django.core.validators import MinValueValidator, MaxValueValidator
import logging

# cambio poderoso
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from django.db.models import Sum
class UsuarioManager(BaseUserManager):
    def create_user(self, username,  password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username=username, password=password, **extra_fields)

class Usuario(AbstractUser):
    
    tipo_usuario = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('docente', 'Docente'), ('estudiante', 'Estudiante')])
    objects = UsuarioManager()

class Escuela(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    rector = models.CharField(max_length=255)
    fundacion = models.PositiveIntegerField()
    vision = models.TextField()
    mision = models.TextField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='admin')
    cedula=models.CharField(max_length=12, unique=True)
    primer_nombre = models.CharField(max_length=150)
    segundo_nombre = models.CharField(max_length=150)
    apellido_Paterno = models.CharField(max_length=150)
    apellido_Materno = models.CharField(max_length=150)
    telefono = models.CharField(max_length=12)
    direccion = models.CharField(max_length=150)
    email = models.EmailField()

    # Convertir los campos de texto a mayúsculas antes de guardar
    def save(self, *args, **kwargs):
        self.primer_nombre = self.primer_nombre.upper()
        self.segundo_nombre = self.segundo_nombre.upper()
        self.apellido_Paterno = self.apellido_Paterno.upper()
        self.apellido_Materno = self.apellido_Materno.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.apellido_Paterno} {self.apellido_Materno} {self.primer_nombre} {self.segundo_nombre}"

class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='docente')
    cedula=models.CharField(max_length=12, unique=True)
    primer_nombre = models.CharField(max_length=150)
    segundo_nombre = models.CharField(max_length=150)
    apellido_Paterno=models.CharField(max_length=150)
    apellido_Materno=models.CharField(max_length=150)
    telefono=models.CharField(max_length=12)
    direccion = models.CharField(max_length=150)
    email=models.EmailField()
    especialidad=models.CharField(max_length=50)
    estado = models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')

    # Convertir los campos de texto a mayúsculas o minusculas antes de guardar
    def save(self,*args, **kwargs):
        self.primer_nombre=self.primer_nombre.upper()
        self.segundo_nombre=self.segundo_nombre.upper()
        self.apellido_Paterno=self.apellido_Paterno.upper()
        self.apellido_Materno=self.apellido_Materno.upper()
        self.especialidad=self.especialidad.upper()
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.apellido_Paterno} {self.apellido_Materno} {self.primer_nombre} {self.segundo_nombre}"



    
# Periodo academico    
class PeriodoAcademico(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad = models.IntegerField(
        null=True,  # Permitir valores nulos
        blank=True,  # Permitir que el campo esté vacío en los formularios
        default=2,  # Valor por defecto es 2
        validators=[
            MinValueValidator(2),  # Valor mínimo es 2
            MaxValueValidator(5)   # Valor máximo es 5
        ]
    )
    estado = models.CharField(max_length=8, choices=ESTADO_CHOICES, default='ACTIVO')
    version = models.IntegerField(default=0)  # Campo de versión para manejar la concurrencia
    
    def save(self, *args, **kwargs):
        # Convertir los campos de texto a mayúsculas antes de guardar
        self.nombre = self.nombre.upper()
        self.descripcion = self.descripcion.upper()
        self.estado = self.estado.upper()
        # Incrementar la versión en cada actualización
        if self.pk is not None:
            self.version += 1
        super().save(*args, **kwargs)
        
        

        
    def __str__(self):
        return self.nombre

# Cursos
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    paralelo = models.CharField(max_length=10)
    periodoAcademico_id = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE,null=True, blank=True)
    estado = models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    descripcion = models.TextField()
    

    def save(self, *args, **kwargs):
        # Convertir los campos de texto a mayúsculas antes de guardar
        self.nombre = self.nombre.upper()
        self.paralelo = self.paralelo.upper()
        self.estado = self.estado.upper()
        self.descripcion = self.descripcion.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.paralelo}"
    


class Estudiante(models.Model):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estudiante')
    cedula=models.CharField(max_length=12, unique=True)
    primer_nombre = models.CharField(max_length=150)
    segundo_nombre = models.CharField(max_length=150)
    apellido_Paterno = models.CharField(max_length=150)
    apellido_Materno = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=12, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    estado = models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    email_enviado = models.BooleanField(default=False)  # Campo para rastrear el envío
    
    #curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    
    # Representante 1
    cedula_R1 = models.CharField(max_length=20, blank=True, null=True)
    nombres_R1 = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno_R1 = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno_R1 = models.CharField(max_length=100, blank=True, null=True)
    celular_R1 = models.CharField(max_length=20, blank=True, null=True)
    email_R1 = models.EmailField(blank=True, null=True)
    estado_R1 = models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    parentesco_R1 = models.CharField(max_length=50, blank=True, null=True)
    email_enviado_R1 = models.BooleanField(default=False)  # Campo para rastrear el envío

    # Representante 2
    cedula_R2 = models.CharField(max_length=20, blank=True, null=True)
    nombres_R2 = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno_R2 = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno_R2 = models.CharField(max_length=100, blank=True, null=True)
    celular_R2 = models.CharField(max_length=20, blank=True, null=True)
    email_R2 = models.EmailField(blank=True, null=True)
    estado_R2=models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    parentesco_R2 = models.CharField(max_length=50, blank=True, null=True)
    email_enviado_R2 = models.BooleanField(default=False)  # Campo para rastrear el envío

    # Representante 3
    cedula_R3 = models.CharField(max_length=20, blank=True, null=True)
    nombres_R3 = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno_R3 = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno_R3 = models.CharField(max_length=100, blank=True, null=True)
    celular_R3 = models.CharField(max_length=20, blank=True, null=True)
    email_R3 = models.EmailField(blank=True, null=True)
    estado_R3=models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    parentesco_R3 = models.CharField(max_length=50, blank=True, null=True)
    email_enviado_R3 = models.BooleanField(default=False)  # Campo para rastrear el envío
    
    
    

    # Convertir los campos de texto a mayúsculas antes de guardar
    def save(self, *args, **kwargs):
        self.primer_nombre = self.primer_nombre.upper()
        self.segundo_nombre = self.segundo_nombre.upper()
        self.apellido_Paterno = self.apellido_Paterno.upper()
        self.apellido_Materno = self.apellido_Materno.upper()
        self.ciudad = self.ciudad.upper()
        if self.email:
            self.email=self.email.lower()
        
        # Datos de los representantes
        if self.nombres_R1:
            self.nombres_R1 = self.nombres_R1.upper()
        if self.apellido_paterno_R1:
            self.apellido_paterno_R1 = self.apellido_paterno_R1.upper()
        if self.apellido_materno_R1:
            self.apellido_materno_R1 = self.apellido_materno_R1.upper()
        if self.email_R1:
            self.email_R1 = self.email_R1.lower()
        
        if self.nombres_R2:
            self.nombres_R2 = self.nombres_R2.upper()
        if self.apellido_paterno_R2:
            self.apellido_paterno_R2 = self.apellido_paterno_R2.upper()
        if self.apellido_materno_R2:
            self.apellido_materno_R2 = self.apellido_materno_R2.upper()
        if self.email_R2:
            self.email_R2 = self.email_R2.lower()
        
        if self.nombres_R3:
            self.nombres_R3 = self.nombres_R3.upper()
        if self.apellido_paterno_R3:
            self.apellido_paterno_R3 = self.apellido_paterno_R3.upper()
        if self.apellido_materno_R3:
            self.apellido_materno_R3 = self.apellido_materno_R3.upper()
        if self.email_R3:
            self.email_R3 = self.email_R3.lower()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.apellido_Paterno} {self.apellido_Materno} {self.primer_nombre} {self.segundo_nombre}"

    
class Asignatura (models.Model):
    nombre=models.CharField(max_length=150)
    nivel=models.CharField(max_length=20,choices=[('INICIAL','Inicial'),('BASICO','Basico'),('BACHILLERATO','Bachillerato')],default='INICIAL')
    estado = models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    descripcion = models.TextField()
    # Convertir los campos de texto a mayúsculas antes de guardar
    def save(self,*args, **kwargs):
        self.nombre=self.nombre.upper()
        self.nivel=self.nivel.upper()
        self.estado=self.estado.upper()

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nombre} - {self.nivel}"


# Relacion entre Docente Asigantura y curso 

class CursoAsignatura (models.Model):
    asignatura_id = models.ForeignKey(Asignatura, on_delete=models.CASCADE,null=True, blank=True)
    docente_id = models.ForeignKey(Docente, on_delete=models.CASCADE,null=True, blank=True)
    curso_id = models.ForeignKey(Curso, on_delete=models.CASCADE,null=True, blank=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['asignatura_id', 'curso_id'], name='unique_asignatura_curso')
        ]
    
    def __str__(self) -> str:
        return f'{self.curso_id}-{self.asignatura_id}'



# vamos por las calificaciones 

# debemos genera la division academica es decir donde estaran los trimestres
class PeriodoDivision(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del trimestre, por ejemplo, 'Primer Trimestre'
    periodo_academico = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    
    # Convertir los campos de texto a mayúsculas antes de guardar
    def save(self,*args, **kwargs):
        self.nombre=self.nombre.upper()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nombre} - {self.periodo_academico.nombre}"



# SEGUNDO debemos tener un tipo de evaluacion
class TipoEvaluacion(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del tipo de evaluación
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2)  # Ponderación en porcentaje
    
    trimestre_id = models.ForeignKey(PeriodoDivision, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, default='#FFFFFF', null=True, blank=True)  # Código de color opcional


    
    
        
    # Convertir los campos de texto a mayúsculas antes de guardar
    def save(self,*args, **kwargs):
        self.nombre=self.nombre.upper()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nombre} ({self.ponderacion}% - {self.trimestre_id})"


class Matricula(models.Model):
    estudiante_id = models.ForeignKey(Estudiante,on_delete=models.CASCADE)  
    curso_id = models.ForeignKey(Curso,on_delete=models.CASCADE)
    estado = models.CharField(max_length=8, choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')], default='ACTIVO')
    
    def __str__(self):
        return f"{self.estudiante_id} ({self.curso_id}- {self.estado})"


class EquivalentesTipoEvaluacion(models.Model):
    matricula_id= models.ForeignKey(Matricula,on_delete=models.CASCADE)
    trimestre_id = models.ForeignKey(PeriodoDivision, on_delete=models.CASCADE)
    tipoEvaluacion_id = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    promedioTipo = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
        validators=[
            MinValueValidator(0.00),  # Valor mínimo 0.00
            MaxValueValidator(10.00)  # Valor máximo 10.00 
        ]
    )
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')

class subpromedioTipoEvaluacion(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    trimestre_id = models.ForeignKey(PeriodoDivision,on_delete=models.CASCADE)
    tipoEvaluacion_id = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    evaluacionPromedio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
        validators=[
            MinValueValidator(0.00),  # Valor mínimo 0.00
            MaxValueValidator(10.00)  # Valor máximo 10.00 
        ]
    )
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')




# mejoras del codigo 
class ExamenTrimestral(models.Model):
    ESTADO_OPCIONES = [
        ('ACTIVO', 'ACTIVO'),
        ('INACTIVO', 'INACTIVO')
    ]
    nombre = models.CharField(max_length=100)
    trimestre_id = models.ForeignKey(PeriodoDivision, on_delete=models.CASCADE)
    descripcion = models.TextField(default='NINGUNA', blank=True)
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(
        max_length=8,
        choices=ESTADO_OPCIONES,
        default='ACTIVO'
    )

    def __str__(self):
        return self.nombre
    

class ExamenFinal(models.Model):
    ESTADO_OPCIONES = [
        ('ACTIVO', 'ACTIVO'),
        ('INACTIVO', 'INACTIVO')
    ]
    nombre = models.CharField(max_length=100)
    periodoAcademico_id = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)
    descripcion = models.TextField(default='NINGUNA', blank=True)
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(
        max_length=8,
        choices=ESTADO_OPCIONES,
        default='ACTIVO'
    )

    def __str__(self):
        return self.nombre
    
class UnidadTrimestral (models.Model):
    nombre = models.CharField(max_length=100)
    trimestre_id = models.ForeignKey(PeriodoDivision, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre
    
class PromedioTipos(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    trimestre_id = models.ForeignKey(PeriodoDivision,on_delete=models.CASCADE)
    unidad_id = models.ForeignKey(UnidadTrimestral,blank=True, null=True,on_delete=models.CASCADE)
    curso_asignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, null=True, blank=True)
    tipoEvaluacion_id = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    subpromedioTipo = models.DecimalField(max_digits=7, decimal_places=5, default=0.00000,
        validators=[
            MinValueValidator(0.00000),  # Valor mínimo
            MaxValueValidator(10.00000)   # Valor máximo
        ])
    subEquivalenteTipo = models.DecimalField(max_digits=7, decimal_places=5, default=0.00000, blank=True,null=True,
        validators=[
            MinValueValidator(0.00000),  # Valor mínimo
            MaxValueValidator(10.00000)   # Valor máximo
        ])
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')
    
class PromedioUnidades(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    trimestre_id = models.ForeignKey(PeriodoDivision,on_delete=models.CASCADE)
    unidad_id = models.ForeignKey(UnidadTrimestral,blank=True, null=True,on_delete=models.CASCADE)
    curso_asignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, null=True, blank=True)
    subPromedioUnidad = models.DecimalField(max_digits=7, decimal_places=5, default=0.00000,
        validators=[
            MinValueValidator(0.00000),  # Valor mínimo
            MaxValueValidator(10.00000)   # Valor máximo
        ])
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')    

class PromedioTrimestres(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    trimestre_id = models.ForeignKey(PeriodoDivision,on_delete=models.CASCADE)
    curso_asignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, null=True, blank=True)
    promedioTrimestral = models.DecimalField(max_digits=7,decimal_places=5, default=0.000,
        validators=[
            MinValueValidator(0.00000),  # Valor mínimo
            MaxValueValidator(10.00000)   # Valor máximo
        ])
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')    

class PromedioTrimestresAsignatura(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    curso_asignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, null=True, blank=True)
    periodoAcademico_id =models.ForeignKey(PeriodoAcademico,on_delete=models.CASCADE)
    promedioTrimestral = models.DecimalField(max_digits=7,decimal_places=5, default=0.000,
        validators=[
            MinValueValidator(0.00000),  # Valor mínimo
            MaxValueValidator(10.00000)   # Valor máximo
        ])
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')  
 
# aqui esta los  importantes para los promedios 
    
class Aporte (models.Model):
    nombre= models.CharField(max_length=100)
    cursoAsignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE) #esto cambie recien
    fecha = models.DateField()
    tipo_id = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    unidad_id= models.ForeignKey(UnidadTrimestral, on_delete=models.CASCADE,blank=True,null=True)
    
    def save(self, *args , **kwargs):
        self.nombre= self.nombre.upper()
        super().save(*args, **kwargs)


# ahora si la tabla de calificaciones
class Calificacion(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    aporte_id = models.ForeignKey(Aporte, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
        validators=[
            MinValueValidator(0.00),  # Valor mínimo 0.00
            MaxValueValidator(10.00)  # Valor máximo 10.00 
        ]
    )
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNO')
    def __str__(self):

        return f"{self.matricula_id} - {self.aporte_id} - {format(self.nota, '.2f')}"
    
class CalificacionExamen(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    examen_id = models.ForeignKey(ExamenTrimestral, on_delete=models.CASCADE)
    curso_asignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, null=True, blank=True)
    nota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
        validators=[
            MinValueValidator(0.00),  # Valor mínimo 0.00
            MaxValueValidator(10.00)  # Valor máximo 10.00 
        ]
    )
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')
    def __str__(self):


        return f"{self.matricula_id} - {self.examen_id} - {format(self.nota, '.2f')}" 

class CalificacionExamenSupletorio(models.Model):
    matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
    examen_id = models.ForeignKey(ExamenFinal, on_delete=models.CASCADE)
    curso_asignatura_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, null=True, blank=True)
    nota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
        validators=[
            MinValueValidator(0.00),  # Valor mínimo 0.00
            MaxValueValidator(10.00)  # Valor máximo 10.00 
        ]
    )
    observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA')
    def __str__(self):


        return f"{self.matricula_id} - {self.examen_id} - {format(self.nota, '.2f')}"

class PromedioPeriodical(models.Model):
        matricula_id = models.ForeignKey(Matricula,on_delete=models.CASCADE)
        periodoAcademico_id = models.ForeignKey(PeriodoDivision,on_delete=models.CASCADE)
        curso_id = models.ForeignKey(Curso,on_delete=models.CASCADE,blank=True,null=True)
        promedioPeriodicalGeneral = models.DecimalField(max_digits=7,decimal_places=5, default=0.000,
            validators=[
                MinValueValidator(0.00000),  # Valor mínimo
                MaxValueValidator(10.00000)   # Valor máximo
            ])
        observacion = models.CharField(max_length=100, blank=True, null=True, default='NINGUNA') 




@receiver(post_save, sender=Calificacion)
def calcular_promedioTipos(sender, instance, **kwargs):
    tipo_evaluacion = instance.aporte_id.tipo_id
    matricula = instance.matricula_id
    unidad = instance.aporte_id.unidad_id 
    trimestre = tipo_evaluacion.trimestre_id
    curso_asignatura = instance.aporte_id.cursoAsignatura_id
    # Obtener todas las calificaciones para el mismo `matricula`, `tipo_evaluacion`, `unidad` y `trimestre`
    calificaciones = Calificacion.objects.filter(
        matricula_id=matricula,
        aporte_id__tipo_id=tipo_evaluacion,
        aporte_id__unidad_id=unidad
    )

    # Calcular el promedio
    if calificaciones.exists():
        promedio = calificaciones.aggregate(models.Avg('nota'))['nota__avg']

        # Obtener la ponderación
        ponderacion = tipo_evaluacion.ponderacion / 100  # Convertir a decimal

        # Calcular el subequivalente
        sub_equivalente = promedio * ponderacion

        # Aplicar la cantidad de decimales definida en PeriodoAcademico
        cantidad_decimales = tipo_evaluacion.trimestre_id.periodo_academico.cantidad
        promedio = promedio.quantize(Decimal('1.' + '0' * cantidad_decimales), rounding=ROUND_DOWN)
        sub_equivalente = sub_equivalente.quantize(Decimal('1.' + '0' * cantidad_decimales), rounding=ROUND_DOWN)

        # Actualizar o crear un registro en PromedioTipos
        PromedioTipos.objects.update_or_create(
            matricula_id=matricula,
            trimestre_id=trimestre,
            unidad_id=unidad,
            tipoEvaluacion_id=tipo_evaluacion,
            curso_asignatura_id=curso_asignatura,
            defaults={
                'subpromedioTipo': promedio,
                'subEquivalenteTipo': sub_equivalente
            }
        )

@receiver(post_delete, sender=Calificacion)
def actualizar_promedioTipos_post_delete(sender, instance, **kwargs):
    tipo_evaluacion = instance.aporte_id.tipo_id
    matricula = instance.matricula_id
    unidad = instance.aporte_id.unidad_id
    trimestre = tipo_evaluacion.trimestre_id
    curso_asignatura = instance.aporte_id.cursoAsignatura_id
    # Obtener todas las calificaciones restantes después de la eliminación
    calificaciones = Calificacion.objects.filter(
        matricula_id=matricula,
        aporte_id__tipo_id=tipo_evaluacion,
        aporte_id__unidad_id=unidad
    )

    # Calcular el nuevo promedio o eliminar el registro si ya no hay calificaciones
    if calificaciones.exists():
        promedio = calificaciones.aggregate(models.Avg('nota'))['nota__avg']

        # Obtener la ponderación
        ponderacion = tipo_evaluacion.ponderacion / 100  # Convertir a decimal

        # Calcular el subequivalente
        sub_equivalente = promedio * ponderacion

        # Aplicar la cantidad de decimales definida en PeriodoAcademico
        cantidad_decimales = tipo_evaluacion.trimestre_id.periodo_academico.cantidad
        promedio = promedio.quantize(Decimal('1.' + '0' * cantidad_decimales), rounding=ROUND_DOWN)
        sub_equivalente = sub_equivalente.quantize(Decimal('1.' + '0' * cantidad_decimales), rounding=ROUND_DOWN)

        # Actualizar el registro en PromedioTipos
        PromedioTipos.objects.update_or_create(
            matricula_id=matricula,
            trimestre_id=trimestre,
            unidad_id=unidad,
            tipoEvaluacion_id=tipo_evaluacion,
            curso_asignatura_id=curso_asignatura,
            defaults={
                'subpromedioTipo': promedio,
                'subEquivalenteTipo': sub_equivalente
            }
        )
    else:
        # Si no hay calificaciones restantes, eliminar el promedio asociado
        PromedioTipos.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre,
            unidad_id=unidad,
            curso_asignatura_id=curso_asignatura,
            tipoEvaluacion_id=tipo_evaluacion
        ).delete()
        
@receiver(post_save, sender=PromedioTipos)
def calcular_promedio_unidades(sender, instance, created, **kwargs):
    # Obtener los parámetros necesarios de la instancia de PromedioTipos
    matricula = instance.matricula_id
    trimestre = instance.trimestre_id
    unidad = instance.unidad_id
    curso_asignatura = instance.curso_asignatura_id
    # Obtener todos los subEquivalenteTipo de PromedioTipos relacionados
    sub_equivalentes = PromedioTipos.objects.filter(
        matricula_id=matricula,
        trimestre_id=trimestre,
        unidad_id=unidad,
        curso_asignatura_id=curso_asignatura
    ).values_list('subEquivalenteTipo', flat=True)

    # Calcular el nuevo subPromedioUnidad (sumar todos los subEquivalenteTipo)
    if sub_equivalentes:
        suma_sub_equivalentes = sum(sub_equivalentes)
        cantidad_sub_equivalentes = len(sub_equivalentes)

        # Calcular el promedio dividiendo la suma total por la cantidad
        nuevo_promedio = suma_sub_equivalentes / cantidad_sub_equivalentes
    else:
        nuevo_promedio = 0.00000

    # Redondear según la cantidad de decimales definida en el PeriodoAcademico
    cantidad_decimales = instance.trimestre_id.periodo_academico.cantidad
    nuevo_promedio = round(nuevo_promedio, cantidad_decimales)

    # Actualizar o crear el promedio en PromedioUnidades
    PromedioUnidades.objects.update_or_create(
        matricula_id=matricula,
        trimestre_id=trimestre,
        unidad_id=unidad,
        curso_asignatura_id=curso_asignatura,
        defaults={'subPromedioUnidad': nuevo_promedio}
    )
    
@receiver(post_delete, sender=PromedioTipos)
def eliminar_promedio_unidades(sender, instance, **kwargs):
    matricula = instance.matricula_id
    trimestre = instance.trimestre_id
    unidad = instance.unidad_id
    curso_asignatura = instance.curso_asignatura_id

    # Verificar si aún quedan otros promedios para la misma unidad, trimestre y matrícula
    promedios_tipos_restantes = PromedioTipos.objects.filter(
        matricula_id=matricula,
        trimestre_id=trimestre,
        curso_asignatura_id=curso_asignatura,
        unidad_id=unidad
    )

    if promedios_tipos_restantes.exists():
        # Si quedan otros promedios, recalcular el nuevo subPromedioUnidad
        suma_sub_equivalentes = promedios_tipos_restantes.aggregate(models.Sum('subEquivalenteTipo'))['subEquivalenteTipo__sum']
        cantidad_sub_equivalentes = promedios_tipos_restantes.count()

        # Calcular el nuevo promedio dividiendo la suma por la cantidad restante de subEquivalenteTipo
        nuevo_promedio = suma_sub_equivalentes / cantidad_sub_equivalentes

        # Obtener la cantidad de decimales desde el periodo académico
        cantidad_decimales = instance.trimestre_id.periodo_academico.cantidad

        # Redondear el nuevo promedio
        nuevo_promedio = round(nuevo_promedio, cantidad_decimales)

        # Actualizar o crear el registro en PromedioUnidades
        PromedioUnidades.objects.update_or_create(
            matricula_id=matricula,
            trimestre_id=trimestre,
            curso_asignatura_id=curso_asignatura,
            unidad_id=unidad,
            defaults={'subPromedioUnidad': nuevo_promedio}
        )
    else:
        # Si no hay más promedios, eliminar el registro de PromedioUnidades
        PromedioUnidades.objects.filter(
            matricula_id=matricula,
            trimestre_id=trimestre,
            curso_asignatura_id=curso_asignatura,
            unidad_id=unidad
        ).delete()
        
@receiver(post_delete, sender=UnidadTrimestral)
def eliminar_datos_asociados(sender, instance, **kwargs):
    # Obtener el trimestre relacionado con la unidad eliminada
    trimestre = instance.trimestre_id

    # Eliminar calificaciones relacionadas
    Calificacion.objects.filter(aporte_id__unidad_id=instance).delete()

    # Eliminar promedios relacionados
    PromedioTipos.objects.filter(unidad_id=instance).delete()

    # Puedes agregar más lógica aquí si es necesario
    print(f'Datos asociados a la Unidad Trimestral "{instance.nombre}" eliminados.')
    
    
# señal para guardar el promedio trimestral  debe conciderarse las unidades 
@receiver(post_save, sender=PromedioUnidades)
@receiver(post_save, sender=CalificacionExamen)
def calcular_promedio_trimestral(sender, instance, **kwargs):
    matricula_id = instance.matricula_id
    trimestre_id = instance.trimestre_id if sender == PromedioUnidades else instance.examen_id.trimestre_id
    
    curso_asignatura = instance.curso_asignatura_id
    
     # Contar el número total de unidades asociadas al trimestre
    total_unidades_trimestre = UnidadTrimestral.objects.filter(
        trimestre_id=trimestre_id
    ).count()


    # Obtener todas las subPromedios de las unidades y calcular su promedio
    sub_promedios = PromedioUnidades.objects.filter(
        matricula_id=matricula_id,
        trimestre_id=trimestre_id,
        curso_asignatura_id =curso_asignatura
    
    )
    
    # Sumar las calificaciones de las unidades registradas
    total_calificaciones = sub_promedios.aggregate(total=models.Sum('subPromedioUnidad'))['total'] or Decimal('0.0')
    
    # Si hay unidades registradas, calcular el promedio de esas unidades
    if total_unidades_trimestre > 0:
        promedio_unidades = total_calificaciones / total_unidades_trimestre
    else:
        promedio_unidades = Decimal('0.0')
    
    #promedio_unidades = sub_promedios.aggregate(promedio=models.Avg('subPromedioUnidad'))['promedio'] or Decimal('0.0')

    # Obtener la calificación del examen más reciente
    calificacion_examen = CalificacionExamen.objects.filter(
        matricula_id=matricula_id,
        examen_id__trimestre_id=trimestre_id,
        curso_asignatura_id=curso_asignatura
        ).last()
    
    # Si no hay examen trimestral o el campo `nota` está vacío o es nulo, asignar 0.00
    nota_examen = Decimal('0.0')
    if calificacion_examen and calificacion_examen.nota is not None:
        nota_examen = calificacion_examen.nota


    #Convertir los coeficientes a Decimal y calcular el promedio trimestral
    promedio_trimestral = (Decimal('0.7') * promedio_unidades) + (Decimal('0.3') * nota_examen)
    
    # Obtener el curso_asignatura_id (esto dependerá de tu lógica, como puede ser un campo en `instance`)
    
    # Guardar o actualizar el promedio trimestral en PromedioTrimestres
    PromedioTrimestres.objects.update_or_create(
        matricula_id=matricula_id,
        trimestre_id=trimestre_id,
        curso_asignatura_id=curso_asignatura,
        defaults={'promedioTrimestral': promedio_trimestral}
    )
    
    
# cuando de borra el promedio de unidades  o calificaciones de examen
@receiver(post_delete, sender=PromedioUnidades)
@receiver(post_delete, sender=CalificacionExamen)
def eliminar_promedio_trimestral(sender, instance, **kwargs):
    matricula_id = instance.matricula_id
    trimestre_id = instance.trimestre_id if sender == PromedioUnidades else instance.examen_id.trimestre_id
    curso_asignatura = instance.curso_asignatura_id

    # Eliminar el promedio trimestral relacionado
    PromedioTrimestres.objects.filter(
        matricula_id=matricula_id,
        trimestre_id=trimestre_id,
        curso_asignatura_id=curso_asignatura
    ).delete()



# para calcular el promedio general cuando se crea 

@receiver(post_save, sender=PromedioTrimestres)
def actualizar_promedio_asignatura(sender, instance, **kwargs):
    from django.db.models import F
    from decimal import Decimal  # Asegurarse de importar Decimal para las operaciones precisas

    # Extraer datos del registro actual
    matricula_id = instance.matricula_id
    curso_asignatura_id = instance.curso_asignatura_id
    periodo_academico_id = instance.trimestre_id.periodo_academico  

    # Obtener todos los trimestres para el periodo académico actual
    trimestres_ids = PeriodoDivision.objects.filter(periodo_academico=periodo_academico_id).values_list('id', flat=True)

    # Filtrar registros de promedios para los trimestres existentes
    promedios_existentes = PromedioTrimestres.objects.filter(
        matricula_id=matricula_id,
        curso_asignatura_id=curso_asignatura_id,
        trimestre_id__in=trimestres_ids
    ).values('trimestre_id').annotate(valor=F('promedioTrimestral'))

    # Crear un diccionario de los promedios existentes
    promedios_dict = {item['trimestre_id']: item['valor'] for item in promedios_existentes}

    # Calcular el promedio considerando trimestres con 0 donde no hay datos
    total_trimestres = len(trimestres_ids)
    suma_promedios = sum(Decimal(promedios_dict.get(trimestre_id, 0.00000)) for trimestre_id in trimestres_ids)
    promedio = suma_promedios / Decimal(total_trimestres) if total_trimestres > 0 else Decimal('0.00000')

    # Determinar la observación en base al promedio
    if promedio < 7:
        observacion = 'REPROBADO'
    else:
        observacion = 'APROBADO'

    # Obtener o crear el registro en `PromedioTrimestresAsignatura`
    promedio_asignatura, created = PromedioTrimestresAsignatura.objects.get_or_create(
        matricula_id=matricula_id,
        curso_asignatura_id=curso_asignatura_id,
        periodoAcademico_id=periodo_academico_id,
        defaults={'promedioTrimestral': promedio, 'observacion': observacion}
    )

    # Si el registro ya existía, actualizar el promedio y la observación
    if not created:
        promedio_asignatura.promedioTrimestral = promedio
        promedio_asignatura.observacion = observacion
        promedio_asignatura.save()


# para calcular el promedio general cuando se crea 
@receiver(post_delete, sender=PromedioTrimestres)
def recalcular_promedio_asignatura(sender, instance, **kwargs):
    from django.db.models import F  # Import necesario para trabajar con anotaciones

    # Extraer datos del registro eliminado
    matricula_id = instance.matricula_id
    curso_asignatura_id = instance.curso_asignatura_id
    periodo_academico_id = instance.trimestre_id.periodo_academico

    # Obtener todos los trimestres para el periodo académico actual
    trimestres_ids = PeriodoDivision.objects.filter(periodo_academico=periodo_academico_id).values_list('id', flat=True)

    # Filtrar registros de promedios para los trimestres existentes
    promedios_existentes = PromedioTrimestres.objects.filter(
        matricula_id=matricula_id,
        curso_asignatura_id=curso_asignatura_id,
        trimestre_id__in=trimestres_ids
    ).values('trimestre_id').annotate(valor=F('promedioTrimestral'))

    # Crear un diccionario de los promedios existentes
    promedios_dict = {item['trimestre_id']: item['valor'] for item in promedios_existentes}

    # Calcular el promedio considerando trimestres con 0 donde no hay datos
    total_trimestres = len(trimestres_ids)
    suma_promedios = sum(Decimal(promedios_dict.get(trimestre_id, 0.00000)) for trimestre_id in trimestres_ids)
    promedio = suma_promedios / Decimal(total_trimestres) if total_trimestres > 0 else Decimal('0.00000')

    # Verificar si existe un registro en `PromedioTrimestresAsignatura`
    try:
        promedio_asignatura = PromedioTrimestresAsignatura.objects.get(
            matricula_id=matricula_id,
            curso_asignatura_id=curso_asignatura_id,
            periodoAcademico_id=periodo_academico_id
        )
        # Actualizar el promedio o eliminar si ya no hay trimestres relacionados
        if total_trimestres > 0:
            promedio_asignatura.promedioTrimestral = promedio
            promedio_asignatura.save()
        else:
            promedio_asignatura.delete()
    except PromedioTrimestresAsignatura.DoesNotExist:
        # Si no existe, no hacemos nada
        pass
    
    
    

    # Obtener la matrícula y el periodo académico del registro actual
    matricula = instance.matricula_id  # Obtén la instancia completa de la matrícula
    periodo_academico = instance.periodoAcademico_id.id  # Obtén la instancia completa del periodo académico

    # Obtener el curso_id de la matrícula del estudiante
    curso_id = matricula.curso_id.id  # Obtén solo el ID del curso desde la matrícula

    # Obtener todas las asignaturas del curso en el que está matriculado el estudiante
    curso_asignaturas = CursoAsignatura.objects.filter(curso_id=curso_id)

    # Filtrar los promedios trimestrales para esas asignaturas y el periodo académico
    promedios_trimestrales = PromedioTrimestresAsignatura.objects.filter(
        matricula_id=matricula,
        curso_asignatura_id__in=curso_asignaturas.values_list('id', flat=True),
        periodoAcademico_id=periodo_academico  # Usamos la instancia del periodo académico
    )

    # Calcular la suma de los promedios trimestrales
    total_promedios = sum(promedio.promedioTrimestral for promedio in promedios_trimestrales)
    total_asignaturas = len(promedios_trimestrales)

    # Calcular el promedio general
    if total_asignaturas > 0:
        promedio_final = total_promedios / Decimal(total_asignaturas)
    else:
        promedio_final = Decimal('0.00000')  # Si no hay asignaturas, el promedio es 0

   

    promedio_periodical, created = PromedioPeriodical.objects.get_or_create(
        matricula_id=matricula,  # Pasa la instancia completa de la matrícula
        periodoAcademico_id=periodo_academico,  
        curso_id=curso_id,  # Solo se pasa el ID del curso
        defaults={'promedioPeriodicalGeneral': promedio_final}
    )

    # Si ya existía el registro, actualizar el promedio
    if not created:
        promedio_periodical.promedioPeriodicalGeneral = promedio_final
        promedio_periodical.save()

class Asistencia(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)  # Relaciona la asistencia a un estudiante específico en un curso
    periodo_division = models.ForeignKey(PeriodoDivision, on_delete=models.CASCADE)  # Relaciona la asistencia a una división de período, como un trimestre
    clase_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE) #Relaciona la asistencia a una clase
    fecha = models.DateField(default=date.today)  # Fecha de la asistencia
    
    ESTADO_ASISTENCIA = [
        ('ASISTENCIA', 'Asistencia'),
        ('ATRASO', 'Atraso'),
        ('FALTA JUSTIFICADA', 'Falta Justificada'),
        ('FALTA INJUSTIFICADA', 'Falta Injustificada'),
    ]
    estado = models.CharField(
        max_length=19,
        choices=ESTADO_ASISTENCIA,
        default='ASISTENCIA'
    )
    
    def __str__(self):
        return f"Asistencia de {self.matricula.estudiante_id} en {self.fecha} - {self.estado}"



class AsistenciaTotal(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)  # Relacionado al estudiante
    periodo_division = models.ForeignKey(PeriodoDivision, on_delete=models.CASCADE)  # Relacionado al período
    clase_id = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE)  # Relacionado a la clase
    total_asistencias = models.PositiveIntegerField(default=0)
    total_atrasos = models.PositiveIntegerField(default=0)
    total_faltas_justificadas = models.PositiveIntegerField(default=0)
    total_faltas_injustificadas = models.PositiveIntegerField(default=0)
    total_asistencias_completas = models.PositiveIntegerField(default=0)  # Asistencias + Atrasos
    total_faltas = models.PositiveIntegerField(default=0)  # Faltas justificadas + injustificadas


# Configura el logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Asistencia)
def actualizar_totales_asistencia(sender, instance, **kwargs):
    # Obtener o crear el registro de totales para el estudiante
    totales, created = AsistenciaTotal.objects.get_or_create(
        matricula=instance.matricula,
        periodo_division=instance.periodo_division,
        clase_id=instance.clase_id
    )
    
    # Calcular totales individuales para el estudiante
    asistencias = Asistencia.objects.filter(
        matricula=instance.matricula,
        periodo_division=instance.periodo_division,
        clase_id=instance.clase_id
    )

    totales.total_asistencias = asistencias.filter(estado='ASISTENCIA').count()
    totales.total_atrasos = asistencias.filter(estado='ATRASO').count()
    totales.total_faltas_justificadas = asistencias.filter(estado='FALTA JUSTIFICADA').count()
    totales.total_faltas_injustificadas = asistencias.filter(estado='FALTA INJUSTIFICADA').count()
    
    # Calcular totales combinados
    totales.total_asistencias_completas = totales.total_asistencias + totales.total_atrasos
    totales.total_faltas = totales.total_faltas_justificadas + totales.total_faltas_injustificadas

    # Guardar los totales individuales
    totales.save()

    # Calcular los totales generales para todos los trimestres y clases del mismo estudiante
    totales_generales = AsistenciaTotal.objects.filter(
        matricula=instance.matricula
    ).aggregate(
        asistencias_generales=Sum('total_asistencias_completas'),
        faltas_generales=Sum('total_faltas'),
    )

    # Guardar los totales generales en el registro actual
    totales.asistencias_generales = totales_generales['asistencias_generales'] or 0
    totales.faltas_generales = totales_generales['faltas_generales'] or 0
    totales.save()

    # Enviar mensaje de actualización
    mensaje = (
        f"Totales actualizados para el estudiante {instance.matricula}: "
        f"Asistencias generales: {totales.asistencias_generales}, "
        f"Faltas generales: {totales.faltas_generales}"
    )
    # Aquí se muestra el mensaje en el log del servidor
    logger.info(mensaje)