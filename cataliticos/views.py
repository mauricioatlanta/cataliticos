from django.http import JsonResponse, HttpResponse
import csv
from .models import ProductoChatarra

def exportar_catalogo_json(request):
    productos = list(ProductoChatarra.objects.values("codigo", "nombre", "precio_kg", "categoria"))
    return JsonResponse(productos, safe=False)

def exportar_catalogo_csv(request):
    productos = ProductoChatarra.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="catalogo_chatarra.csv"'
    writer = csv.writer(response)
    writer.writerow(["Código", "Nombre", "Precio CLP/kg", "Categoría"])
    for p in productos:
        writer.writerow([p.codigo, p.nombre, p.precio_kg, p.categoria])
    return response
def bienvenida_chatarra(request):
    return render(request, 'chatarra/bienvenida.html')
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ProductoChatarra

def catalogo_chatarra(request):
    productos = ProductoChatarra.objects.all()
    return render(request, "chatarra/catalogo.html", {"productos": productos})
# Vista para marcar catalíticos como vendidos
@login_required
@require_POST
def marcar_vendido(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    catalitico.vendido = True
    catalitico.save()
    messages.success(request, f"Catalítico {catalitico.codigo} marcado como vendido.")
    return redirect('cataliticos:resumen_stock')
from decimal import Decimal, InvalidOperation
import logging
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .models import Catalitico, Cliente, CompraCatalitico, DetalleCatalitico, Region, Ciudad

# AJAX: Obtener ciudades por región
from django.views.decorators.http import require_GET, require_POST
@require_GET
def ajax_ciudades_por_region(request):
    region_id = request.GET.get('region_id')
    ciudades = []
    if region_id:
        ciudades = list(Ciudad.objects.filter(region_id=region_id).order_by('nombre').values('id', 'nombre'))
    return JsonResponse({'ciudades': ciudades})

# AJAX: Agregar nueva ciudad
@require_POST
def ajax_agregar_ciudad(request):
    region_id = request.POST.get('region_id')
    nombre = request.POST.get('nombre')
    if not (region_id and nombre):
        return JsonResponse({'ok': False, 'error': 'Datos incompletos'})
    region = Region.objects.filter(id=region_id).first()
    if not region:
        return JsonResponse({'ok': False, 'error': 'Región no encontrada'})
    ciudad, created = Ciudad.objects.get_or_create(nombre=nombre.strip(), region=region)
    return JsonResponse({'ok': True, 'ciudad': {'id': ciudad.id, 'nombre': ciudad.nombre}, 'nueva': created})
from .forms import CataliticoForm, ClienteForm, CompraForm, DetalleCataliticoFormSet

from django.contrib.auth.decorators import login_required

@login_required(login_url='cataliticos:employee_login')
def dashboard(request):
    from django.db.models import Sum, Avg, Max, Min, Count, Q
    from django.utils import timezone
    import json
    
    # Estadísticas generales
    total_cataliticos = Catalitico.objects.count()
    total_clientes = Cliente.objects.count()
    total_compras = CompraCatalitico.objects.count()
    valor_total_inventario = Catalitico.objects.aggregate(total=Sum('valor_venta'))['total'] or 0
    valor_promedio_catalitico = Catalitico.objects.aggregate(avg=Avg('valor_venta'))['avg'] or 0
    
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
        '0-10k': Catalitico.objects.filter(valor_venta__lt=10000).count(),
        '10k-25k': Catalitico.objects.filter(valor_venta__gte=10000, valor_venta__lt=25000).count(),
        '25k-50k': Catalitico.objects.filter(valor_venta__gte=25000, valor_venta__lt=50000).count(),
        '50k+': Catalitico.objects.filter(valor_venta__gte=50000).count(),
    }
    
    # Catalíticos más caros y más baratos
    catalitico_mas_caro = Catalitico.objects.order_by('-valor_venta').first()
    catalitico_mas_barato = Catalitico.objects.order_by('valor_venta').first()
    
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


@login_required(login_url='cataliticos:employee_login')
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

@login_required(login_url='cataliticos:employee_login')
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


@login_required(login_url='cataliticos:employee_login')
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

