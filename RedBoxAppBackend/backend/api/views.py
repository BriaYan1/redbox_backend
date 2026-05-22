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
from datetime import time, date
from rest_framework.decorators import action
from django.db import transaction
from dateutil.relativedelta import relativedelta

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
        fecha = self.request.query_params.get('fecha')
        hora = self.request.query_params.get('hora')

        if id_usuario is not None:
            queryset = queryset.filter(id_usuario=id_usuario)
        if fecha is not None:
            queryset = queryset.filter(fecha_clase__date=fecha)
        if hora is not None:
            queryset = queryset.filter(hora_inicio_clase=hora)
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
            if not (time(6, 0) <= hora_obj <= time(19, 0)):
                return Response({"error": "Horario no permitido, las clases son de 6am a 19pm"}, status=400)

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
        
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        clase = self.get_object()
        usuario = clase.id_usuario # Obtenemos el usuario de esa clase

        try:
            with transaction.atomic():
                # 1. Devolvemos el crédito
                usuario.creditos_usuario += 1
                usuario.save()

                # 2. Eliminamos la clase
                clase.delete()

            return Response({'message': 'Clase cancelada y crédito devuelto'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class Planificacion_diariaViewSet(viewsets.ModelViewSet):
    queryset = Planificacion_diaria.objects.all()
    serializer_class = Planificacion_diariaSerializer
    
class ResultadosViewSet(viewsets.ModelViewSet):
    queryset = Resultados.objects.all()
    serializer_class = ResultadosSerializer
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def registrar_pago(request):
    """
    Solo el admin puede llamar esto.
    Recibe: id_usuario, nombre_plan (Basico/Premium), monto, moneda, pin
    """
    PIN_ADMIN = "1234"  # Cámbialo por el que quieras

    id_usuario    = request.data.get('id_usuario')
    nombre_plan   = request.data.get('nombre_plan')  # 'Basico' o 'Premium'
    monto         = request.data.get('monto')
    moneda        = request.data.get('moneda')
    pin           = request.data.get('pin')

    # 1. Validar PIN
    if str(pin) != PIN_ADMIN:
        return Response({'error': 'PIN incorrecto'}, status=status.HTTP_403_FORBIDDEN)

    # 2. Validar campos
    if not all([id_usuario, nombre_plan, monto, moneda]):
        return Response({'error': 'Faltan campos obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

    # 3. Buscar usuario y plan
    try:
        usuario = Usuarios.objects.get(id_usuario=id_usuario)
    except Usuarios.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        plan = Planes.objects.get(nombre_plan=nombre_plan)
    except Planes.DoesNotExist:
        return Response({'error': f'Plan "{nombre_plan}" no existe. Crea los planes primero.'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        # 4. Desactivar suscripción anterior si existe
        Usuario_planes.objects.filter(id_usuario=usuario, activo_usuario_plan=True).update(activo_usuario_plan=False)

        # 5. Crear nueva suscripción (1 mes desde hoy)
        hoy = date.today()
        fecha_fin = hoy + relativedelta(months=1)

        suscripcion = Usuario_planes.objects.create(
            id_usuario=usuario,
            id_plan=plan,
            fecha_inicio_plan=hoy,
            fecha_fin_plan=fecha_fin,
            clases_restantes=plan.cantidad_clases,
            activo_usuario_plan=True,
        )

        # 6. Registrar el pago
        Pagos.objects.create(
            id_usuario_plan=plan,
            monto=monto,
            moneda=moneda,
            metodo_pago='Manual',
            comprobante_pago='',
            estado_pago=Pagos.COMPLETADO,
        )

        # 7. Asignar créditos al usuario
        usuario.creditos_usuario = plan.cantidad_clases
        usuario.save()

    return Response({
        'mensaje': f'Pago registrado. Se asignaron {plan.cantidad_clases} créditos a {usuario.pnombre_usuario}.',
        'fecha_inicio': str(hoy),
        'fecha_fin': str(fecha_fin),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def suscripcion_usuario(request, id_usuario):
    """
    Devuelve la suscripción activa de un usuario.
    """
    try:
        suscripcion = Usuario_planes.objects.select_related('id_plan').get(
            id_usuario=id_usuario,
            activo_usuario_plan=True
        )
        return Response({
            'plan': suscripcion.id_plan.nombre_plan,
            'fecha_inicio': suscripcion.fecha_inicio_plan,
            'fecha_fin': suscripcion.fecha_fin_plan,
            'clases_restantes': suscripcion.clases_restantes,
            'activo': suscripcion.activo_usuario_plan,
        })
    except Usuario_planes.DoesNotExist:
        return Response({'activo': False, 'plan': None}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def historial_pagos(request):
    id_usuario_filtro = request.query_params.get('id_usuario')
    fecha_filtro = request.query_params.get('fecha')  # formato YYYY-MM-DD

    try:
        perfil = Usuarios.objects.get(user=request.user)
        rol = Usuario_roles.objects.filter(id_usuario=perfil).select_related('id_rol').first()
        es_admin = rol and rol.id_rol.nombre_rol == 'Administrador'
    except Usuarios.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)

    pagos = Pagos.objects.select_related('id_usuario_plan').order_by('-fecha_pago')

    if es_admin:
        # Admin puede filtrar por usuario específico
        if id_usuario_filtro:
            planes_usuario = Usuario_planes.objects.filter(
                id_usuario=id_usuario_filtro
            ).values_list('id_plan', flat=True)
            pagos = pagos.filter(id_usuario_plan__in=planes_usuario)
    else:
        # Usuario normal solo ve sus propios pagos
        planes_propios = Usuario_planes.objects.filter(
            id_usuario=perfil
        ).values_list('id_plan', flat=True)
        pagos = pagos.filter(id_usuario_plan__in=planes_propios)

    # Filtro por fecha (aplica para ambos roles)
    if fecha_filtro:
        pagos = pagos.filter(fecha_pago__date=fecha_filtro)

    resultado = []
    for pago in pagos:
        usuario_plan = Usuario_planes.objects.filter(
            id_plan=pago.id_usuario_plan
        ).order_by('-fecha_inicio_plan').first()
        usuario = usuario_plan.id_usuario if usuario_plan else None

        resultado.append({
            'id_pago': pago.id_pago,
            'usuario': f"{usuario.pnombre_usuario} {usuario.papellido_usuario}" if usuario else 'Desconocido',
            'fecha': pago.fecha_pago.strftime('%d/%m/%Y'),
            'fecha_iso': pago.fecha_pago.strftime('%Y-%m-%d'),
            'monto': str(pago.monto),
            'moneda': pago.moneda,
            'plan': pago.id_usuario_plan.nombre_plan,
            'estado': pago.estado_pago,
        })

    return Response(resultado, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil_usuario(request, id_usuario):
    try:
        usuario = Usuarios.objects.get(id_usuario=id_usuario)
        rol = Usuario_roles.objects.filter(id_usuario=usuario).select_related('id_rol').first()
        datos = UsuariosSerializer(usuario).data
        datos['rol'] = rol.id_rol.nombre_rol if rol else 'Usuario'
        return Response(datos)
    except Usuarios.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def editar_mi_perfil(request):
    """
    Cualquier usuario autenticado puede editar su propio perfil
    """
    try:
        usuario = Usuarios.objects.get(user=request.user)
    except Usuarios.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    print("Datos recibidos:", data)  # Para depuración
    
    # Actualizar campos del usuario
    campos_usuario = [
        'pnombre_usuario', 'snombre_usuario', 'papellido_usuario', 
        'sapellido_usuario', 'telefono_usuario', 'fecha_nacimiento_usuario', 
        'genero_usuario', 'cedula_usuario', 'peso', 'altura'  # Agregar peso y altura aquí
    ]
    
    for campo in campos_usuario:
        if campo in data:
            setattr(usuario, campo, data[campo])
    
    # Cambiar contraseña si se proporciona
    nueva_contrasena = data.get('nueva_contrasena')
    if nueva_contrasena and len(nueva_contrasena) >= 6:
        usuario.user.set_password(nueva_contrasena)
        usuario.user.save()
    
    usuario.save()
    
    # Serializar y devolver datos actualizados
    serializer = UsuariosSerializer(usuario)
    response_data = serializer.data
    
    return Response(response_data, status=status.HTTP_200_OK)