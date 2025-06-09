from django import forms
from .models import Catalitico, Cliente, CompraCatalitico

class CataliticoForm(forms.ModelForm):
    class Meta:
        model = Catalitico
        fields = ['codigo', 'descripcion', 'valor', 'imagen_principal', 'imagen2', 'imagen3', 'imagen4']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido', 'rut', 'telefono',
            'correo', 'direccion', 'region', 'ciudad'
        ]

class CompraForm(forms.ModelForm):
    class Meta:
        model = CompraCatalitico
        fields = ['cliente_nombre', 'cliente_rut']
