from rest_framework import serializers
from backend.models import *
from django.contrib.auth.models import User

"""El serializador convierte objetos complejos, como los modelos de Django, en tipos de datos nativos de Python que luego pueden ser fácilmente renderizados en JSON, XML u otros formatos de contenido. También se encarga de la validación de datos y la deserialización, es decir, convertir datos entrantes en objetos complejos."""


class PatologiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patologias
        fields = '__all__'

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    contrasena_usuario = serializers.CharField(write_only=True)
    user = serializers.IntegerField(required=False, read_only=True)  # override manual

    class Meta:
        model = Usuarios
        fields = [
            'user',  # lo dejamos pero como read_only e integer
            'pnombre_usuario', 'snombre_usuario', 'papellido_usuario', 
            'sapellido_usuario', 'email_usuario', 'cedula_usuario', 
            'telefono_usuario', 'fecha_nacimiento_usuario', 
            'genero_usuario', 'contrasena_usuario'
        ]

    def create(self, validated_data):
        validated_data.pop('user', None)  # por si acaso llega algo
        password = validated_data.pop('contrasena_usuario')
        email = validated_data.get('email_usuario')
        user = User.objects.create_user(
            username=email, 
            email=email, 
            password=password
        )
        usuario = Usuarios.objects.create(
            user=user,
            creditos_usuario=20, 
            **validated_data
        )
        return usuario
    
class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'

class Usuario_rolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario_roles
        fields = '__all__'


class BiometriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biometria
        fields = '__all__'
        

class PlanesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planes
        fields = '__all__'

class Usuario_planesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario_planes
        fields = '__all__'

class AccesosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accesos
        fields = '__all__'

class PagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'

class Usuario_patologiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario_patologias
        fields = '__all__'

class ClasesSerializer(serializers.ModelSerializer):
    id_usuario = serializers.PrimaryKeyRelatedField(queryset=Usuarios.objects.all())
    nombre_usuario = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Clases
        fields = '__all__'

    def get_nombre_usuario(self, obj):
        return f"{obj.id_usuario.pnombre_usuario} {obj.id_usuario.papellido_usuario}"

class Planificacion_diariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planificacion_diaria
        fields = '__all__'

class MovimientosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimientos
        fields = '__all__'

class ResultadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resultados
        fields = '__all__'

class ReservasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservas
        fields = '__all__'
