from rest_framework import routers
from backend.api import views
from django.urls import path, re_path

router = routers.DefaultRouter()
router.register('patologias', views.PatologiasViewSet, basename='patologias')
router.register('roles', views.RolesViewSet, basename='roles')
router.register('usuarios', views.UsuariosViewSet, basename='usuarios')
router.register('usuario_roles', views.Usuario_rolesViewSet, basename='usuario_roles')
router.register('biometria', views.BiometriaViewSet, basename='biometria')
router.register('planes', views.PlanesViewSet, basename='planes')
router.register('usuario_planes', views.Usuario_planesViewSet, basename='usuario_planes')
router.register('accesos', views.AccesosViewSet, basename='accesos')
router.register('pagos', views.PagosViewSet, basename='pagos')
router.register('usuario_patologias', views.Usuario_patologiasViewSet, basename='usuario_patologias')
router.register('clases', views.ClasesViewSet, basename='clases')
router.register('planificacion_diaria', views.Planificacion_diariaViewSet, basename='planificacion_diaria')
router.register('resultados', views.ResultadosViewSet, basename='resultados')

urlpatterns = router.urls
urlpatterns += [
    re_path('login/', views.login, name='login'),
    re_path('registro/', views.registro, name='registro'), 
    re_path('perfil/', views.perfil, name='perfil'),
]

