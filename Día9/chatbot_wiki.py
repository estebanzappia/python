import wikipedia  


wikipedia.set_lang("es")


class Chatbot:

    def __init__(self, nombre):
        self.nombre = nombre
        self.base_conocimiento = {
            "hola": "¡Hola! ¿En qué puedo ayudarte?",
        }
        self.historial = []

    def responder(self, mensaje):
        mensaje = mensaje.lower().strip()
        self.historial.append(mensaje)

        
        for clave, respuesta in self.base_conocimiento.items():
            if clave in mensaje:
                return respuesta

        
        try:
            resumen = wikipedia.summary(mensaje, sentences=2)
            return f"Según Wikipedia: {resumen}"
        except wikipedia.exceptions.DisambiguationError:
            return "Tu búsqueda es muy ambigua, ¿puedes ser más específico?"
        except wikipedia.exceptions.PageNotFoundError:
            return (
                "No encontré información sobre eso en Wikipedia ni en mi base"
                " de datos."
            )
        except Exception:
            return "No entendí tu mensaje, o no tengo acceso a internet. ¿podrías reformularlo?."

    def agregar_conocimiento(self, clave, respuesta):
        self.base_conocimiento[clave.lower()] = respuesta


def main():
    bot = Chatbot("Asistente SNPP")
    print(
        f"{bot.nombre}: ¡Hola! Escribe 'salir' para terminar la conversación."
    )

    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            print(f"{bot.nombre}: ¡Hasta pronto!")
            break

        respuesta = bot.responder(entrada)
        print(f"{bot.nombre}: {respuesta}")


if __name__ == "__main__":
    main()


