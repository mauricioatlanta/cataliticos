from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'cataliticos'

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name="catalíticos_home"),
    
    # Rutas de autenticación
    path('login/', views.employee_login, name='employee_login'),
    path('logout/', views.employee_logout, name='employee_logout'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Rutas protegidas (requieren login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('listado/', views.listado_y_busqueda, name='listado'),
    path('crear/', views.crear_catalitico, name='crear'),
    path('editar/<int:pk>/', views.editar_catalitico, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_catalitico, name='eliminar'),
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),
    path('compra/', views.crear_compra_multiple, name='crear_compra_multiple'),
    path('compras/', views.listado_compras, name='listado_compras'),
    path('compras/editar/<int:pk>/', views.editar_compra, name='editar_compra'),
    path('compras/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    
    # APIs
    path('api/cliente/', views.api_buscar_cliente, name='api_buscar_cliente'),
    path('api/catalitico/', views.api_buscar_catalitico, name='api_buscar_catalitico'),
    path('api/verificar-codigo/', views.api_verificar_codigo_unico, name='api_verificar_codigo_unico'),
    path('api/verificar-eliminacion/<int:pk>/', views.api_verificar_eliminacion_catalitico, name='api_verificar_eliminacion'),
    path('api/dashboard-metrics/', views.api_dashboard_metrics, name='api_dashboard_metrics'),
    path('api/regiones-ciudades/', views.api_regiones_ciudades, name='api_regiones_ciudades'),
    
    # Páginas públicas
    path('consulta-catalitico/', views.consulta_catalitico, name='consulta_catalitico'),
    path('detalle/<int:pk>/', views.detalle_catalitico, name='detalle'),
    path('bienvenida-atlanta/', views.bienvenida_atlanta, name='bienvenida_atlanta'),
    path('chatarra-electronica/', views.chatarra_electronica, name='chatarra_electronica'),
]
