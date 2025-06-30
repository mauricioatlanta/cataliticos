
from django.db import models

class PrecioMetal(models.Model):
    fecha = models.DateField(auto_now_add=True)
    platino = models.FloatField(help_text="Variación porcentual diaria del platino")
    paladio = models.FloatField(help_text="Variación porcentual diaria del paladio")
    rodio = models.FloatField(null=True, blank=True, help_text="Variación del rodio (solo se usa 1 y 15 de cada mes)")

    def __str__(self):
        return f"Precio {self.fecha} - Pt: {self.platino}% Pd: {self.paladio}% Rh: {self.rodio}%"


class Catalitico(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)
    valor = models.PositiveIntegerField(default=0)
    valor_actual = models.IntegerField(default=0)

    imagen_principal = models.ImageField(upload_to='cataliticos/', null=True, blank=True)
    imagen2 = models.ImageField(upload_to='cataliticos/', null=True, blank=True)
    imagen3 = models.ImageField(upload_to='cataliticos/', null=True, blank=True)
    imagen4 = models.ImageField(upload_to='cataliticos/', null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} - ${self.valor_actual}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)

    def __str__(self):
        rut_display = f"({self.rut})" if self.rut else "(Sin RUT)"
        return f"{self.nombre} {self.apellido} {rut_display}".strip()


class CompraCatalitico(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    cliente_telefono = models.CharField(max_length=30, blank=True)
    region = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    cliente_nombre = models.CharField(max_length=100)
    cliente_apellido = models.CharField(max_length=100, blank=True)
    cliente_rut = models.CharField(max_length=20, blank=True)  # Ahora es opcional
    fecha = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.subtotal() for item in self.detalles.all())

    def __str__(self):
        return f"Compra de {self.cliente_nombre} - {self.fecha.strftime('%Y-%m-%d')}"


class DetalleCatalitico(models.Model):
    compra = models.ForeignKey(CompraCatalitico, related_name='detalles', on_delete=models.CASCADE)
    catalitico = models.ForeignKey(Catalitico, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField()

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.catalitico.descripcion}"
