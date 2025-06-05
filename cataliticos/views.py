from django.shortcuts import render
from .forms import CataliticoForm

def buscar_codigo(request):
    codigo = request.GET.get('q')
    resultado = None
    creado = False
    form = CataliticoForm()

    if codigo:
        try:
            resultado = Catalitico.objects.get(codigo__iexact=codigo.strip())
        except Catalitico.DoesNotExist:
            if request.method == 'POST':
                form = CataliticoForm(request.POST)
                if form.is_valid():
                    form.save()
                    creado = True
                    resultado = form.instance

    # SIEMPRE se devuelve la plantilla
    return render(request, 'cataliticos/busqueda.html', {
        'codigo': codigo,
        'resultado': resultado,
        'form': form,
        'creado': creado
    })