@login_required(login_url='cataliticos:employee_login')
def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cataliticos:crear_compra_multiple')
    return render(request, 'cataliticos/crear_cliente.html', {'form': form})

@login_required(login_url='cataliticos:employee_login')
def clientes_listado(request):
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(
            models.Q(nombre__icontains=q) |
            models.Q(apellido__icontains=q) |
            models.Q(rut__icontains=q)
        )
    return render(request, 'cataliticos/clientes_listado.html', {'clientes': clientes})

@login_required(login_url='cataliticos:employee_login')
def ver_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'cataliticos/ver_cliente.html', {'cliente': cliente})

@login_required(login_url='cataliticos:employee_login')
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('cataliticos:clientes_listado')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cataliticos/editar_cliente.html', {'form': form, 'cliente': cliente})

@login_required(login_url='cataliticos:employee_login')
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('cataliticos:clientes_listado')
    return render(request, 'cataliticos/eliminar_cliente.html', {'cliente': cliente})
def crear_compra_multiple(request):
    cataliticos = Catalitico.objects.all()
    cliente = None
    cliente_nombre = ''
    cliente_apellido = ''
    cliente_rut = ''
    cliente_telefono = ''
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
            cliente_nombre = cliente.nombre
            cliente_apellido = cliente.apellido

    logger = logging.getLogger("django")
    if request.method == 'POST':
        logger.info("POST recibido en crear_compra_multiple")
        logger.info(f"POST data: {request.POST}")

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

    logger.info("Cliente: %s, Nombre: %s, Apellido: %s, Rut: %s, Telefono: %s", cliente, cliente_nombre, cliente_apellido, cliente_rut, cliente_telefono)

    compra = CompraCatalitico.objects.create(
        cliente=cliente,
        cliente_nombre=cliente_nombre or "",
        cliente_apellido=cliente_apellido or "",
        cliente_rut=cliente_rut or "",
        cliente_telefono=cliente_telefono or "",
        region=request.POST.get("region") or "",
        ciudad=request.POST.get("ciudad") or "",
    )

    logger.info(f"Compra creada: {compra}")

    codigos = request.POST.getlist('codigo[]')
    cantidades = request.POST.getlist('cantidad[]')
    valores = request.POST.getlist('valor_unitario[]')

    logger.info(f"Codigos: {codigos}")
    logger.info(f"Cantidades: {cantidades}")
    logger.info(f"Valores: {valores}")

    detalles_guardados = 0
    for codigo, cantidad_str, valor_str in zip(codigos, cantidades, valores):
        codigo = codigo.strip()
        if not codigo or not cantidad_str or not valor_str:
            continue  # omitir líneas vacías

        try:
            catalitico = Catalitico.objects.get(codigo__iexact=codigo)
        except Catalitico.DoesNotExist:
            continue  # omitir si el código no existe

        try:
            cantidad = Decimal(cantidad_str)
            precio_unitario = Decimal(valor_str)
        except Exception:
            continue  # omitir si valores no son válidos

        DetalleCatalitico.objects.create(
            compra=compra,
            catalitico=catalitico,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        detalles_guardados += 1

    if detalles_guardados == 0:
        compra.delete()
        messages.error(request, "❌ Debes ingresar al menos un catalítico válido para guardar la compra.")
        return render(request, 'cataliticos/crear_compra_multiple.html', {'cataliticos': Catalitico.objects.all()})

    messages.success(request, f"✅ Compra creada con {detalles_guardados} catalítico(s).")
    return redirect('cataliticos:listado_compras')

    # Si es GET o POST inválido, mostrar el formulario vacío
    return render(request, 'cataliticos/crear_compra_multiple.html', {
        'cataliticos': Catalitico.objects.all(),
    })
    logger = logging.getLogger("django")
    if request.method == 'POST':
        logger.info("POST recibido en crear_compra_multiple")
        logger.info(f"POST data: {request.POST}")

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

        logger.info("Cliente: %s, Nombre: %s, Apellido: %s, Rut: %s, Telefono: %s", cliente, cliente_nombre, cliente_apellido, cliente_rut, cliente_telefono)

        compra = CompraCatalitico.objects.create(
            cliente=cliente,
            cliente_nombre=cliente_nombre or "",
            cliente_apellido=cliente_apellido or "",
            cliente_rut=cliente_rut or "",
            cliente_telefono=cliente_telefono or "",
            region=request.POST.get("region") or "",
            ciudad=request.POST.get("ciudad") or "",
        )

        logger.info(f"Compra creada: {compra}")

        codigos = request.POST.getlist('codigo[]')
        cantidades = request.POST.getlist('cantidad[]')
        valores = request.POST.getlist('valor_unitario[]')

        logger.info(f"Codigos: {codigos}")
        logger.info(f"Cantidades: {cantidades}")
        logger.info(f"Valores: {valores}")

        detalles_guardados = 0
        for codigo, cantidad_str, valor_str in zip(codigos, cantidades, valores):
            codigo = codigo.strip()
            if not codigo or not cantidad_str or not valor_str:
                continue  # omitir líneas vacías

            try:
                catalitico = Catalitico.objects.get(codigo__iexact=codigo)
            except Catalitico.DoesNotExist:
                continue  # omitir si el código no existe

            try:
                cantidad = Decimal(cantidad_str)
                precio_unitario = Decimal(valor_str)
            except Exception:
                continue  # omitir si valores no son válidos

            DetalleCatalitico.objects.create(
                compra=compra,
                catalitico=catalitico,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            detalles_guardados += 1

        if detalles_guardados == 0:
            compra.delete()
            messages.error(request, "❌ Debes ingresar al menos un catalítico válido para guardar la compra.")
            return render(request, 'cataliticos/crear_compra_multiple.html', {'cataliticos': Catalitico.objects.all()})

        messages.success(request, f"✅ Compra creada con {detalles_guardados} catalítico(s).")
        return redirect('cataliticos:listado_compras')

@login_required(login_url='cataliticos:employee_login')
def listado_compras(request):
    compras = CompraCatalitico.objects.order_by('-fecha')
    return render(request, 'cataliticos/listado_compras.html', {'compras': compras})

def editar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    form = CompraForm(request.POST or None, instance=compra)
    formset = DetalleCataliticoFormSet(request.POST or None, instance=compra)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "✅ La compra se actualizó correctamente.")
            return redirect('cataliticos:listado_compras')

    return render(request, 'cataliticos/editar_compra.html', {
        'form': form,
        'formset': formset,
        'compra': compra,
    })

@login_required(login_url='cataliticos:employee_login')
def eliminar_compra(request, pk):
    compra = get_object_or_404(CompraCatalitico, pk=pk)
    compra.delete()
    return redirect('cataliticos:listado_compras')

def api_buscar_catalitico(request):
    # Permite buscar por código exacto (param: codigo) o búsqueda rápida (param: term)
    from django.conf import settings
    import os
    import glob
    codigo = request.GET.get('codigo', '').strip()
    term = request.GET.get('term', '').strip()
    if codigo:
        try:
            catalitico = Catalitico.objects.get(codigo__iexact=codigo)
            imagenes = []
            campos_imagen = ['imagen_principal', 'imagen2', 'imagen3', 'imagen4']
            for campo in campos_imagen:
                img_field = getattr(catalitico, campo, None)
                if img_field and hasattr(img_field, 'url') and img_field.url:
                    imagenes.append(img_field.url)
            # Respuesta plana para JS del formulario de compras
            return JsonResponse({
                'success': True,
                'id': catalitico.pk,
                'codigo': catalitico.codigo,
                'descripcion': catalitico.descripcion,
                'valor': float(catalitico.valor_compra),
                'valor_venta': float(catalitico.valor_venta) if catalitico.valor_venta else None,
                'imagenes': imagenes
            })
        except Catalitico.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No existe catalítico con ese código.'})
    elif term:
        cataliticos = Catalitico.objects.filter(codigo__icontains=term).values('id', 'codigo', 'descripcion', 'valor_compra')[:10]
        resultados = [
            {
                'id': c['id'],
                'text': c['codigo'],
                'descripcion': c['descripcion'],
                'valor': c['valor_compra']
            }
            for c in cataliticos
            if term.lower() in c['codigo'].lower()
        ]
        return JsonResponse({'results': resultados})
    else:
        return JsonResponse({'success': False, 'error': 'Debe proporcionar un código o término de búsqueda.'})

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
    if q:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(rut__icontains=q)
        ).values('id', 'nombre', 'apellido', 'rut')[:20]
    else:
        clientes = Cliente.objects.all().order_by('nombre').values('id', 'nombre', 'apellido', 'rut')[:20]
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

