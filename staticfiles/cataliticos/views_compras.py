from django.shortcuts import render, redirect, get_object_or_404
from .models import CompraCatalitico
from .forms import CompraForm

def crear_compra(request):
    form = CompraForm()
    if request.method == "POST":
        form = CompraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cataliticos:listado_compras')
    return render(request, 'crear_compra_multiple.html', {'form': form})


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
