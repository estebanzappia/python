from django.contrib import admin
from django.urls import path
from .views import listar, saludar, inicio, sumar, saludar_nombre, factorial, tabla, par_impar, inicio_render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mostrar/', listar),
    path('saludar/', saludar),
    path('', inicio),
    path('sumar/', sumar),
    path('saludar/<str:nombre>/', saludar_nombre),
    path('factorial/<int:numero>/', factorial),
    path('tabla/<int:numero>/', tabla),
    path('parimpar/<int:numero>/', par_impar),
    path('ver/', inicio_render)
]