from rest_framework import routers
from backend.api import views
from django.urls import path, re_path, include

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

# 2. Definición de urlpatterns
urlpatterns = [
    # Incluimos todas las rutas del router automáticamente
    path('', include(router.urls)),
    
    # 3. Rutas personalizadas con re_path
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^registro/$', views.registro, name='registro'), 
    re_path(r'^perfil/$', views.perfil, name='perfil'),
]
