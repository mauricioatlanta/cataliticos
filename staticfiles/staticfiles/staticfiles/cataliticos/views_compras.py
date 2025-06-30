from django.shortcuts import render, redirect, get_object_or_404
from .models import CompraCatalitico

def listado_compras(request):
    compras = CompraCatalitico.objects.order_by('-fecha')
    return render(request, 'listado_compras.html', {'compras': compras})

def editar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    # Aquí agregas lógica para formulario si deseas editar.
    return redirect('cataliticos:listado_compras')

def eliminar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    compra.delete()
    return redirect('cataliticos:listado_compras')
