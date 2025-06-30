from django.urls import path
from . import views
from . import views_compras

app_name = 'cataliticos'

urlpatterns = [
    urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/cliente/', views.api_buscar_cliente, name='api_buscar_cliente'),
    path('api/catalitico/', views.api_buscar_catalitico, name='api_buscar_catalitico'),
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),
    path('compra/', views.crear_compra_multiple, name='crear_compra_multiple'),
    path('compra-multiple/', views.crear_compra_multiple, name='compra_multiple'),
    path('compras/', views.listado_compras, name='listado_compras'),  # solo una vez
    path('compras/editar/<int:pk>/', views.editar_compra, name='editar_compra'),
    path('compras/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    path('listado/', views.listado_y_busqueda, name='listado'),
    path('crear/', views.crear_catalitico, name='crear'),
    path('editar/<int:pk>/', views.editar_catalitico, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_catalitico, name='eliminar'),
]

    

]
