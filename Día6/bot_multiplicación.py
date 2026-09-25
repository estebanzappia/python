import random

puntaje = 0

for pregunta in range(5):
    num1 = random.randint(1,10)
    num2 = random.randint(1,10)

    respuesta = int(input(f"Cuanto es:{num1} x {num2}?"))

    if respuesta == num1 * num2:
        print("Excelente")
        puntaje +=1
    else:
        print("Ops, fallaste")

print(f"Acertaste {puntaje} de 5")
if(puntaje < 3):
    print("Debes practicar mucho más")
elif(puntaje < 5):
    print("Eres bueno, pero falta prácticar un poco más")
else:
    print("Eres genial con las multiplicaciones")
