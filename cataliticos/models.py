from django.db import models

class Catalitico(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    foto1 = models.ImageField(upload_to='media/img/imagenes_cataliticos/', blank=True, null=True)
    foto2 = models.ImageField(upload_to='media/img/imagenes_cataliticos/', blank=True, null=True)
    foto3 = models.ImageField(upload_to='media/img/imagenes_cataliticos/', blank=True, null=True)
    foto4 = models.ImageField(upload_to='media/img/imagenes_cataliticos/', blank=True, null=True)
    valor = models.IntegerField(default=0)

    def __str__(self):
        return self.codigo

class CompraCatalitico(models.Model):
    catalitico = models.ForeignKey(Catalitico, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=100)
    cliente_rut = models.CharField(max_length=20, blank=True)
    valor_ofrecido = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra {self.catalitico.codigo} - {self.cliente_nombre}"
