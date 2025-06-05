
from django.contrib import admin
from django.urls import path
from cataliticos import views

urlpatterns = [
    path('', views.buscar_codigo, name='buscar_codigo'),
    path('admin/', admin.site.urls),
]
