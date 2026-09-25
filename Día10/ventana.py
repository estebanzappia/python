import tkinter as tk

def ejecutar():
    os.system(campo.get())
    

ventana = tk.Tk()
ventana.title("Saludo")
ventana.geometry("300x150")

campo = tk.Entry(ventana)
campo.pack(pady=10)


boton = tk.Button(ventana, text="Aceptar", command=ejecutar)
boton.pack(pady=5)

etiqueta = tk.Label(ventana, text="")
etiqueta.pack(pady=5)

ventana.mainloop()