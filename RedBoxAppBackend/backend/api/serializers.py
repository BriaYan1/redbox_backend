from rest_framework import serializers
from backend.models import *

"""El serializador convierte objetos complejos, como los modelos de Django, en tipos de datos nativos de Python que luego pueden ser fácilmente renderizados en JSON, XML u otros formatos de contenido. También se encarga de la validación de datos y la deserialización, es decir, convertir datos entrantes en objetos complejos."""


class PatologiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patologias
        fields = '__all__'

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'

class Usuario_rolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario_roles
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
    class Meta:
        model = Clases
        fields = '__all__'

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
