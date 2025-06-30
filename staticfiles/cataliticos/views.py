from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.http import urlencode
from django.db.models import Count, Q
from django.utils.timezone import now, timedelta
from urllib.parse import quote
from .models import Catalitico, Cliente, CompraCatalitico, DetalleCatalitico
from .forms import CataliticoForm, ClienteForm, CompraForm
from .views_compras import listado_compras


def dashboard(request):
    dias, ventas = [], []
    for i in range(7):
        dia = now().date() - timedelta(days=i)
        count = CompraCatalitico.objects.filter(fecha__date=dia).count()
        dias.insert(0, dia.strftime('%d/%m'))
        ventas.insert(0, count)

    top = CompraCatalitico.objects.values('cliente_nombre').annotate(total=Count('id')).order_by('-total')[:5]
    top_clientes = [t['cliente_nombre'] for t in top]
    top_valores = [t['total'] for t in top]
    total_ventas = sum(ventas)

    return render(request, 'dashboard.html', {
        'dias': dias,
        'ventas': ventas,
        'top_clientes': top_clientes,
        'top_valores': top_valores,
        'top_compras': zip(top_clientes, top_valores),
        'total_ventas': total_ventas,
        'codigos': Catalitico.objects.all(),
    })

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

    return render(request, "cataliticos/listado.html", {
        "codigo": codigo,
        "resultado": resultado,
        "creado": creado,
        "form": form,
        "codigos": codigos,
        "cataliticos": cataliticos,
    })

def editar_catalitico(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    form = CataliticoForm(request.POST or None, request.FILES or None, instance=catalitico)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cataliticos:listado')
    return render(request, 'editar.html', {'form': form, 'catalitico': catalitico})

def crear_catalitico(request):
    form = CataliticoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cataliticos:listado')
    return render(request, 'crear.html', {'form': form})

def eliminar_catalitico(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    catalitico.delete()
    return redirect('cataliticos:listado')

def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cataliticos:compra_multiple')
    return render(request, 'crear_cliente.html', {'form': form})

def crear_compra_multiple(request):
    cataliticos = Catalitico.objects.all()
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
        else:
            nombre = request.POST.get('cliente_nombre')
            apellido = request.POST.get('cliente_apellido')
            rut = request.POST.get('cliente_rut')
            telefono = request.POST.get('cliente_telefono')
            if not (nombre and rut):
                error = 'Debes seleccionar un cliente o ingresar nombre y RUT.'
                return render(request, 'crear_compra_multiple.html', {'cataliticos': cataliticos, 'error': error})
            cliente, _ = Cliente.objects.get_or_create(
                rut=rut,
                defaults={'nombre': nombre, 'apellido': apellido, 'telefono': telefono}
            )

        compra = CompraCatalitico.objects.create(cliente_nombre=f"{cliente.nombre} {cliente.apellido}", cliente_rut=cliente.rut)

        codigos = request.POST.getlist('codigo[]')
        cantidades = request.POST.getlist('cantidad[]')
        valores = request.POST.getlist('valor_unitario[]')

        for codigo, cantidad, precio in zip(codigos, cantidades, valores):
            try:
                catalitico = Catalitico.objects.get(codigo=codigo.strip())
                DetalleCatalitico.objects.create(
                    compra=compra,
                    catalitico=catalitico,
                    cantidad=int(cantidad),
                    precio_unitario=int(precio)
                )
            except Catalitico.DoesNotExist:
                continue

        mensaje = (
            "📄 *Atlanta Reciclajes Spa*%0A"
            "🧾 *Recibo de Compra*%0A%0A"
            f"👤 Cliente: {cliente.nombre} {cliente.apellido}%0A"
            f"🛒 Detalle:%0A"
        )
        for detalle in compra.detalles.all():
            subtotal = detalle.subtotal()
            mensaje += f"• {detalle.catalitico.codigo} - {detalle.cantidad} x ${detalle.precio_unitario:,} = ${subtotal:,}%0A"
        mensaje += f"%0A💰 Total: ${compra.total():,}%0A"
        mensaje += "✅ ¡Gracias por preferirnos!"
        return redirect(f"https://wa.me/?text={quote(mensaje)}")

    return render(request, 'crear_compra_multiple.html', {'cataliticos': cataliticos})

def api_buscar_catalitico(request):
    q = request.GET.get('term', '').strip()
    cataliticos = Catalitico.objects.filter(Q(codigo__icontains=q)).values('id', 'codigo', 'descripcion', 'valor')[:10]
    resultados = [{'id': c['id'], 'text': c['codigo'], 'descripcion': c['descripcion'], 'valor': c['valor']} for c in cataliticos]
    return JsonResponse({'results': resultados})

def api_buscar_cliente(request):
    q = request.GET.get('term', '').strip()
    clientes = Cliente.objects.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q)).values('id', 'nombre', 'apellido', 'rut')[:10]
    resultados = [{'id': c['id'], 'text': f"{c['nombre']} {c['apellido']} ({c['rut']})"} for c in clientes]
    return JsonResponse({'results': resultados})
