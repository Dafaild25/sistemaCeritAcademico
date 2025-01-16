from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from Aplicaciones.Login.views.Variables_Globales_views import obtenerEscuela, registrarEscuela



from .views.Calificacion_General_Admin_views import guardarExamenSupletorioAdmin, obtenerCalificacionSupletorioAdmin, obtenerMatriculasParaSupletorioAdmin, obtenerPromediosGeneralesAdmin, obtenerPromediosGeneralesTrimestralesAdmin, vistaCalificacionGeneralAdmin
from .views.login_views import logueo,cerrarSesion,registro
from .views.Periodo_views import vistaPeriodo,crearPeriodo,listarPeriodo,selecionarUnPeriodo,editarUnPeriodo,eliminarUnPeriodo
from .views.Division_views import listarTrimestres,crearTrimestre,selecionarUnTrimestre,editarUnTrimestre,eliminarUnTrimestre
from .views.TipoEvaluacion_views import listarTiposEvaluacion,crearTipoEvaluacion,selecionarUnTipoEvaluacion,editarUnTipoEvaluacion,eliminarUnTipoEvaluacion
from .views.Curso_views import listarCursos,crearCurso,selecionarUnCurso,editarUnCurso,eliminarUnCurso
from .views.Docente_views import registroDocente,listadoDocentes,obtenerDocente,actualizarDocente,eliminarDocente,registroDocente,EstudiantesPorCurso
from .views.Admin_views import adminHome,registroAdmin,listadoAdministrador,eliminarAdministrador,obtenerAdministrador,actualizarAdministrador
from .views.Estudiante_views import estudianteHome,registroEstudiante,listadoEstudiantes,eliminarEstudiante,editarEstudiante,obtenerEstudiante,actualizarEstudiante
from .views.Curso_views import listarCursos,crearCurso,selecionarUnCurso,editarUnCurso,eliminarUnCurso
from .views.Matricula_views import adminCurso,listarPeriodosAcademicos,listarCursosPeriodo,listarEstudiantes,actualizarDatosEstudiante,datosEstudiantes,eliminarMatricula,matriculaIndividual,obtener_matricula,actualizar_matricula,cargarEstudiantes_MatriculaIndividual
from .views.login_views import logueo,cerrarSesion,enviar_codigo,cambiar_contra,verificacion_codigo,buscar_usuario
from .views.Asignatura_views import asignatura,guardar_asignatura,guardarAsignatura,listar_asignaturas,obtenerAsignatura,eliminarAsignatura,actualizarAsignatura,listarCursosClase,listarAsignaturasClase,listarDocentesClase,guardarCursoAsignatura,listarCursosAsignatura,eliminarCursoAsigantura,vistaClases
from.views.Reportes_views import reportes,listarCursosReportes,listar_estudiantes,listarPeriodosAcademicosReportes,listarTrimestresReportes,vistaTrimestresReportes,reportesTrimestrales,crearAporteAdmin,selecionarUnAporteAdmin,editarAporteAdmin,eliminarAporteAdmin,calificacionAporteTrimestralAdmin
from.views.Dashboard_views import obtener_datos_graficos,obtener_tipos_evaluacion
# lo que va hacer el docente 
from .views.Aporte_Docente_views import docenteHome,listarPeriodosDocente,listarCursosDocente,listarTrimestresTipo,listartiposPorTrimestre,crearAporteDocente,selecionarUnAporte,editarAporte,eliminarAporte

from.views.Calificacion_Clase_views import vistaTrabajoClase,claseTrabajo,reporteTrimestral,calificacionAporteTrimestral,obtenerObservacion,editarObservacion,obtenerCalificaciones,obtenerEquivalentesTipos, obtenerSubpromediosTipos


