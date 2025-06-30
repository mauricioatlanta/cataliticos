from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from django.db import models
from .models import Catalitico, Cliente, CompraCatalitico, DetalleCatalitico
from .forms import CataliticoForm, ClienteForm, CompraForm, DetalleCataliticoFormSet

def dashboard(request):
    from django.db.models import Sum, Avg, Max, Min, Count, Q
    from django.utils import timezone
    import json
    
    # Estadísticas generales
    total_cataliticos = Catalitico.objects.count()
    total_clientes = Cliente.objects.count()
    total_compras = CompraCatalitico.objects.count()
    valor_total_inventario = Catalitico.objects.aggregate(total=Sum('valor_actual'))['total'] or 0
    valor_promedio_catalitico = Catalitico.objects.aggregate(avg=Avg('valor_actual'))['avg'] or 0
    
    # Ventas últimos 7 días
    dias, ventas, ingresos_diarios = [], [], []
    for i in range(7):
        dia = now().date() - timedelta(days=i)
        compras_dia = CompraCatalitico.objects.filter(fecha__date=dia)
        count = compras_dia.count()
        ingresos = sum([compra.total() for compra in compras_dia])
        
        dias.insert(0, dia.strftime('%d/%m'))
        ventas.insert(0, count)
        ingresos_diarios.insert(0, ingresos)
    
    # Top 5 clientes por número de compras
    top_clientes_compras = CompraCatalitico.objects.values('cliente_nombre').annotate(
        total_compras=Count('id'),
        total_gastado=Sum('detalles__cantidad') * Sum('detalles__precio_unitario')
    ).order_by('-total_compras')[:5]
    
    # Top 5 catalíticos más vendidos
    top_cataliticos = DetalleCatalitico.objects.values(
        'catalitico__codigo', 
        'catalitico__descripcion'
    ).annotate(
        total_vendido=Sum('cantidad'),
        ingresos_generados=Sum('cantidad') * Sum('precio_unitario')
    ).order_by('-total_vendido')[:5]
    
    # Estadísticas por mes (últimos 6 meses)
    meses, ventas_mensuales, ingresos_mensuales = [], [], []
    for i in range(6):
        mes = now().date().replace(day=1) - timedelta(days=30*i)
        compras_mes = CompraCatalitico.objects.filter(
            fecha__year=mes.year, 
            fecha__month=mes.month
        )
        ventas_mes = compras_mes.count()
        ingresos_mes = sum([compra.total() for compra in compras_mes])
        
        meses.insert(0, mes.strftime('%b %Y'))
        ventas_mensuales.insert(0, ventas_mes)
        ingresos_mensuales.insert(0, ingresos_mes)
    
    # Distribución de precios de catalíticos
    rangos_precios = {
        '0-10k': Catalitico.objects.filter(valor_actual__lt=10000).count(),
        '10k-25k': Catalitico.objects.filter(valor_actual__gte=10000, valor_actual__lt=25000).count(),
        '25k-50k': Catalitico.objects.filter(valor_actual__gte=25000, valor_actual__lt=50000).count(),
        '50k+': Catalitico.objects.filter(valor_actual__gte=50000).count(),
    }
    
    # Catalíticos más caros y más baratos
    catalitico_mas_caro = Catalitico.objects.order_by('-valor_actual').first()
    catalitico_mas_barato = Catalitico.objects.order_by('valor_actual').first()
    
    # Compras recientes (últimas 5)
    compras_recientes = CompraCatalitico.objects.select_related().order_by('-fecha')[:5]
    
    # Clientes que más gastan
    top_clientes_gastos = []
    for compra_data in top_clientes_compras:
        cliente_compras = CompraCatalitico.objects.filter(cliente_nombre=compra_data['cliente_nombre'])
        total_gastado = sum([compra.total() for compra in cliente_compras])
        top_clientes_gastos.append({
            'nombre': compra_data['cliente_nombre'],
            'compras': compra_data['total_compras'],
            'gastado': total_gastado
        })
    
    # Datos para gráficos (formato JSON)
    chart_data = {
        'ventas_diarias': {
            'labels': dias,
            'data': ventas,
            'ingresos': ingresos_diarios
        },
        'ventas_mensuales': {
            'labels': meses,
            'ventas': ventas_mensuales,
            'ingresos': ingresos_mensuales
        },
        'top_cataliticos': {
            'labels': [item['catalitico__codigo'] for item in top_cataliticos],
            'data': [item['total_vendido'] for item in top_cataliticos]
        },
        'rangos_precios': {
            'labels': list(rangos_precios.keys()),
            'data': list(rangos_precios.values())
        }
    }
    
    context = {
        # Estadísticas generales
        'total_cataliticos': total_cataliticos,
        'total_clientes': total_clientes,
        'total_compras': total_compras,
        'valor_total_inventario': valor_total_inventario,
        'valor_promedio_catalitico': valor_promedio_catalitico,
        
        # Datos históricos
        'dias': dias,
        'ventas': ventas,
        'total_ventas': sum(ventas),
        'ingresos_diarios': ingresos_diarios,
        'total_ingresos_semana': sum(ingresos_diarios),
        
        # Top lists
        'top_clientes': top_clientes_gastos[:5],
        'top_cataliticos': top_cataliticos,
        'compras_recientes': compras_recientes,
        
        # Records
        'catalitico_mas_caro': catalitico_mas_caro,
        'catalitico_mas_barato': catalitico_mas_barato,
        
        # Datos para gráficos
        'chart_data_json': json.dumps(chart_data),
        
        # Códigos (para compatibilidad)
        'codigos': Catalitico.objects.all(),
    }
    
    return render(request, 'cataliticos/dashboard.html', context)


