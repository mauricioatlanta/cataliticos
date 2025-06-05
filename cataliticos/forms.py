
from django import forms
from .models import Catalitico

class CataliticoForm(forms.ModelForm):
    class Meta:
        model = Catalitico
        fields = ['codigo', 'descripcion', 'valor_estimado']
