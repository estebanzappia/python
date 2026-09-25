def mostrar_pares(limite=100, destacado=64):
    """Muestra los numeros pares desde cero hasta limite, sin incluirlo."""
    if limite < 0:
        raise ValueError("El limite no puede ser negativo.")

    for numero in range(0, limite, 2):
        texto = f"***{numero}***" if numero == destacado else str(numero)
        print(f" | {texto}")


if __name__ == "__main__":
    mostrar_pares()