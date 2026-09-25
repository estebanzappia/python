from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto

def productos_index(request):
    productos = Producto.objects.all()
    return render(request, 'productos/index.html', {'productos': productos})

def productos_crear(request):
    if request.method == 'POST':
        codigo_barra = request.POST.get('codigo_barra')
        descripcion = request.POST.get('descripcion')
        precio_costo = request.POST.get('precio_costo')
        precio_venta = request.POST.get('precio_venta')
        iva = request.POST.get('iva')
        stock = request.POST.get('stock')
        unidad_medida = request.POST.get('unidad_medida')
        
        Producto.objects.create(
            codigo_barra=codigo_barra,
            descripcion=descripcion,
            precio_costo=precio_costo,
            precio_venta=precio_venta,
            iva=iva,
            stock=stock,
            unidad_medida=unidad_medida
        )
        return redirect('productos_index')
    return redirect('productos_index')

def productos_editar(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.codigo_barra = request.POST.get('codigo_barra')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio_costo = request.POST.get('precio_costo')
        producto.precio_venta = request.POST.get('precio_venta')
        producto.iva = request.POST.get('iva')
        producto.stock = request.POST.get('stock')
        producto.unidad_medida = request.POST.get('unidad_medida')
        producto.save()
        return redirect('productos_index')
    
    return render(request, 'productos/editar.html', {'producto': producto})

def productos_eliminar(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('productos_index')