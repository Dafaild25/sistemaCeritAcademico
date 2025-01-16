from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Usuario,PeriodoAcademico,Curso,Docente,Estudiante,Administrador,Asignatura,CursoAsignatura, Matricula, TipoEvaluacion,Aporte,PeriodoDivision,Calificacion,EquivalentesTipoEvaluacion,subpromedioTipoEvaluacion,Asistencia



class UserAdmin(BaseUserAdmin):
    model = Usuario
    # Define los campos a mostrar en el panel de administración
    list_display = ('username', 'tipo_usuario', 'is_staff', 'is_active')
    # Opcionalmente puedes añadir filtros y campos de búsqueda
    list_filter = ('tipo_usuario', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Definir los campos del formulario para crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'tipo_usuario'),
        }),
    )
    # Definir los campos del formulario para editar un usuario existente
    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined'),
        }),
        ('User Info', {
            'fields': ('tipo_usuario',),
        }),
    )

admin.site.register(Usuario, UserAdmin)
admin.site.register(Docente)
admin.site.register(Estudiante)
admin.site.register(Administrador)

# aqui creo a los modelos 
admin.site.register(PeriodoAcademico)
admin.site.register(Curso)

admin.site.register(Asignatura)

admin.site.register(CursoAsignatura)

admin.site.register(PeriodoDivision)
admin.site.register(TipoEvaluacion)
admin.site.register(Aporte)
admin.site.register(Matricula)
admin.site.register(Calificacion)
admin.site.register(EquivalentesTipoEvaluacion)
admin.site.register(subpromedioTipoEvaluacion)

admin.site.register(Asistencia)