from .views.Importaciones_views import importar_docentes,importarEstudiantes,importar_clases,importar_asignaturas
from .views.Asistencias_Docente_views import listar_asistencias,obtener_trimestres,vistaAsistencias,registrar_asistencia,obtener_asistencia,obtener_asistencias_por_mes,resumen_asistencias,generar_pdf_asistencias,obtener_dias_estado,generar_pdf_asistencias_trimestre

from .views.Examen_Trimestral_views import listarExamenesTrimestrales,selecionarExamenTrimestral,editarUnExamenTrimestral,crearExamenTrimestral,eliminarUnExamenTrimestral
from .views.Unidad_Trimestral_views import listarUnidadesTrimestrales,selecionarUnidadTrimestral,editarUnidadTrimestral,crearUnidadTrimestral,eliminarUnidadTrimestral
from .views.Examen_Final_views import listarExamenFinal,selecionarExamenFinal,editarUnExamenFinal,crearExamenFinal,eliminarUnExamenFinal
from .views.Calificacion_Unidad_views import vistaCalificacionUnidad
from .views.Calificacion_Trimestre_views import editarObservacionExamen, obtenerObservacionExamen, vistaCalificacionTrimestre,obtenerSubPromedioUnidad,calificacionExamenTrimestral,obtenerCalificacionExamenTrimestral,obtenerPromedioTrimestral
from .views.Reporte_Unidad_views import vistaReporteUnidad
from .views.Calificacion_Unidad_Admin_views import obtenerCalificacionesUnidadAdmin,obtenerObservacionUnidadAdmin,editarObservacionUnidadAdmin
from .views.Calificacion_Trimestre_Admin_views import editarObservacionExamenAdmin, vistaCalificacionTrimestreAdmin,obtenerSubPromedioUnidadAdmin,calificacionExamenTrimestralAdmin,obtenerCalificacionExamenTrimestralAdmin,obtenerPromedioTrimestralAdmin,obtenerObservacionExamenAdmin
from .views.Estudiante_Reporte_views import calcularPromedioTrimestralEstudiante, listarPeriodosEstudiantes,listarTrimestresEstudiantes,listarCalificacionesPorPeriodo,listarCalificacionesPorTrimestre, reportePeriodicalEstudiante, reporteTrimestralEstudiante
from .views.Calificacion_General_views import calcularPromedioClaseGeneral, guardarExamenSupletorio, obtenerCalificacionSupletorio, obtenerMatriculasParaSupletorio, obtenerPromediosGeneralesTrimestrales, vistaCalificacionGeneral,obtenerPromediosGenerales
from .views.Variables_Globales_views import vistaVariablesGlobales,listarPeriodoParaVariables


