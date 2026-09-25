import os
from google import genai

class Chatbot:
    def __init__(self, nombre, api_key):
        self.nombre = nombre

       
        self.client = genai.Client(api_key=api_key)

        
        self.chat = self.client.chats.create(
            model="gemini-3.6-flash",
            config={
                "system_instruction": f"Eres {self.nombre}, un chatbot inteligente y servicial para el SNPP."
            }
        )

    def responder(self, mensaje):
        try:
            respuesta = self.chat.send_message(mensaje)
            return respuesta.text
        except Exception as e:
            return f"Lo siento, ocurrió un problema con la conexión a la IA: {e}"


def main():
    # Pega tu clave de formato nuevo directamente aquí 
    API_KEY = "AQ.Ab8RN6KbMbh8l5jQCLEHffV56hL4_5uMFDnsLj3CTlmexxvZww"

    bot = Chatbot("Asistente SNPP", API_KEY)
    print(f"{bot.nombre}: ¡Hola! Conectado con éxito a Gemini. Escribe 'salir' para terminar la conversación.")

    while True:
        entrada = input("Tú: ")
        if entrada.lower().strip() == "salir":
            print(f"{bot.nombre}: ¡Hasta pronto!")
            break

        if not entrada.strip():
            continue

        respuesta = bot.responder(entrada)
        print(f"{bot.nombre}: {respuesta}")


if __name__ == "__main__":
    main()
