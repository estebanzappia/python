sucursal_a =(-25.2637, -57.59)
sucursal_b =(-25.2968, -57.6350)

lat_a, lon_a = sucursal_a
lat_b, lon_b = sucursal_b

distancia = ((lat_b - lat_a)**2 + (lon_b - lon_a)**2)**(0.5)
print(f"Distancia entre sucursales: {distancia:.2f} grados")