import math
import sys
import pygame

# Inicialización
pygame.init()
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Estilo DOOM Raycaster con Movimiento WASD Independiente")
RELOJ = pygame.time.Clock()

# Ocultar y capturar el cursor del mouse
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Mapa del juego (1 = Muro, 0 = Espacio vacío)
MAPA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Posición y ángulo inicial del jugador
px, py = 1.5, 1.5
angulo = 0.0
FOV = math.pi / 3  # Campo de visión (60 grados)
NUM_RAYOS = 120
DELTA_ANGULO = FOV / NUM_RAYOS
DISTANCIA_MAX = 16.0

def juego_principal():
    global px, py, angulo
    ejecutando = True

    while ejecutando:
        RELOJ.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # --- CÁMARA CON EL MOUSE ---
        rel_x, _ = pygame.mouse.get_rel()
        sensibilidad_mouse = 0.003
        angulo += rel_x * sensibilidad_mouse

        # --- MOVIMIENTO INDEPENDIENTE (WASD / Flechas) ---
        teclas = pygame.key.get_pressed()
        velocidad_movimiento = 0.045

        # Vectores base según hacia dónde mira la cámara
        cos_a = math.cos(angulo)
        sin_a = math.sin(angulo)

        dx, dy = 0.0, 0.0

        # W / S: Avanzar y retroceder en la dirección de la vista
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dx += cos_a * velocidad_movimiento
            dy += sin_a * velocidad_movimiento
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dx -= cos_a * velocidad_movimiento
            dy -= sin_a * velocidad_movimiento

        # A / D: Desplazamiento lateral (Strafe) perpendicular a la vista
        if teclas[pygame.K_d]:
            dx += -sin_a * velocidad_movimiento
            dy += cos_a * velocidad_movimiento
        if teclas[pygame.K_a]:
            dx -= -sin_a * velocidad_movimiento
            dy -= cos_a * velocidad_movimiento

        # Colisión con deslizamiento por ejes separados (evita atascos en esquinas)
        if MAPA[int(py)][int(px + dx)] == 0:
            px += dx
        if MAPA[int(py + dy)][int(px)] == 0:
            py += dy

        # Dibujar cielo y suelo
        VENTANA.fill((30, 30, 30), (0, 0, ANCHO, ALTO // 2))  # Cielo
        VENTANA.fill((80, 80, 80), (0, ALTO // 2, ANCHO, ALTO // 2))  # Suelo

        # --- MOTOR DE RAYCASTING ---
        angulo_rayo = angulo - FOV / 2
        ancho_columna = ANCHO / NUM_RAYOS

        for i in range(NUM_RAYOS):
            sen = math.sin(angulo_rayo)
            cos = math.cos(angulo_rayo)
            distancia = 0.0
            hit_muro = False

            while not hit_muro and distancia < DISTANCIA_MAX:
                distancia += 0.05
                test_x = int(px + cos * distancia)
                test_y = int(py + sen * distancia)

                if test_x < 0 or test_x >= len(MAPA[0]) or test_y < 0 or test_y >= len(MAPA):
                    hit_muro = True
                    distancia = DISTANCIA_MAX
                elif MAPA[test_y][test_x] == 1:
                    hit_muro = True

            # Corrección de efecto Ojo de Pez (Fish-eye)
            angulo_corr = angulo_rayo - angulo
            distancia = distancia * math.cos(angulo_corr)

            # Altura de la pared en pantalla
            altura_muro = min(int(ALTO / (distancia + 0.0001)), ALTO)
            y_inicio = (ALTO - altura_muro) // 2

            # Oscurecer muros según la distancia
            color_muro = max(20, min(255, int(255 - distancia * 15)))
            color = (color_muro, color_muro // 3, color_muro // 3)

            # Dibujar la franja vertical del muro
            pygame.draw.rect(VENTANA, color, (i * ancho_columna, y_inicio, ancho_columna + 1, altura_muro))

            angulo_rayo += DELTA_ANGULO

        pygame.display.flip()

if __name__ == "__main__":
    juego_principal()