class Chatbot:
    def __init__(self, nombre):
        self.nombre = nombre
        self.base_conocimiento = {
    
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "adios": "¡Hasta luego, que tengas un buen día!",
    "como estas": "Estoy funcionando correctamente, gracias por preguntar.",
    "quien eres": "Soy un chatbot creado para practicar POO en Python."
    }
        self.historial = []

    def responder(self, mensaje):
        mensaje = mensaje.lower().strip()
        self.historial.append(mensaje)

        for clave, respuesta in self.base_conocimiento.items():
            if clave in mensaje:
                return respuesta

        return "No entendí tu mensaje, ¿podrías reformularlo?"

    def agregar_conocimiento(self, clave, respuesta):
        self.base_conocimiento[clave.lower()] = respuesta

def main():
    bot = Chatbot("Asistente SNPP")
    print(f"{bot.nombre}: ¡Hola! Escribe 'salir' para terminar la conversación.")

    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            print(f"{bot.nombre}: ¡Hasta pronto!")
            break

        respuesta = bot.responder(entrada)
        print(f"{bot.nombre}: {respuesta}")


if __name__ == "__main__":
    main()
