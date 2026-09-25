from django.urls import path
from . import views

urlpatterns = [
    path('', views.productos_index, name='productos_index'),
    path('crear/', views.productos_crear, name='productos_crear'),
    path('editar/<int:id>/', views.productos_editar, name='productos_editar'),
    path('eliminar/<int:id>/', views.productos_eliminar, name='productos_eliminar'),
]