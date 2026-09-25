def calcular_cuota(capital, tasa_anual, cantidad_cuota):
    if capital <= 0:
        raise ValueError("El capital debe ser mayor que cero.")
    if tasa_anual < 0:
        raise ValueError("La tasa anual no puede ser negativa.")
    if cantidad_cuota <= 0:
        raise ValueError("La cantidad de cuotas debe ser mayor que cero.")

    interes_total = capital * (tasa_anual / 100)
    monto_total = capital + interes_total
    cuota = monto_total / cantidad_cuota
    return cuota


def main():
    print("Calcular cuotas")
    try:
        capital = float(input("Ingrese el monto a prestar: "))
        tasa_anual = float(input("Ingrese la tasa anual (%): "))
        cantidad_cuotas = int(input("Ingrese la cantidad de cuotas: "))
        cuota = calcular_cuota(capital, tasa_anual, cantidad_cuotas)
    except ValueError as error:
        print(f"Entrada invalida: {error}")
        return

    print(f"Su cuota mensual sera de: ${cuota:.2f}")


if __name__ == "__main__":
    main()

