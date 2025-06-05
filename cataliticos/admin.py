
from django.contrib import admin
from .models import Catalitico

@admin.register(Catalitico)
class CataliticoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'valor_estimado', 'fecha_creacion')
    search_fields = ('codigo', 'descripcion')
    list_filter = ('fecha_creacion',)
