from django.shortcuts import render
from .models import Catalitico
from .forms import CataliticoForm
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseServerError

@csrf_protect
def buscar_codigo(request):
    try:
        codigo = request.GET.get('q', '').strip()
        resultado = None
        creado = False
        form = CataliticoForm()

        if codigo:
            try:
                resultado = Catalitico.objects.get(codigo__iexact=codigo)
            except Catalitico.DoesNotExist:
                if request.method == 'POST':
                    form = CataliticoForm(request.POST)
                    if form.is_valid():
                        form.save()
                        resultado = form.instance
                        creado = True

        return render(request, 'cataliticos/busqueda.html', {
            'codigo': codigo,
            'resultado': resultado,
            'form': form,
            'creado': creado
        })

    except Exception as e:
        return HttpResponseServerError(f"<h1>500 Error del servidor</h1><pre>{e}</pre>")
