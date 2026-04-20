from rest_framework import viewsets
from backend.models import *
from backend.api.serializers import *

""""La clase viewset es una clase que proporciona una implementación completa de las operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para un modelo específico. Al definir un viewset, puedes especificar el queryset (conjunto de datos) y el serializer (serializador) que se utilizará para convertir los datos a formatos como JSON o XML."""

class PatologiasViewSet(viewsets.ModelViewSet):
    queryset = Patologias.objects.all()
    serializer_class = PatologiasSerializer

class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    
class Usuario_rolesViewSet(viewsets.ModelViewSet):
    queryset = Usuario_roles.objects.all()
    serializer_class = Usuario_rolesSerializer
    
class BiometriaViewSet(viewsets.ModelViewSet):
    queryset = Biometria.objects.all()
    serializer_class = BiometriaSerializer
    
class PlanesViewSet(viewsets.ModelViewSet):
    queryset = Planes.objects.all()
    serializer_class = PlanesSerializer
    
class Usuario_planesViewSet(viewsets.ModelViewSet):
    queryset = Usuario_planes.objects.all()
    serializer_class = Usuario_planesSerializer 
    
class AccesosViewSet(viewsets.ModelViewSet):
    queryset = Accesos.objects.all()
    serializer_class = AccesosSerializer
    
class PagosViewSet(viewsets.ModelViewSet):
    queryset = Pagos.objects.all()
    serializer_class = PagosSerializer
    
class Usuario_patologiasViewSet(viewsets.ModelViewSet):
    queryset = Usuario_patologias.objects.all()
    serializer_class = Usuario_patologiasSerializer
    
class ClasesViewSet(viewsets.ModelViewSet):
    queryset = Clases.objects.all()
    serializer_class = ClasesSerializer
    
class Planificacion_diariaViewSet(viewsets.ModelViewSet):
    queryset = Planificacion_diaria.objects.all()
    serializer_class = Planificacion_diariaSerializer
    
class ResultadosViewSet(viewsets.ModelViewSet):
    queryset = Resultados.objects.all()
    serializer_class = ResultadosSerializer
    

    