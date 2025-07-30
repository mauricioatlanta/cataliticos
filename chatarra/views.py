from django.shortcuts import render
from django.core.paginator import Paginator
from cataliticos.models import ProductoChatarra

def catalogo_chatarra(request):
    productos = ProductoChatarra.objects.all().order_by("nombre")
    paginator = Paginator(productos, 12)  # 12 por página
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "chatarra/catalogo.html", {"page_obj": page_obj})
