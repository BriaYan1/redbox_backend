from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Roles(models.Model):
    # Definimos las constantes para los roles
    ADMINISTRADOR = 'Administrador'
    USUARIO = 'Usuario'
    ENTRENADOR = 'Entrenador'

    # Creamos la lista de opciones (tupla de tuplas)
    OPCIONES_ROLES = [
        (ADMINISTRADOR, 'Administrador'),
        (USUARIO, 'Usuario'),
        (ENTRENADOR, 'Entrenador'),
    ]

    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(
        max_length=50,
        choices=OPCIONES_ROLES, 
        default=USUARIO,        
        unique=True             
    )

    def __str__(self):
        return self.nombre_rol


class Usuarios(models.Model):
    MASCULINO = 'M'
    FEMENINO = 'F'
    OTRO = 'Otro'

    # Creamos la lista de opciones (tupla de tuplas)
    OPCIONES_GENERO = [
        (MASCULINO, 'M'),
        (FEMENINO , 'F'),
        (OTRO, 'Otro'),

    ]
    
    id_usuario = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pnombre_usuario = models.CharField(max_length=100)
    snombre_usuario = models.CharField(max_length=100)
    papellido_usuario = models.CharField(max_length=100)
    sapellido_usuario = models.CharField(max_length=100)
    email_usuario = models.EmailField(unique=True)
    cedula_usuario = models.CharField(max_length=20, unique=True)
    telefono_usuario = models.CharField(max_length=20, unique=True)
    fecha_nacimiento_usuario = models.DateField()
    genero_usuario = models.CharField(
        max_length= 5,
        choices=OPCIONES_GENERO,      
    )
    fecha_creacion_usuario = models.DateTimeField(auto_now_add=True)
    activo_usuario = models.BooleanField(default=True)
    creditos_usuario = models.IntegerField(default=0)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class Usuario_roles(models.Model):
    id_usuario_rol = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    id_rol = models.ForeignKey(Roles, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_usuario} - {self.id_rol}"
    
class Biometria(models.Model):
    id_biometria = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    tipo_biometria = models.CharField(max_length=100)
    huella_hash = models.CharField(max_length=100)
    fecha_registro_biometria = models.DateTimeField(auto_now_add=True)
    activo_biometria = models.BooleanField(default=True)
    
class Planes(models.Model):
    id_plan = models.AutoField(primary_key=True)
    nombre_plan = models.CharField(max_length=100)
    cantidad_clases = models.IntegerField()
    precio_plan = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion_plan = models.TextField()

class Usuario_planes(models.Model):
    id_usuario_plan = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE)
    fecha_inicio_plan = models.DateField()
    fecha_fin_plan = models.DateField()
    clases_restantes = models.IntegerField()
    activo_usuario_plan = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_usuario
    

class Accesos(models.Model):
    id_acceso = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fecha_acceso = models.DateTimeField(auto_now_add=True)
    tipo_acceso = models.CharField(max_length=100)
    permitido_acceso = models.BooleanField(default=True)
    motivo_acceso = models.TextField()
    
class Pagos(models.Model):
    
    COMPLETADO = 'Completado'
    PENDIENTE = 'Pendiente'
    FALLIDO = 'Fallido'

    ESTADOS_PAGO= [
        (COMPLETADO, 'Completado'),
        (PENDIENTE, 'Pendiente'),
        (FALLIDO, 'Fallido'),
    ]
    
    id_pago = models.AutoField(primary_key=True)
    id_usuario_plan = models.ForeignKey(Planes, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=100)
    comprobante_pago = models.CharField(max_length=100)
    estado_pago = models.CharField(max_length=100) 
    
    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADOS_PAGO,
        default=PENDIENTE, # Por defecto, todo pago entra como pendiente
    )

class Patologias(models.Model):
    id_patologia = models.AutoField(primary_key=True)
    nombre_patologia = models.CharField(max_length=100)

    def __str__(self):
        return self.title
    
class Usuario_patologias(models.Model):
    id_usuario_patologia = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    id_patologia = models.ForeignKey(Patologias, on_delete=models.CASCADE)
    observaciones_patologia = models.TextField()
    

class Clases(models.Model):
    id_clase = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='clases_reservadas')  
    id_entrenador = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='clases_impartidas', null=True, blank=True)  
    fecha_clase = models.DateTimeField()
    hora_inicio_clase = models.TimeField()
    hora_fin_clase = models.TimeField()
    cupo_maximo_clase = models.IntegerField()
    descripcion_clase = models.TextField()
    
class Planificacion_diaria(models.Model):
    id_planificacion = models.AutoField(primary_key=True)
    fecha = models.DateField(unique=True)
    entrenamiento = models.TextField()  # Contenido del entrenamiento
    observaciones = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Planificación {self.fecha}"

class Movimientos(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    nombre_movimiento = models.CharField(max_length=100)

class Resultados(models.Model):
    KG = 'kg'
    LB = 'lb'
    
    UNIDADES = [
        (KG, 'kg'),
        (LB, 'lb'),
    ]
    
    id_resultado = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    id_movimiento = models.ForeignKey(Movimientos, on_delete=models.CASCADE)
    fecha_evaluacion = models.DateField()  
    fecha_registro_resultado = models.DateTimeField(auto_now_add=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2)
    repeticiones = models.IntegerField()
    rondas = models.IntegerField()
    unidad = models.CharField(max_length=2, choices=UNIDADES, default=KG)
    comentarios_resultado = models.TextField(blank=True, null=True)
    
class Reservas(models.Model):
    ASISTIDO = 'Asistido'
    CANCELADO = 'Cancelado'
    
    ESTADOS_RESERVAS = [
        (ASISTIDO, 'Asistido'),
        (CANCELADO, 'Cancelado'),
    ]
    
    id_reserva = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    id_clase = models.ForeignKey(Clases, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado_reservas = models.CharField(
        max_length=20,
        choices=ESTADOS_RESERVAS,
    )

class HorarioEntrenador(models.Model):
    HORAS_DISPONIBLES = [
        ('06:00', '6:00 AM'),
        ('07:00', '7:00 AM'),
        ('08:00', '8:00 AM'),
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
        ('17:00', '5:00 PM'),
        ('18:00', '6:00 PM'),
        ('19:00', '7:00 PM'),
    ]
    
    id_horario = models.AutoField(primary_key=True)
    id_entrenador = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='horarios')
    fecha = models.DateField()  # Fecha específica
    hora_inicio = models.CharField(max_length=5, choices=HORAS_DISPONIBLES)
    hora_fin = models.CharField(max_length=5)
    activo = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['id_entrenador', 'fecha', 'hora_inicio']
    
    def __str__(self):
        return f"{self.id_entrenador.pnombre_usuario} - {self.fecha} {self.hora_inicio}"
    
class RecuperacionContrasena(models.Model):
    id_recuperacion = models.AutoField(primary_key=True)
    email = models.EmailField()
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    
    def es_valido(self):
        """Verifica si el código fue creado en los últimos 15 minutos"""
        from django.utils import timezone
        from datetime import timedelta
        expiracion = self.creado_en + timedelta(minutes=15)
        return not self.usado and timezone.now() <= expiracion
    
    def __str__(self):
        return f"{self.email} - {self.codigo} - Válido: {self.es_valido()}"