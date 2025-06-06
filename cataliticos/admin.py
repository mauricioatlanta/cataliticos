
from django.contrib import admin
from .models import Catalitico

@admin.register(Catalitico)
class CataliticoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion']
    list_filter = []
    search_fields = ('codigo', 'descripcion')