def consulta_catalitico(request):
    """
    Vista solo lectura para consulta de precio y detalles de catalíticos por código.
    No muestra navegación ni permite editar/agregar/borrar.
    """
    return render(request, 'consulta_catalitico.html')

def detalle_catalitico(request, pk):
    catalitico = get_object_or_404(Catalitico, pk=pk)
    return render(request, 'cataliticos/detalle.html', {'catalitico': catalitico})

def chatarra_electronica(request):
    # Mostrar el catálogo de productos chatarra
    productos = ProductoChatarra.objects.all()
    return render(request, 'chatarra/catalogo.html', {'productos': productos})

def bienvenida_atlanta(request):
    """
    Página de bienvenida corporativa de Atlanta Reciclajes.
    """
    return render(request, 'bienvenida_atlanta.html')

# ============================================================================
# SISTEMA DE AUTENTICACIÓN DE EMPLEADOS
# ============================================================================

def employee_login(request):
    """
    Vista de login para empleados con formulario de autenticación.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido, {username}!')
                # Redirigir a la página solicitada o al dashboard
                next_page = request.GET.get('next', reverse('cataliticos:dashboard'))
                return redirect(next_page)
            else:
                messages.error(request, 'Credenciales incorrectas.')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def employee_logout(request):
    """
    Vista de logout para empleados.
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    # Redirigir a la página principal pública (index.html)
    return redirect('cataliticos:catalíticos_home')

