from rest_framework import routers
from backend.api import views
from django.urls import path, re_path, include

# import del endpoint de verificacion biometrica
from backend.views_biometrico import verificar_acceso

# 1. Configuración del Router
router = routers.DefaultRouter()
router.register(r'patologias', views.PatologiasViewSet, basename='patologias')
router.register(r'roles', views.RolesViewSet, basename='roles')
router.register(r'usuarios', views.UsuariosViewSet, basename='usuarios')
router.register(r'usuario_roles', views.Usuario_rolesViewSet, basename='usuario_roles')
router.register(r'biometria', views.BiometriaViewSet, basename='biometria')
router.register(r'planes', views.PlanesViewSet, basename='planes')
router.register(r'usuario_planes', views.Usuario_planesViewSet, basename='usuario_planes')
router.register(r'accesos', views.AccesosViewSet, basename='accesos')
router.register(r'pagos', views.PagosViewSet, basename='pagos')
router.register(r'usuario_patologias', views.Usuario_patologiasViewSet, basename='usuario_patologias')
router.register(r'clases', views.ClasesViewSet, basename='clases') # ✅ Esto habilita GET y POST
router.register(r'planificacion_diaria', views.Planificacion_diariaViewSet, basename='planificacion_diaria')
router.register(r'resultados', views.ResultadosViewSet, basename='resultados')
router.register(r'movimientos', views.MovimientosViewSet, basename='movimientos')


urlpatterns = [
    
    path('', include(router.urls)),
    
    # 3. Rutas personalizadas con re_path
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^registro/$', views.registro, name='registro'), 
    re_path(r'^perfil/$', views.perfil, name='perfil'),
    path('generar_invitacion/', views.generar_invitacion, name='generar_invitacion'),
    path('listar_invitaciones/', views.listar_invitaciones, name='listar_invitaciones'),
    # path('verificar_invitacion/', views.verificar_invitacion, name='verificar_invitacion'),
    path('registrar_pago/', views.registrar_pago, name='registrar_pago'),
    path('suscripcion/<int:id_usuario>/', views.suscripcion_usuario, name='suscripcion_usuario'),
    path('historial_pagos/', views.historial_pagos, name='historial_pagos'),
    path('perfil/<int:id_usuario>/', views.perfil_usuario, name='perfil_usuario'),
    path('editar_mi_perfil/', views.editar_mi_perfil, name='editar_mi_perfil'),
    path('mejores_resultados/<int:id_usuario>/<int:id_movimiento>/', views.mejores_resultados, name='mejores_resultados'),
    path('usuarios_con_roles/', views.listar_usuarios_con_roles, name='listar_usuarios_con_roles'),
    path('asignar_rol/<int:id_usuario>/', views.asignar_rol, name='asignar_rol'),
    path('mis_clases_con_alumnos/', views.mis_clases_con_alumnos, name='mis_clases_con_alumnos'),
    path('entrenadores/', views.obtener_entrenadores, name='entrenadores'),
    path('horarios_entrenador/<int:id_entrenador>/', views.obtener_horarios_entrenador, name='horarios_entrenador'),
    path('asignar_horarios/', views.asignar_horarios, name='asignar_horarios'),
    path('eliminar_horario/<int:id_horario>/', views.eliminar_horario, name='eliminar_horario'),
    path('obtener_entrenador_por_horario/', views.obtener_entrenador_por_horario, name='obtener_entrenador_por_horario'),
    path('solicitar_recuperacion/', views.solicitar_recuperacion, name='solicitar_recuperacion'),
    path('verificar_codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('restablecer_password/', views.restablecer_password, name='restablecer_password'),
        # endpoint que usa el ESP32 para verificar acceso biometrico
    path('biometrico/verificar/', verificar_acceso, name='verificar_acceso'),
]
