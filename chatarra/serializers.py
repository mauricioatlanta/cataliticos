from rest_framework import serializers
from cataliticos.models import ProductoChatarra

class ProductoChatarraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoChatarra
        fields = ['id', 'nombre', 'codigo', 'categoria', 'precio_kg', 'imagen']
