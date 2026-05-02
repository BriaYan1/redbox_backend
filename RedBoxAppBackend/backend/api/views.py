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
from rest_framework.response import Response
from datetime import time

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
        # Usamos get_or_create por si el token ya existía
        token, created = Token.objects.get_or_create(user=usuario.user)
        
        return Response({
            'token': token.key,
            'user_id': usuario.id_usuario, # Usamos el ID de tu modelo Usuarios
            'email': usuario.email_usuario
        }, status=status.HTTP_201_CREATED)

    # ESTO ES LO QUE DEBES REVISAR EN TU TERMINAL
    print("ERRORES DE VALIDACIÓN:", serializer.errors)
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

    def get_queryset(self):
        queryset = Clases.objects.all()
        id_usuario = self.request.query_params.get('id_usuario')
        if id_usuario is not None:
            queryset = queryset.filter(id_usuario=id_usuario)
        return queryset

    def create(self, request, *args, **kwargs):
        print("DATOS RECIBIDOS:", request.data) # Esto saldrá en tu terminal de VS Code
        
        id_user_recibido = request.data.get('id_usuario')
        fecha = request.data.get('fecha_clase')
        hora_str = request.data.get('hora_inicio_clase')

        try:
            # Validar que el usuario existe
            perfil_usuario = Usuarios.objects.get(id_usuario=id_user_recibido)
            
            # Lógica de horario
            hora_obj = time.fromisoformat(hora_str)
            if not (time(6, 0) <= hora_obj <= time(21, 0)):
                return Response({"error": "Horario no permitido"}, status=400)

            # Lógica de duplicados
            if Clases.objects.filter(id_usuario=id_user_recibido, fecha_clase=fecha).exists():
                return Response({"error": "Ya tienes clase hoy"}, status=400)

            # Lógica de créditos
            if perfil_usuario.creditos_usuario <= 0:
                return Response({"error": "Sin créditos"}, status=402)

            # GUARDAR
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("ERRORES DEL SERIALIZER:", serializer.errors) # MUY IMPORTANTE
                return Response(serializer.errors, status=400)
            
            self.perform_create(serializer)
            perfil_usuario.creditos_usuario -= 1
            perfil_usuario.save()

            return Response(serializer.data, status=201)

        except Exception as e:
            print("ERROR CRÍTICO EN DJANGO:", str(e)) # Mira tu terminal cuando des click en el botón
            return Response({"error": str(e)}, status=500)
    
class Planificacion_diariaViewSet(viewsets.ModelViewSet):
    queryset = Planificacion_diaria.objects.all()
    serializer_class = Planificacion_diariaSerializer
    
class ResultadosViewSet(viewsets.ModelViewSet):
    queryset = Resultados.objects.all()
    serializer_class = ResultadosSerializer
    

    