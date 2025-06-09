from django.shortcuts import render, redirect, get_object_or_404
from .models import CompraCatalitico
from .forms import CompraForm

def listado_compras(request):
    compras = CompraCatalitico.objects.order_by('-fecha')
    return render(request, 'cataliticos/listado_compras.html', {'compras': compras})

def editar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    form = CompraForm(request.POST or None, instance=compra)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cataliticos:listado_compras')

    return render(request, 'cataliticos/editar_compra.html', {'form': form, 'compra': compra})

def eliminar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    compra.delete()
    return redirect('cataliticos:listado_compras')