def password_reset_request(request):
    """
    Vista para solicitar recuperación de contraseña.
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'No existe un usuario con este email.')
            else:
                # Generar token de recuperación
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # Crear enlace de recuperación
                current_site = get_current_site(request)
                reset_url = f"http://{current_site.domain}/cataliticos/reset-password/{uid}/{token}/"
                # Enviar email (simulado - en producción usar configuración real de email)
                subject = 'Recuperación de contraseña - Atlanta Reciclajes'
                message = f"""
                Hola {user.username},

                Hemos recibido una solicitud para restablecer tu contraseña en Atlanta Reciclajes.
                
                Para restablecer tu contraseña, haz clic en el siguiente enlace:
                {reset_url}
                
                Si no solicitaste este cambio, puedes ignorar este mensaje.
                
                Atentamente,
                El equipo de Atlanta Reciclajes
                """
                # En desarrollo, solo mostrar el mensaje
                messages.success(request, f'Se ha enviado un enlace de recuperación a tu email. (Desarrollo: {reset_url})')
                # En producción, descomentar esta línea:
                # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        else:
            messages.error(request, 'Por favor, ingresa un email válido.')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    """
    Vista para confirmar el restablecimiento de contraseña.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password and new_password == confirm_password:
                if len(new_password) >= 8:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Tu contraseña ha sido restablecida exitosamente.')
                    return redirect('cataliticos:employee_login')
                else:
                    messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
        
        return render(request, 'registration/password_reset_confirm.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, 'El enlace de recuperación no es válido o ha expirado.')
        return render(request, 'registration/password_reset_confirm.html', {'validlink': False})

@login_required
def resumen_stock(request):
    stock = Catalitico.objects.filter(vendido=False)
    total_invertido = sum((c.valor_compra or 0) * (c.cantidad or 0) for c in stock)
    total_venta = sum((c.valor_venta or 0) * (c.cantidad or 0) for c in stock)
    ganancia_esperada = total_venta - total_invertido
    return render(request, 'cataliticos/resumen_stock.html', {
        'stock': stock,
        'total_invertido': total_invertido,
        'total_venta': total_venta,
        'ganancia_esperada': ganancia_esperada
    })