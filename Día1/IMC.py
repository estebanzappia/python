"""Calcula el indice de masa corporal."""


def calcular_imc(peso, estatura):
    """Devuelve el IMC a partir del peso en kg y la estatura en metros."""
    if peso <= 0 or estatura <= 0:
        raise ValueError("El peso y la estatura deben ser mayores que cero.")
    return peso / estatura ** 2


def main():
    print("Calculadora de IMC")
    try:
        peso = float(input("Ingrese su peso en kg: "))
        estatura = float(input("Ingrese su estatura en metros: "))
        imc = calcular_imc(peso, estatura)
    except ValueError as error:
        print(f"Entrada invalida: {error}")
        return

    print(f"Su IMC es: {imc:.2f}")


if __name__ == "__main__":
    main()