producto = {
    "nombre" : "Arroz 1 Kg",
    "precio" : 6500,
    "stock"  : 120
}

cantidad_vendida = 15
producto["stock"] = producto["stock"] - cantidad_vendida
total = producto["precio"] * cantidad_vendida

print (f"Venta registrada: {cantidad_vendida} de unid. de {producto["nombre"]}")
print (f"Monto total: {total} guaraníes")
print (f"Stock restante: {producto["stock"]} unidades.")
