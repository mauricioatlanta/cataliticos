from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import urlencode
from .models import Catalitico, CompraCatalitico
from .forms import CataliticoForm, CompraForm
from cataliticos.models import CompraCatalitico
from django.db.models import Count
from django.utils.timezone import now, timedelta



def dashboard(request):
    dias = []
    ventas = []
    for i in range(7):
        dia = now().date() - timedelta(days=i)
        count = CompraCatalitico.objects.filter(fecha__date=dia).count()
        dias.insert(0, dia.strftime('%d/%m'))
        ventas.insert(0, count)

    top = (CompraCatalitico.objects
           .values('catalitico__codigo')
           .annotate(total=Count('id'))
           .order_by('-total')[:5])

    top_codigos = [t['catalitico__codigo'] for t in top]
    top_valores = [t['total'] for t in top]
    top_cataliticos = list(zip(top_codigos, top_valores))

    total_ventas = sum(ventas)

    return render(request, 'cataliticos/dashboard.html', {
        'dias': dias,
        'ventas': ventas,
        'top_codigos': top_codigos,
        'top_valores': top_valores,
        'top_cataliticos': top_cataliticos,
        'total_ventas': total_ventas,
        'codigos': Catalitico.objects.all(),
    })
             
 
def listado(request):
    cataliticos = Catalitico.objects.all().order_by('-id')
    return render(request, 'cataliticos/listado.html', {'cataliticos': cataliticos, 'codigo': ''})


def buscar_codigo(request):
    codigo = request.GET.get('q', '').strip()
    if codigo:
        try:
            resultado = Catalitico.objects.get(codigo__iexact=codigo)
            return render(request, 'cataliticos/compra.html', {'resultado': resultado})
        except Catalitico.DoesNotExist:
            return render(request, 'cataliticos/crear.html', {'codigo': codigo, 'form': CataliticoForm(initial={'codigo': codigo})})
    return render(request, 'cataliticos/compra.html')

def crear_catalitico(request):
    if request.method == 'POST':
        form = CataliticoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cataliticos:listado')
    else:
        form = CataliticoForm()
    return render(request, 'cataliticos/crear.html', {'form': form})

def comprar(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)
            compra.catalitico = catalitico
            compra.save()
            mensaje = f"Hola {compra.cliente_nombre}. Confirmamos la compra del catalítico {catalitico.codigo} por ${compra.valor_ofrecido:,}. Gracias por su compra. - Atlanta Reciclajes"
            link = "https://wa.me/?text=" + urlencode({'text': mensaje})
            return redirect(link)
    else:
        form = CompraForm()
    return render(request, 'cataliticos/compra.html', {'form': form, 'resultado': catalitico})

def compra(request):
    # Vista simple para /compra/
    return render(request, 'cataliticos/compra.html')


def editar_catalitico(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    if request.method == 'POST':
        form = CataliticoForm(request.POST, request.FILES, instance=catalitico)
        if form.is_valid():
            form.save()
            return redirect('cataliticos:listado')
    else:
        form = CataliticoForm(instance=catalitico)
    return render(request, 'cataliticos/editar.html', {'form': form, 'catalitico': catalitico})


def listado_y_busqueda(request):
    codigo = request.GET.get("q", "")
    resultado = None
    creado = False
    form = CataliticoForm()
    codigos = Catalitico.objects.all().order_by("-id")

    if codigo:
        try:
            resultado = Catalitico.objects.get(codigo__iexact=codigo.strip())
        except Catalitico.DoesNotExist:
            if request.method == "POST":
                form = CataliticoForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    creado = True
                    resultado = form.instance
        cataliticos = codigos.filter(codigo__icontains=codigo)
    else:
        cataliticos = codigos

    context = {
        "codigo": codigo,
        "resultado": resultado,
        "creado": creado,
        "form": form,
        "codigos": codigos,
        "cataliticos": cataliticos,
    }
    return render(request, "cataliticos/listado.html", context)
