from django.contrib import admin
from backend.models import Patologias
from backend.models import Roles
from backend.models import Usuarios
from backend.models import Usuario_roles
from backend.models import Biometrias
from backend.models import Entrenadores
from backend.models import Planes
from backend.models import Usuario_planes   
from backend.models import Accesos
from backend.models import Pagos
from backend.models import Clases
from backend.models import Planificacion_diaria
from backend.models import Movimientos
from backend.models import Resultados
from backend.models import Reservas


# Register your models here.

admin.site.register(Patologias)
admin.site.register(Roles)
admin.site.register(Usuarios)
admin.site.register(Usuario_roles)
admin.site.register(Biometrias)
admin.site.register(Entrenadores)
admin.site.register(Planes)
admin.site.register(Usuario_planes)
admin.site.register(Accesos)
admin.site.register(Pagos)
admin.site.register (Clases)
admin.site.register (Planificacion_diaria)
admin.site.register (Movimientos)
admin.site.register (Resultados)
admin.site.register (Reservas)