def crear_catalitico(request):
    form = CataliticoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            catalitico = form.save()
            messages.success(request, f"✅ Catalítico '{catalitico.codigo}' creado exitosamente.")
            return redirect('cataliticos:listado')
        else:
            messages.error(request, "❌ Por favor, corrige los errores en el formulario.")
    return render(request, 'cataliticos/crear.html', {'form': form})

def editar_catalitico(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    form = CataliticoForm(request.POST or None, request.FILES or None, instance=catalitico)
    if request.method == 'POST':
        if form.is_valid():
            catalitico_actualizado = form.save()
            messages.success(request, f"✅ Catalítico '{catalitico_actualizado.codigo}' actualizado exitosamente.")
            return redirect('cataliticos:listado')
        else:
            messages.error(request, "❌ Por favor, corrige los errores en el formulario.")
    return render(request, 'cataliticos/editar.html', {'form': form, 'catalitico': catalitico})


def eliminar_catalitico(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    
    try:
        catalitico.delete()
        messages.success(request, f"✅ El catalítico '{catalitico.codigo}' fue eliminado correctamente.")
    except models.ProtectedError as e:
        # Obtener información sobre las referencias que impiden la eliminación
        protected_objects = e.protected_objects
        compras_count = len([obj for obj in protected_objects if obj.__class__.__name__ == 'DetalleCatalitico'])
        
        messages.error(request, 
            f"❌ No se puede eliminar el catalítico '{catalitico.codigo}' porque está siendo usado en {compras_count} compra(s). "
            f"Para eliminarlo, primero debe eliminar o modificar las compras que lo contienen."
        )
        return redirect('cataliticos:editar', pk=pk)
    except Exception as e:
        messages.error(request, f"❌ Error inesperado al eliminar el catalítico: {str(e)}")
        return redirect('cataliticos:editar', pk=pk)
    
    return redirect('cataliticos:listado')

def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cataliticos:crear_compra_multiple')
    return render(request, 'cataliticos/crear_cliente.html', {'form': form})

def crear_compra_multiple(request):
    cataliticos = Catalitico.objects.all()
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
            cliente_nombre = cliente.nombre
            cliente_apellido = cliente.apellido
            cliente_rut = cliente.rut
            cliente_telefono = cliente.telefono
        else:
            nombre = request.POST.get('cliente_nombre')
            apellido = request.POST.get('cliente_apellido')
            rut = request.POST.get('cliente_rut')
            telefono = request.POST.get('cliente_telefono')
            cliente = None
            if nombre and rut:
                cliente, _ = Cliente.objects.get_or_create(
                    rut=rut,
                    defaults={'nombre': nombre, 'apellido': apellido, 'telefono': telefono}
                )
            cliente_nombre = nombre
            cliente_apellido = apellido
            cliente_rut = rut
            cliente_telefono = telefono

        compra = CompraCatalitico.objects.create(
            cliente=cliente,
            cliente_nombre=cliente_nombre or "",
            cliente_apellido=cliente_apellido or "",
            cliente_rut=cliente_rut or "",
            cliente_telefono=cliente_telefono or "",
            region=request.POST.get("region") or "",
            ciudad=request.POST.get("ciudad") or "",
        )

        codigos = request.POST.getlist('codigo[]')
        cantidades = request.POST.getlist('cantidad[]')
        valores = request.POST.getlist('valor_unitario[]')

        for codigo, cantidad_str, precio_str in zip(codigos, cantidades, valores):
            try:
                catalitico = Catalitico.objects.get(codigo=codigo.strip())
                try:
                    cantidad = Decimal(cantidad_str)
                    precio = Decimal(precio_str)
                except (InvalidOperation, ValueError):
                    continue

                if cantidad > 0 and precio >= 0:
                    DetalleCatalitico.objects.create(
                        compra=compra,
                        catalitico=catalitico,
                        cantidad=cantidad,
                        precio_unitario=precio
                    )
            except Catalitico.DoesNotExist:
                continue

        messages.success(request, "✅ La compra se guardó correctamente, incluso con datos parciales.")
        return redirect('cataliticos:listado_compras')

    return render(request, 'cataliticos/crear_compra_multiple.html', {'cataliticos': cataliticos})

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

def listado_compras(request):
    compras = CompraCatalitico.objects.order_by('-fecha')
    return render(request, 'cataliticos/listado_compras.html', {'compras': compras})

def editar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    form = CompraForm(request.POST or None, instance=compra)
    formset = DetalleCataliticoFormSet(request.POST or None, instance=compra)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            
            if formset.is_valid():
                # Guardar el formset
                instances = formset.save(commit=False)
                
                # Procesar cada instancia para manejar el código del catalítico
                for instance in instances:
                    # El método save del DetalleCataliticoForm ya maneja la lógica del código
                    instance.save()
                
                # Eliminar las instancias marcadas para eliminación
                for obj in formset.deleted_objects:
                    obj.delete()
                
                messages.success(request, "✅ La compra se actualizó correctamente.")
                return redirect('cataliticos:listado_compras')
            else:
                messages.error(request, "❌ Por favor, corrige los errores en los catalíticos.")
        else:
            messages.error(request, "❌ Por favor, corrige los errores en el formulario.")

    return render(request, 'cataliticos/editar_compra.html', {
        'form': form, 
        'compra': compra, 
        'formset': formset
    })

def eliminar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    compra.delete()
    return redirect('cataliticos:listado_compras')

def api_buscar_catalitico(request):
    q = request.GET.get('term', '').strip()
    cataliticos = Catalitico.objects.filter(Q(codigo__icontains=q)).values('id', 'codigo', 'descripcion', 'valor')[:10]
    resultados = [{
        'id': c['id'],
        'text': c['codigo'],
        'descripcion': c['descripcion'],
        'valor': c['valor']
    } for c in cataliticos]
    return JsonResponse({'results': resultados})

def api_verificar_codigo_unico(request):
    """API para verificar si un código de catalítico es único"""
    codigo = request.GET.get('codigo', '').strip().upper()
    catalitico_id = request.GET.get('id', None)  # Para excluir en caso de edición
    
    if not codigo:
        return JsonResponse({'error': 'Código no proporcionado'}, status=400)
    
    try:
        queryset = Catalitico.objects.filter(codigo=codigo)
        
        # Excluir el catalítico actual si estamos editando
        if catalitico_id:
            queryset = queryset.exclude(pk=int(catalitico_id))
        
        existe = queryset.exists()
        
        return JsonResponse({
            'codigo': codigo,
            'existe': existe,
            'mensaje': f'El código "{codigo}" ya está en uso' if existe else f'El código "{codigo}" está disponible'
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}'
        }, status=500)
    """API para obtener información de un catalítico por su código exacto"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({'error': 'Código no proporcionado'}, status=400)
    
    try:
        catalitico = Catalitico.objects.get(codigo__iexact=codigo)
        return JsonResponse({
            'success': True,
            'id': catalitico.id,
            'codigo': catalitico.codigo,
            'descripcion': catalitico.descripcion,
            'valor': catalitico.valor_actual or catalitico.valor,
            'precio_sugerido': catalitico.valor_actual or catalitico.valor
        })
    except Catalitico.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Catalítico con código "{codigo}" no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })

def api_verificar_eliminacion_catalitico(request, pk):
    """API para verificar si un catalítico puede ser eliminado"""
    try:
        catalitico = get_object_or_404(Catalitico, pk=pk)
        
        # Contar cuántas compras usan este catalítico
        compras_count = DetalleCatalitico.objects.filter(catalitico=catalitico).count()
        
        puede_eliminar = compras_count == 0
        
        return JsonResponse({
            'puede_eliminar': puede_eliminar,
            'compras_count': compras_count,
            'codigo': catalitico.codigo,
            'descripcion': catalitico.descripcion
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error al verificar: {str(e)}',
            'puede_eliminar': False,
            'compras_count': 0
        }, status=500)

def api_buscar_cliente(request):
    q = request.GET.get('term', '').strip()
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(rut__icontains=q)
    ).values('id', 'nombre', 'apellido', 'rut')[:10]
    resultados = [
        {'id': c['id'], 'text': f"{c['nombre']} {c['apellido']} ({c['rut']})".strip()}
        for c in clientes
    ]
    return JsonResponse({'results': resultados})

def test_template_tag(request):
    """Vista temporal para probar template tags"""
    return render(request, 'test_template_tag.html', {
        'none_value': None
    })

def api_dashboard_metrics(request):
    """API endpoint para métricas del dashboard en tiempo real"""
    from django.db.models import Sum, Count, Avg
    from django.http import JsonResponse
    
    try:
        metrics = {
            'total_cataliticos': Catalitico.objects.count(),
            'total_clientes': Cliente.objects.count(),
            'total_compras': CompraCatalitico.objects.count(),
            'valor_inventario': Catalitico.objects.aggregate(total=Sum('valor_actual'))['total'] or 0,
            'ventas_hoy': CompraCatalitico.objects.filter(fecha__date=now().date()).count(),
            'ingresos_hoy': sum([
                compra.total() for compra in 
                CompraCatalitico.objects.filter(fecha__date=now().date())
            ]),
            'timestamp': now().isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'metrics': metrics,
            'values': [
                metrics['total_cataliticos'],
                metrics['total_clientes'],
                metrics['total_compras'],
                metrics['valor_inventario']
            ]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json

@require_GET
def api_regiones_ciudades(request):
    """Devuelve las regiones y ciudades principales de Chile desde el archivo JSON."""
    with open('cataliticos/static/js/regiones_ciudades.json', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)