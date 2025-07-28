from django.contrib import admin
from .models import Catalitico, PrecioMetal, Cliente, CompraCatalitico, DetalleCatalitico

@admin.register(Catalitico)
class CataliticoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'proveedor', 'valor_compra', 'valor_venta', 'cantidad', 'vendido']
    search_fields = ['codigo', 'descripcion']
    list_filter = ['proveedor', 'vendido']

@admin.register(PrecioMetal)
class PrecioMetalAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'platino', 'paladio', 'rodio']
    list_filter = ['fecha']
    ordering = ['-fecha']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'rut', 'telefono', 'ciudad', 'region']
    search_fields = ['nombre', 'apellido', 'rut']
    list_filter = ['region', 'ciudad']

class DetalleCataliticoInline(admin.TabularInline):
    model = DetalleCatalitico
    extra = 0

@admin.register(CompraCatalitico)
class CompraCataliticoAdmin(admin.ModelAdmin):
    list_display = ['cliente_nombre', 'cliente_rut', 'fecha', 'total']
    search_fields = ['cliente_nombre', 'cliente_rut']
    list_filter = ['fecha', 'region']
    inlines = [DetalleCataliticoInline]
