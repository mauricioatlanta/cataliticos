from django import forms
from .models import Catalitico, CompraCatalitico

class CataliticoForm(forms.ModelForm):
    class Meta:
        model = Catalitico
        fields = ['codigo', 'descripcion', 'valor', 'foto1', 'foto2', 'foto3', 'foto4']

class CompraForm(forms.ModelForm):
    class Meta:
        model = CompraCatalitico
        fields = ['cliente_nombre', 'cliente_rut', 'valor_ofrecido']
