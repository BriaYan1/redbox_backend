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
from datetime import datetime
import random
import string
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

""""La clase viewset es una clase que proporciona una implementación completa de las operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para un modelo específico. Al definir un viewset, puedes especificar el queryset (conjunto de datos) y el serializer (serializador) que se utilizará para convertir los datos a formatos como JSON o XML."""

########################## INICIAR SESION ##############################
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

################# CREAR INVITACIONES ###################################

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generar_invitacion(request):
    """
    Genera un código de invitación único (válido por 30 minutos)
    Solo para administradores
    """
    try:
        usuario_actual = Usuarios.objects.get(user=request.user)
        rol_actual = Usuario_roles.objects.filter(id_usuario=usuario_actual, id_rol__nombre_rol='Administrador').exists()
        
        if not rol_actual:
            return Response({'error': 'No tienes permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
        
        # Generar código único de 8 caracteres alfanuméricos
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Verificar que no exista un código igual
        while Invitacion.objects.filter(codigo=codigo).exists():
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        invitacion = Invitacion.objects.create(
            codigo=codigo,
            creado_por=usuario_actual
        )
        
        return Response({
            'codigo': invitacion.codigo,
            'creado_en': invitacion.creado_en,
            'valido_hasta': invitacion.creado_en + timezone.timedelta(minutes=30),
            'es_valido': invitacion.es_valido()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_invitaciones(request):
    """
    Lista todas las invitaciones generadas
    Solo para administradores
    """
    try:
        usuario_actual = Usuarios.objects.get(user=request.user)
        rol_actual = Usuario_roles.objects.filter(id_usuario=usuario_actual, id_rol__nombre_rol='Administrador').exists()
        
        if not rol_actual:
            return Response({'error': 'No tienes permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
        
        invitaciones = Invitacion.objects.all().order_by('-creado_en')
        
        resultado = []
        for inv in invitaciones:
            resultado.append({
                'id_invitacion': inv.id_invitacion,
                'codigo': inv.codigo,
                'creado_en': inv.creado_en,
                'usado': inv.usado,
                'usado_por': inv.usado_por.pnombre_usuario if inv.usado_por else None,
                'creado_por': inv.creado_por.pnombre_usuario if inv.creado_por else None,
                'es_valido': inv.es_valido()
            })
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


######################## REGISTRO (CORREGIDO) ##############################

@api_view(['POST'])
def registro(request):
    """
    Registra un nuevo usuario en el sistema.
    El código de invitación solo se marca como usado después de crear el usuario exitosamente.
    """
    #Verificar código de invitación
    codigo_invitacion = request.data.get('codigo_invitacion')
    
    if not codigo_invitacion:
        return Response({'error': 'El código de invitación es requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        invitacion = Invitacion.objects.get(codigo=codigo_invitacion)
        
        if not invitacion.es_valido():
            return Response({'error': 'Código de invitación inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #validamos que existe y es válido
        
    except Invitacion.DoesNotExist:
        return Response({'error': 'Código de invitación inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    #Validar los datos del formulario
    serializer = UsuarioRegistroSerializer(data=request.data)
    
    if not serializer.is_valid():
        #Si hay errores en el formulario, el código sigue siendo válido
        print("❌ ERRORES DE VALIDACIÓN:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Crear el usuario (solo después de que todos los datos sean válidos)
    try:
        usuario = serializer.save()
    except Exception as e:
        #Si falla la creación del usuario, el código sigue siendo válido
        print(f"❌ Error creando usuario: {e}")
        return Response({'error': 'Error al crear el usuario'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    #Marcar el código como usado (solo después de crear el usuario exitosamente)
    invitacion.usado = True
    invitacion.usado_por = usuario
    invitacion.usado_en = timezone.now()
    invitacion.save()
    
    #ASIGNAR ROL "USUARIO" AUTOMÁTICAMENTE
    try:
        rol_usuario = Roles.objects.get(nombre_rol='Usuario')
        Usuario_roles.objects.create(
            id_usuario=usuario,
            id_rol=rol_usuario
        )
        print(f"✓ Rol 'Usuario' asignado a: {usuario.email_usuario}")
    except Roles.DoesNotExist:
        print("❌ ERROR: El rol 'Usuario' no existe. Ejecuta el script de roles primero.")
    
    #Generar token
    token, created = Token.objects.get_or_create(user=usuario.user)
    
    return Response({
        'token': token.key,
        'user_id': usuario.id_usuario,
        'email': usuario.email_usuario
    }, status=status.HTTP_201_CREATED)


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
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_usuarios_con_roles(request):
    """
    Lista todos los usuarios con su rol actual.
    Solo para administradores.
    """
    # Verificar que el usuario actual es administrador
    try:
        usuario_actual = Usuarios.objects.get(user=request.user)
        rol_actual = Usuario_roles.objects.filter(id_usuario=usuario_actual).first()
        
        if not rol_actual or rol_actual.id_rol.nombre_rol != 'Administrador':
            return Response(
                {'error': 'No tienes permisos de administrador'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except Usuarios.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Obtener todos los usuarios con sus roles
    usuarios = Usuarios.objects.all()
    resultado = []
    
    for usuario in usuarios:
        rol_usuario = Usuario_roles.objects.filter(id_usuario=usuario).first()
        resultado.append({
            'id_usuario': usuario.id_usuario,
            'pnombre_usuario': usuario.pnombre_usuario,
            'papellido_usuario': usuario.papellido_usuario,
            'email_usuario': usuario.email_usuario,
            'rol': rol_usuario.id_rol.nombre_rol if rol_usuario else 'Usuario',
            'activo': usuario.activo_usuario
        })
    
    return Response(resultado, status=status.HTTP_200_OK)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def asignar_rol(request, id_usuario):
    """
    Asigna un rol a un usuario específico.
    Solo para administradores.
    """
    # Verificar que el usuario actual es administrador
    try:
        usuario_actual = Usuarios.objects.get(user=request.user)
        rol_actual = Usuario_roles.objects.filter(id_usuario=usuario_actual).first()
        
        if not rol_actual or rol_actual.id_rol.nombre_rol != 'Administrador':
            return Response(
                {'error': 'No tienes permisos de administrador'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except Usuarios.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Obtener el usuario a modificar
    try:
        usuario = Usuarios.objects.get(id_usuario=id_usuario)
    except Usuarios.DoesNotExist:
        return Response(
            {'error': 'Usuario a modificar no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Obtener el nuevo rol
    nombre_rol = request.data.get('rol')
    if not nombre_rol:
        return Response(
            {'error': 'El rol es requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        rol = Roles.objects.get(nombre_rol=nombre_rol)
    except Roles.DoesNotExist:
        return Response(
            {'error': f'Rol "{nombre_rol}" no existe'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Actualizar o crear el rol del usuario
    usuario_rol, created = Usuario_roles.objects.update_or_create(
        id_usuario=usuario,
        defaults={'id_rol': rol}
    )
    
    return Response({
        'mensaje': f'Rol actualizado a {nombre_rol} para {usuario.pnombre_usuario} {usuario.papellido_usuario}',
        'usuario_id': usuario.id_usuario,
        'rol': nombre_rol
    }, status=status.HTTP_200_OK)

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
    
from rest_framework.decorators import action
from django.db import transaction

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
        print("=== CREANDO CLASE ===")
        print("DATOS RECIBIDOS:", request.data)
        
        id_user_recibido = request.data.get('id_usuario')
        fecha = request.data.get('fecha_clase')
        hora_str = request.data.get('hora_inicio_clase')

        try:
            perfil_usuario = Usuarios.objects.get(id_usuario=id_user_recibido)
            
            # Validar horario (solo horas exactas)
            hora_obj = time.fromisoformat(hora_str)
            hora_exacta = hora_obj.minute == 0
            hora_permitida = hora_obj.hour in [6,7,8,9,10,15,16,17,18,19]
            
            if not hora_permitida or not hora_exacta:
                return Response({"error": "Horario no permitido. Las clases son en punto (6:00, 7:00, 8:00... 19:00)"}, status=400)

            # Validar duplicados
            if Clases.objects.filter(id_usuario=id_user_recibido, fecha_clase=fecha).exists():
                return Response({"error": "Ya tienes clase hoy"}, status=400)

            # Validar créditos
            if perfil_usuario.creditos_usuario <= 0:
                return Response({"error": "Sin créditos"}, status=402)

            # Buscar entrenador asignado para este horario
            fecha_date = datetime.strptime(fecha, '%Y-%m-%d').date()
            horario_entrenador = HorarioEntrenador.objects.filter(
                fecha=fecha_date,
                hora_inicio=hora_str,
                activo=True
            ).first()
            
            print(f"Horario encontrado: {horario_entrenador}")
            
            id_entrenador = None
            if horario_entrenador:
                id_entrenador = horario_entrenador.id_entrenador.id_usuario
                print(f"Entrenador asignado: ID {id_entrenador}")
            else:
                print("No hay entrenador asignado para este horario")

            # Crear datos para guardar
            data = request.data.copy()
            if id_entrenador:
                data['id_entrenador'] = id_entrenador

            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                print("ERRORES DEL SERIALIZER:", serializer.errors)
                return Response(serializer.errors, status=400)
            
            self.perform_create(serializer)
            perfil_usuario.creditos_usuario -= 1
            perfil_usuario.save()

            return Response(serializer.data, status=201)

        except Exception as e:
            print("ERROR CRÍTICO EN DJANGO:", str(e))
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

    # ✅ AGREGAR ESTE MÉTODO PARA CANCELAR CLASES
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela una clase existente y devuelve el crédito al usuario.
        """
        print(f"=== CANCELANDO CLASE ID: {pk} ===")
        
        try:
            clase = self.get_object()
            usuario = clase.id_usuario
            
            print(f"Clase encontrada: {clase.id_clase}")
            print(f"Usuario: {usuario.pnombre_usuario} (Créditos actuales: {usuario.creditos_usuario})")
            
            with transaction.atomic():
                # Devolver el crédito al usuario
                usuario.creditos_usuario += 1
                usuario.save()
                print(f"Créditos después de devolver: {usuario.creditos_usuario}")
                
                # Eliminar la clase
                clase.delete()
                print("Clase eliminada correctamente")
            
            return Response({
                'message': 'Clase cancelada y crédito devuelto',
                'creditos_restantes': usuario.creditos_usuario
            }, status=status.HTTP_200_OK)
            
        except Clases.DoesNotExist:
            print(f"ERROR: Clase con ID {pk} no encontrada")
            return Response({'error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"ERROR CRÍTICO: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class Planificacion_diariaViewSet(viewsets.ModelViewSet):
    queryset = Planificacion_diaria.objects.all().order_by('-fecha')
    serializer_class = Planificacion_diariaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        return queryset
    
    def perform_create(self, serializer):
        # Obtener el usuario actual
        usuario = Usuarios.objects.get(user=self.request.user)
        serializer.save(creado_por=usuario)
    
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
    PIN_ADMIN = "1234"  

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

from django.db.models import Max, F
from django.db.models.functions import Coalesce

class MovimientosViewSet(viewsets.ModelViewSet):
    queryset = Movimientos.objects.all()
    serializer_class = MovimientosSerializer

class ResultadosViewSet(viewsets.ModelViewSet):
    queryset = Resultados.objects.all()
    serializer_class = ResultadosSerializer
    
    def get_queryset(self):
        queryset = Resultados.objects.all()
        id_usuario = self.request.query_params.get('id_usuario')
        id_movimiento = self.request.query_params.get('id_movimiento')
        
        if id_usuario:
            queryset = queryset.filter(id_usuario=id_usuario)
        if id_movimiento:
            queryset = queryset.filter(id_movimiento=id_movimiento)
            
        return queryset.order_by('-fecha_evaluacion')
    
    def create(self, request, *args, **kwargs):
        print("Datos recibidos:", request.data)
        return super().create(request, *args, **kwargs)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mejores_resultados(request, id_usuario, id_movimiento):
    """
    Devuelve los 5 mejores pesos registrados para un usuario y movimiento específico
    """
    resultados = Resultados.objects.filter(
        id_usuario=id_usuario,
        id_movimiento=id_movimiento
    ).order_by('-peso')[:5]
    
    serializer = ResultadosSerializer(resultados, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#Obtener alumnos de un entrenador específico
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mis_clases_con_alumnos(request):
    """
    Devuelve las clases del entrenador con los alumnos que han reservado.
    """
    try:
        entrenador = Usuarios.objects.get(user=request.user)
        
        # Verificar que el usuario es entrenador
        rol_entrenador = Usuario_roles.objects.filter(id_usuario=entrenador, id_rol__nombre_rol='Entrenador').exists()
        if not rol_entrenador:
            return Response({'error': 'No tienes permisos de entrenador'}, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener todas las clases futuras donde este usuario es entrenador
        ahora = datetime.now()
        clases = Clases.objects.filter(
            id_entrenador=entrenador,
            fecha_clase__gte=ahora
        ).order_by('fecha_clase', 'hora_inicio_clase')
        
        resultado = []
        for clase in clases:
            # Obtener el alumno que reservó esta clase
            alumno = clase.id_usuario
            
            # Verificar si ya existe esta clase en el resultado (para no duplicar)
            clase_existente = next((c for c in resultado if c['id_clase'] == clase.id_clase), None)
            
            if not clase_existente:
                resultado.append({
                    'id_clase': clase.id_clase,
                    'fecha': clase.fecha_clase.strftime('%Y-%m-%d'),
                    'hora_inicio': clase.hora_inicio_clase.strftime('%H:%M'),
                    'hora_fin': clase.hora_fin_clase.strftime('%H:%M'),
                    'descripcion': clase.descripcion_clase,
                    'cupo_maximo': clase.cupo_maximo_clase,
                    'alumnos': []
                })
                clase_existente = resultado[-1]
            
            # Agregar alumno a la clase
            if alumno:
                clase_existente['alumnos'].append({
                    'id_usuario': alumno.id_usuario,
                    'pnombre_usuario': alumno.pnombre_usuario,
                    'papellido_usuario': alumno.papellido_usuario,
                    'email_usuario': alumno.email_usuario,
                    'telefono_usuario': alumno.telefono_usuario
                })
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Usuarios.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtener_entrenadores(request):
    """Obtiene lista de usuarios con rol Entrenador"""
    try:
        entrenadores = Usuarios.objects.filter(
            usuario_roles__id_rol__nombre_rol='Entrenador'
        ).distinct()
        
        resultado = []
        for ent in entrenadores:
            resultado.append({
                'id_usuario': ent.id_usuario,
                'nombre': f"{ent.pnombre_usuario} {ent.papellido_usuario}",
                'email': ent.email_usuario
            })
        return Response(resultado, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtener_horarios_entrenador(request, id_entrenador):
    """Obtiene los horarios asignados a un entrenador"""
    try:
        # Verificar que el entrenador existe
        try:
            entrenador = Usuarios.objects.get(id_usuario=id_entrenador)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Entrenador no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener parámetros de fecha
        fecha_str = request.query_params.get('fecha')
        
        # Construir queryset
        queryset = HorarioEntrenador.objects.filter(id_entrenador=id_entrenador, activo=True)
        
        # Filtrar por fecha si se proporciona
        if fecha_str:
            try:
                from datetime import datetime
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha=fecha)
            except ValueError:
                return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ordenar por fecha y hora
        queryset = queryset.order_by('fecha', 'hora_inicio')
        
        # Preparar respuesta
        resultado = []
        for h in queryset:
            resultado.append({
                'id_horario': h.id_horario,
                'fecha': h.fecha.strftime('%Y-%m-%d'),
                'hora_inicio': h.hora_inicio,
                'hora_fin': h.hora_fin,
                'activo': h.activo
            })
        
        print(f"Horarios encontrados: {len(resultado)}")  # Log para depuración
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR en obtener_horarios_entrenador: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def asignar_horarios(request):
    """Asigna múltiples horarios a un entrenador para una fecha específica"""
    try:
        # Verificar que es administrador
        usuario_actual = Usuarios.objects.get(user=request.user)
        rol_actual = Usuario_roles.objects.filter(id_usuario=usuario_actual, id_rol__nombre_rol='Administrador').exists()
        
        if not rol_actual:
            return Response({'error': 'No tienes permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
        
        id_entrenador = request.data.get('id_entrenador')
        fecha = request.data.get('fecha')
        horas = request.data.get('horas', [])
        
        print("=== DATOS RECIBIDOS ===")
        print(f"id_entrenador: {id_entrenador}")
        print(f"fecha: {fecha}")
        print(f"horas: {horas}")
        
        if not id_entrenador or not fecha or not horas:
            return Response({'error': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        horarios_asignados = []
        errores = []
        
        for hora in horas:
            # Calcular hora_fin (1 hora después)
            hora_num = int(hora.split(':')[0])
            hora_fin = f"{hora_num + 1:02d}:00"
            
            # Verificar si ya existe
            existe = HorarioEntrenador.objects.filter(
                id_entrenador=id_entrenador,
                fecha=fecha,
                hora_inicio=hora
            ).exists()
            
            if not existe:
                horario = HorarioEntrenador.objects.create(
                    id_entrenador_id=id_entrenador,
                    fecha=fecha,
                    hora_inicio=hora,
                    hora_fin=hora_fin,
                    activo=True
                )
                horarios_asignados.append({
                    'id_horario': horario.id_horario,
                    'hora_inicio': hora,
                    'hora_fin': hora_fin
                })
            else:
                errores.append(f"El horario {hora} ya está asignado")
        
        return Response({
            'mensaje': f'Se asignaron {len(horarios_asignados)} horarios',
            'horarios_asignados': horarios_asignados,
            'errores': errores
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def eliminar_horario(request, id_horario):
    """Elimina un horario asignado a un entrenador"""
    try:
        usuario_actual = Usuarios.objects.get(user=request.user)
        rol_actual = Usuario_roles.objects.filter(id_usuario=usuario_actual, id_rol__nombre_rol='Administrador').exists()
        
        if not rol_actual:
            return Response({'error': 'No tienes permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
        
        horario = HorarioEntrenador.objects.get(id_horario=id_horario)
        horario.delete()
        
        return Response({'message': 'Horario eliminado correctamente'}, status=status.HTTP_200_OK)
        
    except HorarioEntrenador.DoesNotExist:
        return Response({'error': 'Horario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtener_entrenador_por_horario(request):
    """Obtiene el entrenador asignado para una fecha y hora específica"""
    fecha_str = request.query_params.get('fecha')
    hora_str = request.query_params.get('hora')
    
    print(f"=== Buscando entrenador para fecha: {fecha_str}, hora: {hora_str} ===")
    
    if not fecha_str or not hora_str:
        return Response({'error': 'Faltan fecha u hora'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Formato de fecha inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar entrenador con horario asignado
    horario = HorarioEntrenador.objects.filter(
        fecha=fecha,
        hora_inicio=hora_str,
        activo=True
    ).select_related('id_entrenador').first()
    
    print(f"Horario encontrado: {horario}")
    
    if horario:
        entrenador = horario.id_entrenador
        print(f"Entrenador encontrado: ID {entrenador.id_usuario} - {entrenador.pnombre_usuario}")
        return Response({
            'id_entrenador': entrenador.id_usuario,
            'nombre': f"{entrenador.pnombre_usuario} {entrenador.papellido_usuario}",
            'email': entrenador.email_usuario
        }, status=status.HTTP_200_OK)
    
    print("No se encontró entrenador para este horario")
    return Response({'id_entrenador': None, 'nombre': 'Por asignar'}, status=status.HTTP_200_OK)

########## RECUPERAR CONTRASEÑA ################################

@api_view(['POST'])
def solicitar_recuperacion(request):
    """
    Envía un código de verificación al email del usuario
    """
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'El email es requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        usuario = Usuarios.objects.get(user=user)
        
        # Generar código de 6 dígitos
        codigo = ''.join(random.choices(string.digits, k=6))
        
        # Guardar en base de datos
        RecuperacionContrasena.objects.create(
            email=email,
            codigo=codigo,
            usado=False
        )
        
        # Enviar email
        try:
            send_mail(
                'Recuperación de contraseña - RedBox',
                f'''Hola {usuario.pnombre_usuario},

                Has solicitado recuperar tu contraseña. 

                Tu código de verificación es: {codigo}

                Este código expira en 15 minutos.

                Si no solicitaste este cambio, ignora este mensaje.

                Saludos,
                Equipo RedBox''',
                                settings.DEFAULT_FROM_EMAIL,
                                [email],
                                fail_silently=False,
            )
            return Response({'message': 'Código enviado al correo electrónico'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error enviando email: {e}")
            return Response({'error': 'No se pudo enviar el correo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except User.DoesNotExist:
        # Por seguridad, no revelamos si el email existe o no
        return Response({'message': 'Si el email existe, se enviará un código de verificación'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error: {e}")
        return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verificar_codigo(request):
    """
    Verifica el código de recuperación
    """
    email = request.data.get('email')
    codigo = request.data.get('codigo')
    
    if not email or not codigo:
        return Response({'error': 'Email y código son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        recuperacion = RecuperacionContrasena.objects.filter(
            email=email,
            codigo=codigo,
            usado=False
        ).latest('creado_en')
        
        if recuperacion.es_valido():
            return Response({'message': 'Código válido'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Código expirado. Solicita un nuevo código'}, status=status.HTTP_400_BAD_REQUEST)
            
    except RecuperacionContrasena.DoesNotExist:
        return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def restablecer_password(request):
    """
    Restablece la contraseña del usuario
    """
    email = request.data.get('email')
    codigo = request.data.get('codigo')
    nueva_password = request.data.get('nueva_password')
    
    if not email or not codigo or not nueva_password:
        return Response({'error': 'Todos los campos son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(nueva_password) < 6:
        return Response({'error': 'La contraseña debe tener al menos 6 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        recuperacion = RecuperacionContrasena.objects.filter(
            email=email,
            codigo=codigo,
            usado=False
        ).latest('creado_en')
        
        if not recuperacion.es_valido():
            return Response({'error': 'Código expirado. Solicita un nuevo código'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(email=email)
        user.set_password(nueva_password)
        user.save()
        
        # Marcar código como usado
        recuperacion.usado = True
        recuperacion.save()
        
        # Marcar todos los códigos anteriores como usados
        RecuperacionContrasena.objects.filter(email=email, usado=False).update(usado=True)
        
        return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except RecuperacionContrasena.DoesNotExist:
        return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error: {e}")
        return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)