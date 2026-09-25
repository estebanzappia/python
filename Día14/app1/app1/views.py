from django.http import HttpResponse
from django.shortcuts import render

lista = ["fiorella", "camila", "vanessa", "sofia"]

def listar(request):
    texto = "<ul>" + "".join(f"<li>{nombre}</li>" for nombre in lista) + "</ul>"
    return HttpResponse(texto)

def saludar(request):
    texto = f'Hola, cómo estas?'
    return HttpResponse(texto)

def inicio(request):
    return HttpResponse("<h1>Bienvenido a mi página</h1><p>Este es el inicio del sitio.</p>")

def sumar(request):
    a = 10
    b = 5
    resultado = a + b

    return HttpResponse(f"<h2>La suma de {a} + {b} es {resultado}</h2>")

def saludar_nombre(request, nombre):
    return HttpResponse(f"<h2>Hola, {nombre}! Bienvenido.</h2>")

def factorial(request, numero):
    resultado = 1
    for i in range(1, numero + 1):
        resultado = resultado * i
    return HttpResponse(f"El factorial de {numero} es {resultado}")

def tabla(request, numero):
    texto = ""
    for i in range(1, 11):
        resultado = numero * i
        texto += f"{numero} x {i} = {resultado}<br>"
    return HttpResponse(texto)

def par_impar(request, numero):
    if numero % 2 == 0:
        return HttpResponse(f"{numero} es par")
    else:
        return HttpResponse(f"{numero} es impar")


def inicio_render(request):
    return render(request, 'app1/inicio.html')