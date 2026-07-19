# backend/views_biometrico.py
#
# Endpoint que consume el ESP32 despues de leer la huella.
#
# Flujo:
#   1. Recibe el numero de "slot" de la huella (posicion donde el sensor
#      la guardo internamente) y un identificador del dispositivo.
#   2. Busca en la tabla Biometria que usuario tiene registrado ese slot.
#   3. Verifica en Usuario_planes que tenga un plan activo y con clases
#      restantes.
#   4. Verifica en Reservas + Clases que tenga una clase reservada
#      (no cancelada) dentro de una ventana de +/- 15 minutos de ahora.
#   5. Registra el evento completo en MongoDB (coleccion access_logs).
#   6. Responde con el mensaje que el ESP32 debe mostrar en el OLED.

from datetime import timedelta, datetime

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .mongo_client import get_access_logs_collection
from .models import Usuarios, Biometria, Usuario_planes, Reservas, Clases


@api_view(["POST"])
def verificar_acceso(request):
    """
    Body esperado (JSON) que envia el ESP32:
    {
        "fingerprint_slot": 1,
        "device_id": "esp32-puerta-01"
    }
    """
    fingerprint_slot = request.data.get("fingerprint_slot")
    device_id = request.data.get("device_id", "desconocido")

    if fingerprint_slot is None:
        return Response({"acceso": False, "mensaje": "Solicitud invalida"}, status=400)

    # --- 1. Resolver a que usuario pertenece ese slot de huella ---
    # Guardamos el numero de slot como texto en huella_hash.
    registro_biometrico = Biometria.objects.filter(
        huella_hash=str(fingerprint_slot),
        tipo_biometria="huella",
        activo_biometria=True,
    ).select_related("id_usuario").first()

    if registro_biometrico is None:
        resultado = _construir_respuesta(
            acceso=False,
            mensaje="Huella no reconocida",
            usuario_id=None,
        )
        _registrar_evento_mongo(fingerprint_slot, device_id, resultado, usuario=None)
        return Response(resultado)

    usuario = registro_biometrico.id_usuario
    ahora = timezone.localtime(timezone.now())

    # --- 2. Plan/suscripcion activa ---
    plan_activo = Usuario_planes.objects.filter(
        id_usuario=usuario,
        activo_usuario_plan=True,
        fecha_fin_plan__gte=ahora.date(),
        clases_restantes__gt=0,
    ).exists()

    # --- 3. Reserva valida para la clase de "ahora" ---
    # Buscamos reservas del usuario (no canceladas) cuya clase caiga
    # dentro de una ventana de 15 minutos antes/despues de la hora actual.
    ventana_inicio = (ahora - timedelta(minutes=15)).time()
    ventana_fin = (ahora + timedelta(minutes=15)).time()

    reserva_valida = Reservas.objects.filter(
        id_usuario=usuario,
        id_clase__fecha_clase__date=ahora.date(),
        id_clase__hora_inicio_clase__lte=ventana_fin,
        id_clase__hora_fin_clase__gte=ventana_inicio,
    ).exclude(estado_reservas="Cancelado").exists()

    acceso_concedido = plan_activo and reserva_valida

    if acceso_concedido:
        mensaje = "Acceso concedido - Bienvenido"
    elif not plan_activo:
        mensaje = "Acceso denegado - Sin plan activo"
    else:
        mensaje = "Acceso denegado - Sin reserva activa"

    resultado = _construir_respuesta(
        acceso=acceso_concedido,
        mensaje=mensaje,
        usuario_id=usuario.id_usuario,
        plan_activo=plan_activo,
        reserva_valida=reserva_valida,
    )

    _registrar_evento_mongo(fingerprint_slot, device_id, resultado, usuario=usuario)

    # Si el acceso fue concedido, descontamos una clase del plan y
    # marcamos la reserva como "Asistido".
    if acceso_concedido:
        _descontar_clase_y_marcar_asistencia(usuario, ahora)

    return Response(resultado)


def _construir_respuesta(acceso, mensaje, usuario_id, plan_activo=None, reserva_valida=None):
    return {
        "acceso": acceso,
        "mensaje": mensaje,
        "usuario_id": usuario_id,
        "plan_activo": plan_activo,
        "reserva_valida": reserva_valida,
    }


def _registrar_evento_mongo(fingerprint_slot, device_id, resultado, usuario):
    """Inserta un documento del intento de acceso en MongoDB."""
    coleccion = get_access_logs_collection()
    coleccion.insert_one({
        "usuario_id": usuario.id_usuario if usuario else None,
        "nombre_usuario": usuario.pnombre_usuario if usuario else None,
        "device_id": device_id,
        "fingerprint_slot": fingerprint_slot,
        "timestamp": timezone.now(),
        "plan_activo": resultado.get("plan_activo"),
        "reserva_valida": resultado.get("reserva_valida"),
        "acceso_concedido": resultado["acceso"],
        "mensaje_mostrado": resultado["mensaje"],
    })


def _descontar_clase_y_marcar_asistencia(usuario, ahora):
    """Actualiza el plan (resta una clase) y marca la reserva como Asistido."""
    plan = Usuario_planes.objects.filter(
        id_usuario=usuario,
        activo_usuario_plan=True,
        clases_restantes__gt=0,
    ).order_by("fecha_fin_plan").first()

    if plan:
        plan.clases_restantes -= 1
        plan.save()

    reserva = Reservas.objects.filter(
        id_usuario=usuario,
        id_clase__fecha_clase__date=ahora.date(),
    ).exclude(estado_reservas="Cancelado").first()

    if reserva:
        reserva.estado_reservas = "Asistido"
        reserva.save()