urlpatterns = [

    #URLS LOGIN
    path('', logueo, name='logueo'), 
    path('registro/',registro, name='registro'),
    path('login/',logueo, name='login'),    
    path('cerrarSesion/', cerrarSesion, name='cerrarSesion'),  # Nueva URL para cerrar sesión
    path('enviar_codigo/', enviar_codigo, name='enviar_codigo'),
    path('verificacion_codigo/', verificacion_codigo, name='verificacion_codigo'),
    path('cambiar_contra/', cambiar_contra, name='cambiar_contra'),
    path('buscar_usuario/', buscar_usuario, name='buscar_usuario'),

    #URLS LOGINADMIN
    path('adminHome/', adminHome, name='adminHome'),
    path('registroAdmin/', registroAdmin, name='registroAdmin'),
    path('listadoAdministrador/', listadoAdministrador, name='listadoAdministrador'),
    path('eliminarAdministrador/<int:id>/',eliminarAdministrador,name='eliminarAdministrador'),
    path('obtenerAdministrador/<int:id>/', obtenerAdministrador, name='obtenerAdministrador'),
    path('actualizarAdministrador/<int:id>/', actualizarAdministrador, name='actualizarAdministrador'),

    #CRUD DE PERIODOS ACADEMICOS
    path('vistaPeriodo', vistaPeriodo, name='vistaPeriodo'),
    path('crearPeriodo',crearPeriodo,name='crearPeriodo'),
    path("listarPeriodo", listarPeriodo, name="listarPeriodo"),
    path("selecionarUnPeriodo/<int:id>/",selecionarUnPeriodo, name="selecionarUnPeriodo"),
    path("editarUnPeriodo/<int:id>/",editarUnPeriodo, name="editarUnPeriodo"),
    path('eliminarUnPeriodo/<int:id>/',eliminarUnPeriodo,name="eliminarUnPeriodo"),
    #CRUD DE TRIMESTRES
    path('listarTrimestres/<int:periodo_id>/',listarTrimestres, name="listarTrimestres"),
    path('crearTrimestre',crearTrimestre,name="crearTrimestre"),
    path("selecionarUnTrimestre/<int:id>/",selecionarUnTrimestre, name="selecionarUnTrimestre"),
    path("editarUnTrimestre/<int:id>/",editarUnTrimestre, name="editarUnTrimestre"),
    path('eliminarUnTrimestre/<int:id>/',eliminarUnTrimestre,name="eliminarUnTrimestre"),
    
    #CRUD DE TIPOS DE EVALUACION
    #el admin logueado una ves creado el periodo y trimestes estos podran crear sus tipos de evaluacion
    path('listarTiposEvaluacion/<int:periodo_id>/',listarTiposEvaluacion,name='listarTiposEvaluacion'),
    path('crearTipoEvaluacion',crearTipoEvaluacion,name='crearTipoEvaluacion'),
    path('selecionarUnTipoEvaluacion/<int:id>/',selecionarUnTipoEvaluacion,name='selecionarUnTipoEvaluacion'),
    path('editarUnTipoEvaluacion/<int:id>/',editarUnTipoEvaluacion,name='editarUnTipoEvaluacion'),
    path('eliminarUnTipoEvaluacion/<int:id>/',eliminarUnTipoEvaluacion,name='eliminarUnTipoEvaluacion'),
    
    
    #CRUD EXMAMENES TRIMESTRALES
    path('listarExamenesTrimestrales/<int:periodo_id>/',listarExamenesTrimestrales,name='listarExamenesTrimestrales'),
    path('selecionarExamenTrimestral/<int:id>/', selecionarExamenTrimestral, name='selecionarExamenTrimestral'),
    path('editarUnExamenTrimestral/<int:id>/',editarUnExamenTrimestral,name='editarUnExamenTrimestral'),
    path('crearExamenTrimestral',crearExamenTrimestral,name='crearExamenTrimestral'),
    path('eliminarUnExamenTrimestral/<int:id>/',eliminarUnExamenTrimestral,name='eliminarUnExamenTrimestral'),
    
    # CRUD EXAMENES FINALES
    path('listarExamenFinal/<int:id>/',listarExamenFinal,name='listarExamenFinal'),
    path('selecionarExamenFinal/<int:id>/',selecionarExamenFinal,name='selecionarExamenFinal'),
    path('editarUnExamenFinal/<int:id>/',editarUnExamenFinal,name='editarUnExamenFinal'),
    path('crearExamenFinal/<int:periodo_id>/',crearExamenFinal,name='crearExamenFinal'),
    path('eliminarUnExamenFinal/<int:id>/',eliminarUnExamenFinal,name='eliminarUnExamenFinal'),
    
    #CRUD UNIDADES TRIMESTRALES
    path('listarUnidadesTrimestrales/<int:periodo_id>/',listarUnidadesTrimestrales,name='listarUnidadesTrimestrales'),
    path('selecionarUnidadTrimestral/<int:id>/',selecionarUnidadTrimestral,name='selecionarUnidadTrimestral'),
    path('editarUnidadTrimestral/<int:id>/',editarUnidadTrimestral,name='editarUnidadTrimestral'),
    path('crearUnidadTrimestral',crearUnidadTrimestral,name='crearUnidadTrimestral'),
    path('eliminarUnidadTrimestral/<int:id>/', eliminarUnidadTrimestral, name='eliminarUnidadTrimestral'),
    # Otras rutas...
    
    # VISTA DE CALIFICACIONES  DE CADA UNIDAD
    path('vistaCalificacionUnidad/<int:unidad_id>/<int:clase_id>/',vistaCalificacionUnidad,name='vistaCalificacionUnidad'),
    
    #VISTA DE CALIFICACIONES DE CADA TRIMESTRE
    path("vistaCalificacionTrimestre/<int:trimestre_id>/<int:clase_id>/",vistaCalificacionTrimestre, name="vistaCalificacionTrimestre"),
    path("obtenerSubPromedioUnidad/<int:unidad_id>/<int:matricula_id>/<int:trimestre_id>/<int:clase_id>/",obtenerSubPromedioUnidad,name="obtenerSubPromedioUnidad"),
    path('calificacionExamenTrimestral/',calificacionExamenTrimestral,name='calificacionExamenTrimestral'),
    path('obtenerCalificacionExamenTrimestral/<int:matricula_id>/<int:examen_id>/<int:clase_id>/',obtenerCalificacionExamenTrimestral, name='obtenerCalificacionExamenTrimestral'),
    path('obtenerPromedioTrimestral/<int:matricula_id>/<int:trimestre_id>/<int:clase_id>/', obtenerPromedioTrimestral, name='obtenerPromedioTrimestral'),
    
    # VISTA CALIFICACION  GENERAL DE DOCENTE
    path('vistaCalificacionGeneral/<int:periodo_id>/<int:clase_id>/',vistaCalificacionGeneral,name='vistaCalificacionGeneral'),
    path('obtenerPromediosGeneralesTrimestrales/<int:matricula_id>/<int:trimestre_id>/<int:clase_id>/<int:periodo_id>/',obtenerPromediosGeneralesTrimestrales,name='obtenerPromediosGeneralesTrimestrales'),
    path('obtenerPromediosGenerales/<int:matricula_id>/<int:clase_id>/<int:periodo_id>/',obtenerPromediosGenerales,name='obtenerPromediosGenerales'),
    path('calcularPromedioClaseGeneral/<int:clase_id>/',calcularPromedioClaseGeneral,name='calcularPromedioClaseGeneral'),
    
    #CRUD CURSO
    path('listarCursos/<int:periodo_id>/',listarCursos,name='listarCursos'),
    path('crearCurso',crearCurso,name='crearCurso'),
    path('selecionarUnCurso/<int:id>/',selecionarUnCurso,name='selecionarUnCurso'),
    path('editarUnCurso/<int:id>/',editarUnCurso,name='editarUnCurso'),
    path('eliminarUnCurso/<int:id>/',eliminarUnCurso,name='eliminarUnCurso'),


    # URLS DE  MATRICULA
    path('adminCurso/',adminCurso, name='adminCurso'),
    path("listarPeriodosAcademicos/", listarPeriodosAcademicos, name="listarPeriodosAcademicos"),
    path('listarCursosPeriodo/<int:periodo_id>/',listarCursosPeriodo,name='listarCursosPeriodo'),
    path('listarEstudiantes/',listarEstudiantes,name='listarEstudiantes'),
    path('importarEstudiantes/', importarEstudiantes, name='importarEstudiantes'),
    path('actualizarDatosEstudiante/<int:id>/', actualizarDatosEstudiante, name='actualizarDatosEstudiante'),
    path('datosEstudiantes/', datosEstudiantes, name='datosEstudiantes'),
    path('eliminarMatricula/<int:id>/', eliminarMatricula, name='eliminarMatricula'),
    path('matriculaIndividual/', matriculaIndividual, name='matriculaIndividual'),
    path('obtener_matricula/', obtener_matricula, name='obtener_matricula'),
    path('actualizar_matricula/', actualizar_matricula, name='actualizar_matricula'),
     path('cargar_estudiantes/', cargarEstudiantes_MatriculaIndividual, name='cargar_estudiantes'),
    
    

    #URLS LOGINDOCENTE
    path('registroDocente/', registroDocente, name='registroDocente'),
  
    path('listadoDocentes/', listadoDocentes, name='listadoDocentes'),
    path('obtenerDocente/<int:id>/', obtenerDocente, name='obtenerDocente'),
    path('actualizarDocente/<int:id>/', actualizarDocente, name='actualizarDocente'),
    path('eliminarDocente/<int:id>/',eliminarDocente,name='eliminarDocente'),
    path('importar_docentes/', importar_docentes, name='importar_docentes'),

    #URLS LOGINESTUDIANTE
    path('registroEstudiante/', registroEstudiante, name='registroEstudiante'),
    path('estudianteHome/', estudianteHome, name='estudianteHome'),
    path('listadoEstudiantes/', listadoEstudiantes, name='listadoEstudiantes'),
    path('eliminarEstudiante/<int:id>/',eliminarEstudiante,name='eliminarEstudiante'),
    path('editarEstudiante/', editarEstudiante, name='editarEstudiante'),
    path('obtenerEstudiante/<int:id>/', obtenerEstudiante, name='obtenerEstudiante'),
    path('actualizarEstudiante/<int:id>/', actualizarEstudiante, name='actualizarEstudiante'),


    
    # URLS DE DOCENTE LOGUEADO
    #path('CursosAsignaturaDocente/<int:periodo_id>/',CursosAsignaturaDocente,name='CursosAsignaturaDocente'),
    path('EstudiantesPorCurso/<int:curso_id>/', EstudiantesPorCurso, name='EstudiantesPorCurso'),




    # URLS DE ASIGNATURA
    path('asignatura/',asignatura, name='asignatura'),
    path('guardar_asignatura/', guardar_asignatura, name='guardar_asignatura'),
    path('guardarAsignatura',guardarAsignatura,name='guardarAsignatura'),
    path('listar_asignaturas/', listar_asignaturas, name='listar_asignaturas'),
    path('obtenerAsignatura/<int:id>/', obtenerAsignatura, name='obtenerAsignatura'),
    path('actualizarAsignatura/<int:id>/', actualizarAsignatura, name='actualizarAsignatura'),
    path('eliminarAsignatura/<id>/',eliminarAsignatura,name='eliminarAsignatura'),
    path('importar-clases/', importar_clases, name='importar_clases'),
    path('importar-asignaturas/', importar_asignaturas, name='importar_asignaturas'),
    #aqui estan los links para crear clases
    
   
    
    path("listarCursosClase/<int:periodo_id>/",listarCursosClase, name="listarCursosClase"),
    path('listarAsignaturasClase',listarAsignaturasClase, name='listarAsignaturasClase'),
    path('listarDocentesClase',listarDocentesClase, name='listarDocentesClase'),
    path('guardarCursoAsignatura',guardarCursoAsignatura,name='guardarCursoAsignatura'),
    #  quiero ver primero renderizar 
    path('vistaClases',vistaClases,name='vistaClases'),
    
    
    path('listarCursosAsignatura/<int:periodo_id>/',listarCursosAsignatura, name='listarCursosAsigantura'),
    path('eliminarCursoAsigantura/<int:id>/',eliminarCursoAsigantura,name='eliminarCursoAsigantura'),
    
    
    # Cuando el docente esta logueado 
    path('docenteHome/', docenteHome, name='docenteHome'),
    path('listarPeriodosDocente',listarPeriodosDocente,name='listarPeriodosDocente'),
    path('listarCursosDocente/<int:periodo_id>/',listarCursosDocente,name='listarCursosDocente'),
    path('listarTrimestresTipo/<int:periodo_id>/',listarTrimestresTipo,name='listarTrimestresTipo'),
    path('listartiposPorTrimestre/<int:trimestre_id>/',listartiposPorTrimestre,name='listartiposPorTrimestre'),
    path('crearAporteDocente',crearAporteDocente,name='crearAporteDocente'),
    path('selecionarUnAporte/<int:aporte_id>/',selecionarUnAporte,name='selecionarUnAporte'),
    path('editarAporte/<int:id>/',editarAporte,name='editarAporte'),
    path('eliminarAporte/<int:id>/',eliminarAporte,name='eliminarAporte'),
    path('calificacionAporteTrimestral/',calificacionAporteTrimestral,name='calificacionAporteTrimestral'),

    # Cuando el docente esta logueado asistencias
    path('listar_asistencias/<int:trimestre_id>/<int:clase_id>/', listar_asistencias, name='listar_asistencias'),

    path('obtener_trimestres/<int:periodo_id>/', obtener_trimestres, name='obtener_trimestres'),
    path('vistaAsistencias/<int:clase_id>/',vistaAsistencias,name='vistaAsistencias'),
    path('registrar_asistencia/', registrar_asistencia, name='registrar_asistencia'),
    path('obtener_asistencia/<str:fecha>/', obtener_asistencia, name='obtener_asistencia'),
    path('obtener_asistencias_por_mes/<int:clase_id>/<int:trimestre_id>/<str:fecha_mes>/', obtener_asistencias_por_mes, name='obtener_asistencias_por_mes'),
    path('resumen_asistencias/<int:clase_id>/', resumen_asistencias, name='resumen_asistencias'),
    path('generar_pdf_asistencias/<int:clase_id>/', generar_pdf_asistencias, name='generar_pdf_asistencias'),
    path('obtener_dias_estado/<str:estado>/<int:matricula_id>/<int:trimestre_id>/',obtener_dias_estado, name='obtener_dias_estado' ),
    path('generar_pdf_asistencias_trimestre/<int:clase_id>/<int:trimestre_id>/', generar_pdf_asistencias_trimestre, name='generar_pdf_asistencias_trimestre'),

    
    

    
    # forma 2 para ingresar calificaciones
    path('vistaTrabajoClase/<int:clase_id>/',vistaTrabajoClase,name='vistaTrabajoClase'),
    path('claseTrabajo/<int:trimestre_id>/<int:clase_id>/',claseTrabajo,name='claseTrabajo'),
    path('reporteTrimestral/<int:trimestre_id>/<int:clase_id>/',reporteTrimestral,name='reporteTrimestral'),

    #path('calificacionClase/<int:clase_id>/',calificacionClase,name='calificacionClase'),
    # FORMA PARA OBTENER CALIFICACONES EN DOCENTE 
    path("obtenerCalificaciones/<int:matricula_id>/<int:aporte_id>/<int:calificacion_id>/",obtenerCalificaciones, name="obtenerCalificaciones"),
    # forma para obtener promedios en el modulo de  docentes 
    path("obtenerEquivalentesTipos/<int:tipo_id>/<int:matricula_id>/<int:trimestre_id>/",obtenerEquivalentesTipos, name='obtenerEquivalentesTipos'),
    
    path('obtenerSubpromediosTipos/<int:tipo_id>/<int:matricula_id>/<int:trimestre_id>/', obtenerSubpromediosTipos, name=' obtenerSubpromediosTipos'),
    
    
   




    #URLS DE REPORTES
    path('reportes/',reportes, name='reportes'),
    path('listarCursosReportes/<int:periodo_id>/',listarCursosReportes, name='listarCursosReportes'),
    path('listarEstudiantes/<int:curso_id>/', listar_estudiantes, name='listar_estudiantes'),
    path('listarPeriodosAcademicosReportes/',listarPeriodosAcademicosReportes,name='listarPeriodosAcademicosReportes'),
    path('listarTrimestresReportes/<int:periodo_id>/',listarTrimestresReportes,name='listarTrimestresReportes'),
    path('vistaTrimestresReportes/<int:clase_id>/',vistaTrimestresReportes,name='vistaTrimestresReportes'),
    path('reportesTrimestrales/<int:trimestre_id>/<int:clase_id>/', reportesTrimestrales, name='reportesTrimestrales'),
    path('crearAporteAdmin',crearAporteAdmin, name ='crearAporteAdmin'),
    path('selecionarUnAporteAdmin/<int:aporte_id>/',selecionarUnAporteAdmin, name='selecionarUnAporteAdmin'),
    path('editarAporteAdmin/<int:id>/',editarAporteAdmin, name='editarAporteAdmin'),
    path('eliminarAporteAdmin/<int:id>/', eliminarAporteAdmin, name="eliminarAporteAdmin"),
    path('calificacionAporteTrimestralAdmin/',calificacionAporteTrimestralAdmin, name='calificacionAporteTrimestralAdmin'),
    path('vistaCalificacionGeneralAdmin/<int:periodo_id>/<int:clase_id>/',vistaCalificacionGeneralAdmin,name='vistaCalificacionGeneralAdmin'),
    path('obtenerPromediosGeneralesTrimestralesAdmin/<int:matricula_id>/<int:trimestre_id>/<int:clase_id>/<int:periodo_id>/',obtenerPromediosGeneralesTrimestralesAdmin,name='obtenerPromediosGeneralesTrimestralesAdmin'),
    path('obtenerPromediosGeneralesAdmin/<int:matricula_id>/<int:clase_id>/<int:periodo_id>/',obtenerPromediosGeneralesAdmin,name='obtenerPromediosGeneralesAdmin'),
    path('calcularPromedioClaseGeneralAdmin/<int:clase_id>/',calcularPromedioClaseGeneral,name='calcularPromedioClaseGeneral'),
    
    # urls para el reporte de una unidad esto netamente es el admin
    path('vistaReporteUnidad/<int:unidad_id>/<int:clase_id>/',vistaReporteUnidad,name='vistaReporteUnidad'),
    path('obtenerCalificacionesUnidadAdmin/<int:matricula_id>/<int:aporte_id>/<int:calificacion_id>/',obtenerCalificacionesUnidadAdmin,name='obtenerCalificacionesUnidadAdmin'),
    path('obtenerObservacionUnidadAdmin/<int:calificacion_id>/',obtenerObservacionUnidadAdmin,name='obtenerObservacionUnidadAdmin'),
    path('editarObservacionUnidadAdmin/<int:calificacion_id>/',editarObservacionUnidadAdmin,name='editarObservacionUnidadAdmin'),


    # urls para ver contenido de trimestre para el admin
    path('vistaCalificacionTrimestreAdmin/<int:trimestre_id>/<int:clase_id>/',vistaCalificacionTrimestreAdmin,name='vistaCalificacionTrimestreAdmin'),
    path('obtenerSubPromedioUnidadAdmin/<int:unidad_id>/<int:matricula_id>/<int:trimestre_id>/<int:clase_id>/',obtenerSubPromedioUnidadAdmin,name='obtenerSubPromedioUnidadAdmin'),
    path('calificacionExamenTrimestralAdmin/',calificacionExamenTrimestralAdmin,name='calificacionExamenTrimestralAdmin'),
    path('obtenerCalificacionExamenTrimestralAdmin/<int:matricula_id>/<int:examen_id>/<int:clase_id>/',obtenerCalificacionExamenTrimestralAdmin,name='obtenerCalificacionExamenTrimestralAdmin'),
    path('obtenerPromedioTrimestralAdmin/<int:matricula_id>/<int:trimestre_id>/<int:clase_id>/',obtenerPromedioTrimestralAdmin,name='obtenerPromedioTrimestralAdmin'),
    path('obtenerObservacionExamenAdmin/<int:calificacion_id>/',obtenerObservacionExamenAdmin,name='obtenerObservacionExamenAdmin'),
    path('editarObservacionExamenAdmin/<int:calificacion_id>/',editarObservacionExamenAdmin,name='editarObservacionExamenAdmin'),
    #URLS DASHBOARD
    path('datos-graficos/', obtener_datos_graficos, name='datos_graficos'),
    path('obtener_tipos_evaluacion/<int:curso_asignatura_id>/<int:trimestre>/', obtener_tipos_evaluacion, name='obtener_tipos_evaluacion'),

    
    # para obteer una observacion para los docentes 
    path('obtenerObservacion/<int:calificacion_id>/',obtenerObservacion,name='obtenerObservacion'),
    path('editarObservacion/<int:calificacion_id>/',editarObservacion,name='editarObservacion'),
    path('obtenerObservacionExamen/<int:calificacion_id>/',obtenerObservacionExamen,name='obtenerObservacionExamen'),
    path('editarObservacionExamen/<int:calificacion_id>/',editarObservacionExamen,name='editarObservacionExamen'),
    
    
    #url de reportes para que vea el representante
    path('listarPeriodosEstudiantes',listarPeriodosEstudiantes,name='listarPeriodosEstudiantes'),
    path('listarTrimestresEstudiantes/<int:periodo_id>/',listarTrimestresEstudiantes,name='listarTrimestresEstudiantes'),
    path('listarCalificacionesPorPeriodo/<int:periodo_id>/',listarCalificacionesPorPeriodo,name='listarCalificacionesPorPeriodo'),
    path('listarCalificacionesPorTrimestre/<int:periodo_id>/<int:trimestre_id>/',listarCalificacionesPorTrimestre,name='listarCalificacionesPorTrimestre'),

    path('calcularPromedioTrimestralEstudiante/<int:matricula_id>/<int:trimestre_id>/',calcularPromedioTrimestralEstudiante,name='calcularPromedioTrimestralEstudiante'),
    path('reportePeriodicalEstudiante/<int:periodo_id>/', reportePeriodicalEstudiante, name='reportePeriodicalEstudiante'),
    path('reporteTrimestralEstudiante/<int:periodo_id>/<int:trimestre_id>/', reporteTrimestralEstudiante, name='reporteTrimestralEstudiante'), 
   
#    Supletorio
    path('obtenerMatriculasParaSupletorio/<int:clase_id>/<int:matricula_id>/', obtenerMatriculasParaSupletorio, name='obtenerMatriculasParaSupletorio'),
    path('guardarExamenSupletorio/',guardarExamenSupletorio,name='guardarExamenSupletorio'),
    path('obtenerCalificacionSupletorio/<int:examen_id>/<int:matricula_id>/<int:clase_id>/',obtenerCalificacionSupletorio,name='obtenerCalificacionSupletorio'),
    
    # Supletorio modo admin
    path('obtenerMatriculasParaSupletorioAdmin/<int:clase_id>/<int:matricula_id>/', obtenerMatriculasParaSupletorioAdmin, name='obtenerMatriculasParaSupletorioAdmin'),
    path('guardarExamenSupletorioAdmin/',guardarExamenSupletorioAdmin,name='guardarExamenSupletorioAdmin'),
    path('obtenerCalificacionSupletorioAdmin/<int:examen_id>/<int:matricula_id>/<int:clase_id>/',obtenerCalificacionSupletorioAdmin,name='obtenerCalificacionSupletorioAdmin'),
    
    #variables globales  del admin 
    path('vistaVariablesGlobales/',vistaVariablesGlobales,name='vistaVariablesGlobales'),
    path('listarPeriodoParaVariables/',listarPeriodoParaVariables,name='listarPeriodoParaVariables'),
    path('vistaVariablesGlobales/registrarEscuela/',registrarEscuela,name='registrarEscuela'),
    path('vistaVariablesGlobales/obtenerEscuela/',obtenerEscuela,name='obtenerEscuela'),
   
    
]


