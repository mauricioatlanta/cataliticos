from django.urls import path
from . import views
from . import views_compras

app_name = 'cataliticos'

urlpatterns = [

    # 🔹 Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # 🔹 Catálogo / Búsqueda
    path('listado/', views.listado_y_busqueda, name='listado'),
    path('crear/', views.crear_catalitico, name='crear'),
    path('editar/<int:pk>/', views.editar_catalitico, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_catalitico, name='eliminar'),

    # 🔹 Cliente
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),

    # 🔹 Compras
    path('compra/', views.crear_compra_multiple, name='crear_compra_multiple'),
    path('compras/', views_compras.listado_compras, name='listado_compras'),
    path('compras/editar/<int:pk>/', views_compras.editar_compra, name='editar_compra'),
    path('compras/eliminar/<int:pk>/', views_compras.eliminar_compra, name='eliminar_compra'),

    # 🔹 APIs públicas (Autocompletado)
    path('api/cliente/', views.api_buscar_cliente, name='api_buscar_cliente'),
    path('api/catalitico/', views.api_buscar_catalitico, name='api_buscar_catalitico'),

    # 🔹 Página principal
    path('', views.listado_y_busqueda, name='home'),
]
