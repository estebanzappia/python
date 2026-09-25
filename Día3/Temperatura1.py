def indicar_climatizacion(temperatura):
    """Devuelve la accion recomendada para una temperatura."""
    if temperatura >= 28:
        return "Encender AA"
    if temperatura <= 17:
        return "Encender calefaccion"
    return "Temperatura agradable"


def main():
    print("Control de temperatura (ingrese 0 o menos para salir)")
    while True:
        try:
            temperatura = float(input("Ingrese temperatura: "))
        except ValueError:
            print("Entrada invalida: ingrese un numero.")
            continue

        if temperatura <= 0:
            print("Programa finalizado.")
            break
        print(indicar_climatizacion(temperatura))


if __name__ == "__main__":
    main()