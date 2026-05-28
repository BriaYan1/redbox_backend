from django.core.management.base import BaseCommand
from backend.models import Movimientos

class Command(BaseCommand):
    help = 'Crea movimientos de CrossFit predeterminados'

    def handle(self, *args, **options):
        movimientos = [
            'Snatch',
            'Power Snatch',
            'Clean & Jerk',
            'Power Clean',
            'Deadlift',
            'Squat',
            'Front Squat',
            'Overhead Squat',
            'Push Press',
            'Push Jerk',
            'Split Jerk',
            'Clean',
            'Power Clean & Jerk',
            'Muscle Up',
            'Pull Up',
            'Burpee',
            'Box Jump',
            'Wall Ball',
            'Thruster',
            'Kettlebell Swing',
            'Handstand Push Up',
            'Double Under',
            'Rowing',
            'Run',
            'Bike'
        ]
        
        for movimiento in movimientos:
            obj, created = Movimientos.objects.get_or_create(nombre_movimiento=movimiento)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Creado: {movimiento}'))
            else:
                self.stdout.write(f'Ya existe: {movimiento}')
        
        self.stdout.write(self.style.SUCCESS('¡Movimientos creados exitosamente!'))