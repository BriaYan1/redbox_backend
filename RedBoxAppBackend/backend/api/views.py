from rest_framework import viewsets
from backend.models import *
from backend.api.serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated



""""La clase viewset es una clase que proporciona una implementación completa de las operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para un modelo específico. Al definir un viewset, puedes especificar el queryset (conjunto de datos) y el serializer (serializador) que se utilizará para convertir los datos a formatos como JSON o XML."""

@api_view(['POST'])
def login(request):
    email = request.data.get('email_usuario')
    password = request.data.get('contrasena_usuario')

    if not email or not password:
        return Response({'error': 'email_usuario y contrasena_usuario son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, email=email)

    if not user.check_password(password):
        return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)

    try:
        usuario = Usuarios.objects.get(user=user)
        usuario_data = UsuariosSerializer(usuario).data
    except Usuarios.DoesNotExist:
        usuario_data = {'username': user.username, 'email': user.email}

    return Response({'token': token.key, 'user': usuario_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def registro(request):
    serializer = UsuarioRegistroSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        token = Token.objects.create(user=usuario.user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil(request):
    
    print(request.user)
    return Response("Estas logueado como: {} " .format(request.user.username), status=status.HTTP_200_OK)

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
    

    