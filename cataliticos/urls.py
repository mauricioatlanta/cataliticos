from django.urls import path
from . import views
from .views import inicio, buscar_codigo

urlpatterns = [
    path('', inicio, name='inicio'),
    path('buscar/', buscar_codigo, name='buscar_codigo'),
   
]
