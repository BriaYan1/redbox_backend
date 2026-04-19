from django.db import models

# Create your models here.
class Patologias(models.Model):
    id_patologia = models.AutoField(primary_key=True)
    nombre_patologia = models.CharField(max_length=100)

    def __str__(self):
        return self.title