from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_codigo, name='buscar_codigo'),
]
