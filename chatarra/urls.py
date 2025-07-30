from django.urls import path
from . import views

from . import api_views

urlpatterns = [
    path('catalogo/', views.catalogo_chatarra, name='catalogo_chatarra'),
    path('api/catalogo/', api_views.CatalogoChatarraAPI.as_view(), name='api_catalogo_chatarra'),
]
