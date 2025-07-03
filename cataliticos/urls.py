from django.urls import path
from . import views

app_name = 'cataliticos'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/cliente/', views.api_buscar_cliente, name='api_buscar_cliente'),
    path('api/catalitico/', views.api_buscar_catalitico, name='api_buscar_catalitico'),
    # path('api/catalitico-codigo/', views.api_obtener_catalitico_por_codigo, name='api_obtener_catalitico_por_codigo'),
    path('api/verificar-codigo/', views.api_verificar_codigo_unico, name='api_verificar_codigo_unico'),
    path('api/verificar-eliminacion/<int:pk>/', views.api_verificar_eliminacion_catalitico, name='api_verificar_eliminacion'),
    path('api/dashboard-metrics/', views.api_dashboard_metrics, name='api_dashboard_metrics'),
    path('api/regiones-ciudades/', views.api_regiones_ciudades, name='api_regiones_ciudades'),
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),
    path('compra/', views.crear_compra_multiple, name='crear_compra_multiple'),
    path('compras/', views.listado_compras, name='listado_compras'),
    path('compras/editar/<int:pk>/', views.editar_compra, name='editar_compra'),
    path('compras/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    path('listado/', views.listado_y_busqueda, name='listado'),
    path('crear/', views.crear_catalitico, name='crear'),
    path('editar/<int:pk>/', views.editar_catalitico, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_catalitico, name='eliminar'),
]
