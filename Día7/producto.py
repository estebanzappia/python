class Producto:
    nombre = None

    def __init__(self,n):
        self.nombre = n

    def ver_datos(self):
        return f"Producto {self.nombre}"


#crear objeto
p1 = Producto("computadora")

print(p1.ver_datos())