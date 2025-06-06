from django.urls import path
from . import views

app_name = 'cataliticos'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('editar/<int:pk>/', views.editar_catalitico, name='editar'),
    path('', views.listado, name='listado'),
    path('listado/', views.listado_y_busqueda, name='listado'),
    path('buscar/', views.buscar_codigo, name='buscar'),
    path('crear/', views.crear_catalitico, name='crear'),
    path('comprar/<int:pk>/', views.comprar, name='comprar'),
    path('compra/', views.compra, name='compra'),
]
