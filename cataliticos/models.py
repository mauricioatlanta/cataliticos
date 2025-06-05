
from django.db import models

class Catalitico(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo
