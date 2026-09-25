from math import isqrt


def es_primo(numero):
    """Indica si un numero es primo usando divisores hasta su raiz cuadrada."""
    if numero < 2:
        return False
    if numero % 2 == 0:
        return numero == 2

    for divisor in range(3, isqrt(numero) + 1, 2):
        if numero % divisor == 0:
            return False
    return True


def primos_desde(inicio, cantidad):
    """Devuelve una lista con una cantidad de primos desde inicio en adelante."""
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    encontrados = []
    candidato = max(2, inicio)
    while len(encontrados) < cantidad:
        if es_primo(candidato):
            encontrados.append(candidato)
        candidato += 1
    return encontrados


def main():
    print("Busqueda de numeros primos")
    try:
        inicio = int(input("Buscar desde (por defecto 2): ") or "2")
        cantidad = int(input("Cantidad de primos: "))
        encontrados = primos_desde(inicio, cantidad)
    except ValueError as error:
        print(f"Entrada invalida: {error}")
        return

    print("Primos encontrados:", ", ".join(map(str, encontrados)))


if __name__ == "__main__":
    main()