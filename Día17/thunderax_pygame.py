"""
================================================================================
 SPACE RAIDER - Shoot 'em up estilo Thunderax (vista vertical)
================================================================================
Versión avanzada pulida con:
    - Menú principal interactivo (teclado + mouse)
    - Selección de nave (3 naves con estadísticas distintas)
    - Enemigos variados y Jefe Final con barra de vida
    - Tabla de puntuaciones máximas persistente (JSON)
    - Efectos visuales avanzados: Destellos (flash) y Sistema de Partículas
    - Arma especial de emergencia: Bombas inteligentes (Tecla X)

Controles:
    - Menús: flechas ARRIBA/ABAJO + ENTER, o clic con el mouse
    - En juego: flechas para mover, ESPACIO para disparar, X para Bomba
    - ESC: volver / salir según el contexto
    - En Game Over: R = reintentar, M = volver al menú

Requisitos: pip install pygame
================================================================================
"""

import pygame
import random
import sys
import os
import json
import math

# ============================================================================
# CONFIGURACIÓN GENERAL
# ============================================================================
ANCHO_VENTANA = 480
ALTO_VENTANA = 640
FPS = 60

# Colores (R, G, B)
NEGRO = (5, 5, 15)
BLANCO = (255, 255, 255)
GRIS = (120, 120, 130)
GRIS_OSCURO = (60, 60, 70)
AZUL_CLARO = (150, 220, 255)
VERDE_LASER = (80, 255, 120)
ROJO_ENEMIGO = (230, 60, 60)
NARANJA_ENEMIGO = (255, 140, 40)
AMARILLO = (255, 220, 60)
ROJO_EXPLOSION = (255, 100, 0)
MORADO_JEFE = (170, 80, 220)
BALA_ENEMIGA_COLOR = (255, 80, 80)
VERDE_VIDA = (80, 220, 100)
ROJO_VIDA = (220, 60, 60)
COLOR_BOMBA = (0, 255, 255)

# Parámetros de juego
VELOCIDAD_BALA_JUGADOR = 10
VELOCIDAD_BALA_ENEMIGA = 5
INTERVALO_SPAWN_ENEMIGO = 900
PUNTOS_PRIMER_JEFE = 300
INCREMENTO_PUNTOS_JEFE = 500
ARCHIVO_PUNTUACIONES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")
MAX_PUNTUACIONES_GUARDADAS = 8

# Estados posibles del juego
ESTADO_MENU = "menu"
ESTADO_SELECCION_NAVE = "seleccion_nave"
ESTADO_PUNTUACIONES = "puntuaciones"
ESTADO_JUGANDO = "jugando"
ESTADO_GAMEOVER = "gameover"

# ----------------------------------------------------------------------------
# CATÁLOGO DE NAVES JUGABLES
# ----------------------------------------------------------------------------
NAVES = {
    "interceptor": {
        "nombre": "Interceptor",
        "color_principal": (60, 180, 255),
        "color_secundario": AZUL_CLARO,
        "velocidad": 8,
        "vida_max": 2,
        "cooldown_disparo": 150,
        "danio_bala": 1,
        "patron_disparo": "simple",
        "ancho_nave": 32,
        "descripcion": "Muy ágil y veloz, pero frágil. Dispara rápido y solo.",
    },
    "acorazado": {
        "nombre": "Acorazado",
        "color_principal": ROJO_ENEMIGO,
        "color_secundario": (255, 160, 160),
        "velocidad": 4,
        "vida_max": 5,
        "cooldown_disparo": 380,
        "danio_bala": 2,
        "patron_disparo": "abanico",
        "ancho_nave": 50,
        "descripcion": "Lento y pesado, resiste mucho. Dispara en abanico (3).",
    },
    "equilibrada": {
        "nombre": "Equilibrada",
        "color_principal": (120, 220, 120),
        "color_secundario": (200, 255, 200),
        "velocidad": 6,
        "vida_max": 3,
        "cooldown_disparo": 220,
        "danio_bala": 1,
        "patron_disparo": "doble",
        "ancho_nave": 40,
        "descripcion": "Estadísticas balanceadas. Dispara dos láseres paralelos.",
    },
}
ORDEN_NAVES = ["interceptor", "equilibrada", "acorazado"]


# ============================================================================
# UTILIDAD: Gestor de puntuaciones máximas (persistencia en JSON)
# ============================================================================
class GestorPuntuaciones:
    def __init__(self, ruta_archivo=ARCHIVO_PUNTUACIONES):
        self.ruta_archivo = ruta_archivo

    def cargar(self):
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if isinstance(datos, list):
                    return sorted([int(p) for p in datos], reverse=True)
        except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
            pass
        return []

    def guardar(self, lista_puntuaciones):
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(lista_puntuaciones, f)
        except OSError:
            pass

    def agregar_puntuacion(self, puntos):
        puntuaciones = self.cargar()
        puntuaciones.append(puntos)
        puntuaciones.sort(reverse=True)
        puntuaciones = puntuaciones[:MAX_PUNTUACIONES_GUARDADAS]
        self.guardar(puntuaciones)
        return puntos in puntuaciones and puntos == max(puntuaciones)


# ============================================================================
# CLASE: Estrella (fondo animado)
# ============================================================================
class Estrella:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.x = random.randint(0, ancho)
        self.y = random.randint(0, alto)
        self.velocidad = random.uniform(1, 4)
        self.radio = 1 if self.velocidad < 2.5 else 2
        brillo = int(120 + (self.velocidad / 4) * 135)
        self.color = (brillo, brillo, brillo)

    def actualizar(self):
        self.y += self.velocidad
        if self.y > self.alto:
            self.y = 0
            self.x = random.randint(0, self.ancho)

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), self.radio)


# ============================================================================
# CLASE: Particula (para el sistema avanzado de explosiones y destellos)
# ============================================================================
class Particula(pygame.sprite.Sprite):
    """Partícula individual para simular chispas y esquirlas al explotar."""
    def __init__(self, x, y, color):
        super().__init__()
        self.radio = random.randint(2, 4)
        self.image = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.radio, self.radio), self.radio)
        self.rect = self.image.get_rect(center=(x, y))
        
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(2, 6)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.vida_util = random.randint(20, 35)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        self.vida_util -= 1
        if self.vida_util <= 0:
            self.kill()


# ============================================================================
# CLASE: Bullet (proyectil genérico)
# ============================================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direccion=-1, color=VERDE_LASER,
                 velocidad=VELOCIDAD_BALA_JUGADOR, vx=0.0,
                 ancho=4, alto=14, danio=1, es_enemiga=False):
        super().__init__()
        self.image = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, ancho, alto), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.direccion = direccion
        self.velocidad = velocidad
        self.vx = vx
        self.danio = danio
        self.es_enemiga = es_enemiga

    def update(self):
        self.pos_x += self.vx
        self.rect.centerx = int(self.pos_x)
        self.rect.y += self.velocidad * self.direccion
        if self.rect.bottom < 0 or self.rect.top > ALTO_VENTANA:
            self.kill()


# ============================================================================
# CLASE: Explosion (efecto visual con ondas y partículas)
# ============================================================================
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, escala=1.0, color_base=ROJO_EXPLOSION):
        super().__init__()
        self.radio = 4 * escala
        self.radio_max = 28 * escala
        self.velocidad_crecimiento = 2.5 * escala
        tam = int(self.radio_max * 2)
        self.image = pygame.Surface((tam, tam), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.centro = tam // 2
        self.color_base = color_base

    def update(self):
        self.radio += self.velocidad_crecimiento
        self.image.fill((0, 0, 0, 0))
        if self.radio < self.radio_max:
            alpha = max(0, 255 - int((self.radio / self.radio_max) * 255))
            pygame.draw.circle(self.image, (*self.color_base, alpha), (self.centro, self.centro), int(self.radio))
            pygame.draw.circle(self.image, (*AMARILLO, alpha), (self.centro, self.centro), max(1, int(self.radio * 0.4)))
        else:
            self.kill()


# ============================================================================
# CLASE: Player (nave del jugador)
# ============================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, ancho_pantalla, alto_pantalla, clave_nave="equilibrada"):
        super().__init__()
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.stats = NAVES[clave_nave]

        self.image_normal = self._crear_sprite(self.stats, color_flash=False)
        self.image_flash = self._crear_sprite(self.stats, color_flash=True)
        self.image = self.image_normal
        self.rect = self.image.get_rect(center=(ancho_pantalla // 2, alto_pantalla - 70))

        self.velocidad = self.stats["velocidad"]
        self.vida_max = self.stats["vida_max"]
        self.vida = self.vida_max
        self.cooldown_disparo = self.stats["cooldown_disparo"]
        self.danio_bala = self.stats["danio_bala"]
        self.patron_disparo = self.stats["patron_disparo"]

        self.bombas = 2  # Bombas inteligentes de emergencia iniciales
        self.ultimo_disparo = 0
        self.invulnerable_hasta = 0
        self.visible = True

    def _crear_sprite(self, stats, color_flash=False):
        ancho = stats["ancho_nave"]
        alto = ancho
        cp = BLANCO if color_flash else stats["color_principal"]
        cs = BLANCO if color_flash else stats["color_secundario"]
        superficie = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.polygon(superficie, cp, [(ancho // 2, 0), (0, alto), (ancho, alto)])
        pygame.draw.polygon(superficie, cs, [
            (ancho // 2, ancho * 0.25), (ancho // 2 - ancho * 0.2, alto - alto * 0.2),
            (ancho // 2 + ancho * 0.2, alto - alto * 0.2)
        ])
        pygame.draw.polygon(superficie, GRIS, [(0, alto), (ancho * 0.25, alto - ancho * 0.35), (ancho * 0.35, alto)])
        pygame.draw.polygon(superficie, GRIS, [(ancho, alto), (ancho - ancho * 0.25, alto - ancho * 0.35), (ancho - ancho * 0.35, alto)])
        return superficie

    def manejar_input(self, teclas):
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.ancho_pantalla)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.alto_pantalla)

    def puede_disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo >= self.cooldown_disparo:
            self.ultimo_disparo = ahora
            return True
        return False

    def disparar(self, grupo_balas, grupo_todos):
        x, y = self.rect.centerx, self.rect.top
        nuevas_balas = []

        if self.patron_disparo == "simple":
            nuevas_balas.append(Bullet(x, y, -1, VERDE_LASER, VELOCIDAD_BALA_JUGADOR, 0, danio=self.danio_bala))
        elif self.patron_disparo == "doble":
            offset = 10
            nuevas_balas.append(Bullet(x - offset, y, -1, VERDE_LASER, VELOCIDAD_BALA_JUGADOR, 0, danio=self.danio_bala))
            nuevas_balas.append(Bullet(x + offset, y, -1, VERDE_LASER, VELOCIDAD_BALA_JUGADOR, 0, danio=self.danio_bala))
        elif self.patron_disparo == "abanico":
            nuevas_balas.append(Bullet(x, y, -1, VERDE_LASER, VELOCIDAD_BALA_JUGADOR, 0, ancho=6, alto=16, danio=self.danio_bala))
            nuevas_balas.append(Bullet(x, y, -1, VERDE_LASER, VELOCIDAD_BALA_JUGADOR, vx=-2.4, ancho=6, alto=16, danio=self.danio_bala))
            nuevas_balas.append(Bullet(x, y, -1, VERDE_LASER, VELOCIDAD_BALA_JUGADOR, vx=2.4, ancho=6, alto=16, danio=self.danio_bala))

        for bala in nuevas_balas:
            grupo_balas.add(bala)
            grupo_todos.add(bala)

    def recibir_dano(self, cantidad=1):
        ahora = pygame.time.get_ticks()
        if ahora >= self.invulnerable_hasta:
            self.vida -= cantidad
            self.invulnerable_hasta = ahora + 1200
            return True
        return False

    def esta_invulnerable(self):
        return pygame.time.get_ticks() < self.invulnerable_hasta

    def update(self):
        if self.esta_invulnerable():
            self.visible = (pygame.time.get_ticks() // 100) % 2 == 0
            self.image = self.image_flash
        else:
            self.visible = True
            self.image = self.image_normal

    def dibujar(self, pantalla):
        if self.visible:
            pantalla.blit(self.image, self.rect)


# ============================================================================
# CLASE: Enemy (enemigo base) y sus variantes con destello de daño
# ============================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, ancho_pantalla, tipo, color, tamano, vida, puntos,
                 velocidad_y, patron="recto"):
        super().__init__()
        self.ancho_pantalla = ancho_pantalla
        self.tipo = tipo
        self.patron = patron
        self.vida_max = vida
        self.vida = vida
        self.puntos = puntos

        self.color_original = color
        self.image_normal = self._crear_sprite(color, tamano, flash=False)
        self.image_flash = self._crear_sprite(BLANCO, tamano, flash=True)
        self.image = self.image_normal
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, ancho_pantalla - self.rect.width)
        self.rect.y = random.randint(-120, -40)

        self.velocidad_y = velocidad_y
        self.velocidad_x = random.choice([-1, 1]) * random.uniform(1, 2)
        self.x_flotante = float(self.rect.x)
        self.tiempo_inicial = pygame.time.get_ticks()

        self.puede_disparar = (tipo == "mediano")
        self.cooldown_disparo = random.randint(1800, 3200)
        self.ultimo_disparo = pygame.time.get_ticks() + random.randint(0, 1500)
        self.tiempo_flash_hasta = 0

    def _crear_sprite(self, color, tamano, flash=False):
        superficie = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
        pygame.draw.polygon(superficie, color, [(0, 0), (tamano, 0), (tamano // 2, tamano)])
        pygame.draw.circle(superficie, AMARILLO if not flash else BLANCO, (tamano // 2, int(tamano * 0.3)), max(3, tamano // 7))
        return superficie

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        self.tiempo_flash_hasta = pygame.time.get_ticks() + 90  # Destello de 90ms al recibir impacto
        return self.vida <= 0

    def intentar_disparar(self, grupo_balas_enemigas, grupo_todos):
        if not self.puede_disparar:
            return
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo >= self.cooldown_disparo:
            self.ultimo_disparo = ahora
            bala = Bullet(self.rect.centerx, self.rect.bottom, direccion=1,
                          color=BALA_ENEMIGA_COLOR, velocidad=VELOCIDAD_BALA_ENEMIGA,
                          danio=1, es_enemiga=True)
            grupo_balas_enemigas.add(bala)
            grupo_todos.add(bala)

    def update(self):
        self.rect.y += self.velocidad_y

        if self.patron == "zigzag":
            tiempo = (pygame.time.get_ticks() - self.tiempo_inicial) / 300.0
            self.x_flotante += self.velocidad_x
            self.rect.x = int(self.x_flotante + 40 * math.sin(tiempo))
            if self.rect.left < 0 or self.rect.right > self.ancho_pantalla:
                self.velocidad_x *= -1

        # Control del destello visual
        if pygame.time.get_ticks() < self.tiempo_flash_hasta:
            self.image = self.image_flash
        else:
            self.image = self.image_normal

        if self.rect.top > ALTO_VENTANA:
            self.kill()


class EnemigoPequeno(Enemy):
    def __init__(self, ancho_pantalla):
        super().__init__(
            ancho_pantalla, tipo="pequeno", color=NARANJA_ENEMIGO, tamano=26,
            vida=1, puntos=10, velocidad_y=random.uniform(3, 4.5), patron="zigzag"
        )


class EnemigoMediano(Enemy):
    def __init__(self, ancho_pantalla):
        super().__init__(
            ancho_pantalla, tipo="mediano", color=ROJO_ENEMIGO, tamano=40,
            vida=3, puntos=25, velocidad_y=random.uniform(1.5, 2.5), patron="recto"
        )


# ============================================================================
# CLASE: Jefe (Boss final con destello y patrones de ataque)
# ============================================================================
class Jefe(pygame.sprite.Sprite):
    ANCHO = 110
    ALTO = 90

    def __init__(self, ancho_pantalla, nivel=1):
        super().__init__()
        self.ancho_pantalla = ancho_pantalla
        self.nivel = nivel
        self.vida_max = 40 + (nivel - 1) * 25
        self.vida = self.vida_max
        self.puntos = 200 + (nivel - 1) * 50

        self.image_normal = self._crear_sprite(flash=False)
        self.image_flash = self._crear_sprite(flash=True)
        self.image = self.image_normal
        self.rect = self.image.get_rect(midtop=(ancho_pantalla // 2, -self.ALTO))

        self.y_objetivo = 90
        self.entrando = True
        self.velocidad_entrada = 2
        self.velocidad_patrulla = 2.2
        self.direccion_x = 1

        self.ultimo_disparo = pygame.time.get_ticks()
        self.cooldown_disparo = 1100
        self.patron_actual = "abanico"
        self.ultimo_cambio_patron = pygame.time.get_ticks()
        self.tiempo_flash_hasta = 0

    def _crear_sprite(self, flash=False):
        superficie = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        cp = BLANCO if flash else MORADO_JEFE
        pygame.draw.polygon(superficie, cp, [
            (self.ANCHO * 0.5, 0), (self.ANCHO * 0.05, self.ALTO * 0.55),
            (self.ANCHO * 0.2, self.ALTO), (self.ANCHO * 0.8, self.ALTO),
            (self.ANCHO * 0.95, self.ALTO * 0.55)
        ])
        pygame.draw.polygon(superficie, (220, 160, 255) if not flash else BLANCO, [
            (self.ANCHO * 0.5, self.ALTO * 0.15), (self.ANCHO * 0.35, self.ALTO * 0.55),
            (self.ANCHO * 0.65, self.ALTO * 0.55)
        ])
        pygame.draw.circle(superficie, AMARILLO, (int(self.ANCHO * 0.5), int(self.ALTO * 0.4)), 8)
        pygame.draw.circle(superficie, ROJO_ENEMIGO, (int(self.ANCHO * 0.2), int(self.ALTO * 0.65)), 6)
        pygame.draw.circle(superficie, ROJO_ENEMIGO, (int(self.ANCHO * 0.8), int(self.ALTO * 0.65)), 6)
        return superficie

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        self.tiempo_flash_hasta = pygame.time.get_ticks() + 90
        return self.vida <= 0

    def _disparar_abanico(self, grupo_balas_enemigas, grupo_todos):
        for vx in (-3.0, -1.5, 0.0, 1.5, 3.0):
            bala = Bullet(self.rect.centerx, self.rect.bottom, direccion=1,
                          color=BALA_ENEMIGA_COLOR, velocidad=VELOCIDAD_BALA_ENEMIGA,
                          vx=vx, danio=1, es_enemiga=True)
            grupo_balas_enemigas.add(bala)
            grupo_todos.add(bala)

    def _disparar_rafaga(self, grupo_balas_enemigas, grupo_todos):
        for dx in (-25, 0, 25):
            bala = Bullet(self.rect.centerx + dx, self.rect.bottom, direccion=1,
                          color=BALA_ENEMIGA_COLOR, velocidad=VELOCIDAD_BALA_ENEMIGA + 1.5,
                          danio=1, es_enemiga=True)
            grupo_balas_enemigas.add(bala)
            grupo_todos.add(bala)

    def update_ataque(self, grupo_balas_enemigas, grupo_todos):
        if self.entrando:
            return
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_cambio_patron >= 4000:
            self.patron_actual = "rafaga" if self.patron_actual == "abanico" else "abanico"
            self.ultimo_cambio_patron = ahora

        if ahora - self.ultimo_disparo >= self.cooldown_disparo:
            self.ultimo_disparo = ahora
            if self.patron_actual == "abanico":
                self._disparar_abanico(grupo_balas_enemigas, grupo_todos)
            else:
                self._disparar_rafaga(grupo_balas_enemigas, grupo_todos)

    def update(self):
        if self.entrando:
            self.rect.y += self.velocidad_entrada
            if self.rect.top >= self.y_objetivo:
                self.rect.top = self.y_objetivo
                self.entrando = False
        else:
            self.rect.x += int(self.velocidad_patrulla * self.direccion_x)
            if self.rect.left <= 0 or self.rect.right >= self.ancho_pantalla:
                self.direccion_x *= -1

        if pygame.time.get_ticks() < self.tiempo_flash_hasta:
            self.image = self.image_flash
        else:
            self.image = self.image_normal


# ============================================================================
# CLASE: Menu (menús interactivos)
# ============================================================================
class Menu:
    def __init__(self, pantalla, fuentes, gestor_puntuaciones):
        self.pantalla = pantalla
        self.fuente_titulo = fuentes["titulo"]
        self.fuente_media = fuentes["media"]
        self.fuente_hud = fuentes["hud"]
        self.gestor_puntuaciones = gestor_puntuaciones

        self.opciones_principal = ["Iniciar Juego", "Seleccionar Nave", "Puntuaciones Máximas", "Salir"]
        self.indice_seleccionado = 0
        self.nave_resaltada = 0

    def _dibujar_fondo_simple(self, estrellas):
        self.pantalla.fill(NEGRO)
        for estrella in estrellas:
            estrella.dibujar(self.pantalla)

    def dibujar_principal(self, estrellas, nave_actual):
        self._dibujar_fondo_simple(estrellas)

        titulo = self.fuente_titulo.render("SPACE RAIDER", True, AZUL_CLARO)
        rect_titulo = titulo.get_rect(center=(ANCHO_VENTANA // 2, 110))
        self.pantalla.blit(titulo, rect_titulo)

        subtitulo = self.fuente_hud.render("Shoot 'em up arcade", True, GRIS)
        rect_sub = subtitulo.get_rect(center=(ANCHO_VENTANA // 2, 150))
        self.pantalla.blit(subtitulo, rect_sub)

        self.rects_opciones = []
        y_inicial = 260
        for i, texto in enumerate(self.opciones_principal):
            color = AMARILLO if i == self.indice_seleccionado else BLANCO
            render = self.fuente_media.render(texto, True, color)
            rect = render.get_rect(center=(ANCHO_VENTANA // 2, y_inicial + i * 50))
            self.pantalla.blit(render, rect)
            self.rects_opciones.append(rect)

            if i == self.indice_seleccionado:
                pygame.draw.polygon(self.pantalla, AMARILLO, [
                    (rect.left - 22, rect.centery - 8), (rect.left - 22, rect.centery + 8), (rect.left - 8, rect.centery)
                ])

        nombre_nave = NAVES[nave_actual]["nombre"]
        texto_nave = self.fuente_hud.render(f"Nave actual: {nombre_nave}", True, AZUL_CLARO)
        rect_nave = texto_nave.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA - 40))
        self.pantalla.blit(texto_nave, rect_nave)

    def dibujar_seleccion_nave(self, estrellas, nave_actual):
        self._dibujar_fondo_simple(estrellas)

        titulo = self.fuente_media.render("SELECCIONÁ TU NAVE", True, AZUL_CLARO)
        rect_titulo = titulo.get_rect(center=(ANCHO_VENTANA // 2, 60))
        self.pantalla.blit(titulo, rect_titulo)

        self.rects_naves = []
        y = 130
        for i, clave in enumerate(ORDEN_NAVES):
            stats = NAVES[clave]
            es_actual = (clave == nave_actual)
            resaltada = (i == self.nave_resaltada)

            alto_tarjeta = 110
            rect_tarjeta = pygame.Rect(30, y, ANCHO_VENTANA - 60, alto_tarjeta)
            color_borde = AMARILLO if resaltada else GRIS_OSCURO
            pygame.draw.rect(self.pantalla, (25, 25, 40), rect_tarjeta, border_radius=8)
            pygame.draw.rect(self.pantalla, color_borde, rect_tarjeta, width=3, border_radius=8)

            icono = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(icono, stats["color_principal"], [(20, 0), (0, 40), (40, 40)])
            self.pantalla.blit(icono, (rect_tarjeta.left + 15, rect_tarjeta.top + 15))

            nombre_txt = self.fuente_hud.render(stats["nombre"], True, BLANCO)
            self.pantalla.blit(nombre_txt, (rect_tarjeta.left + 70, rect_tarjeta.top + 12))

            desc_txt = self._render_texto_ajustado(stats["descripcion"], rect_tarjeta.width - 85)
            for j, linea in enumerate(desc_txt):
                self.pantalla.blit(linea, (rect_tarjeta.left + 70, rect_tarjeta.top + 38 + j * 18))

            if es_actual:
                marca = self.fuente_hud.render("EQUIPADA", True, VERDE_VIDA)
                self.pantalla.blit(marca, (rect_tarjeta.right - 100, rect_tarjeta.top + 12))

            self.rects_naves.append(rect_tarjeta)
            y += alto_tarjeta + 15

        ayuda = self.fuente_hud.render("ENTER o clic para equipar - ESC para volver", True, GRIS)
        rect_ayuda = ayuda.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA - 30))
        self.pantalla.blit(ayuda, rect_ayuda)

    def _render_texto_ajustado(self, texto, ancho_max):
        fuente = pygame.font.SysFont("consolas", 14)
        palabras = texto.split(" ")
        lineas, actual = [], ""
        for palabra in palabras:
            prueba = (actual + " " + palabra).strip()
            if fuente.size(prueba)[0] <= ancho_max:
                actual = prueba
            else:
                lineas.append(fuente.render(actual, True, GRIS))
                actual = palabra
        if actual:
            lineas.append(fuente.render(actual, True, GRIS))
        return lineas

    def dibujar_puntuaciones(self, estrellas):
        self._dibujar_fondo_simple(estrellas)

        titulo = self.fuente_media.render("PUNTUACIONES MÁXIMAS", True, AZUL_CLARO)
        rect_titulo = titulo.get_rect(center=(ANCHO_VENTANA // 2, 70))
        self.pantalla.blit(titulo, rect_titulo)

        puntuaciones = self.gestor_puntuaciones.cargar()
        if not puntuaciones:
            vacio = self.fuente_hud.render("Todavía no hay puntuaciones registradas.", True, GRIS)
            rect_vacio = vacio.get_rect(center=(ANCHO_VENTANA // 2, 200))
            self.pantalla.blit(vacio, rect_vacio)
        else:
            for i, puntos in enumerate(puntuaciones):
                color = AMARILLO if i == 0 else BLANCO
                texto = f"{i + 1}.  {puntos} pts"
                render = self.fuente_media.render(texto, True, color)
                rect = render.get_rect(midleft=(ANCHO_VENTANA // 2 - 90, 140 + i * 42))
                self.pantalla.blit(render, rect)

        ayuda = self.fuente_hud.render("ESC para volver al menú", True, GRIS)
        rect_ayuda = ayuda.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA - 30))
        self.pantalla.blit(ayuda, rect_ayuda)


# ============================================================================
# CLASE PRINCIPAL: Game
# ============================================================================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Space Raider - Shoot 'em Up")
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        self.reloj = pygame.time.Clock()

        self.fuentes = {
            "hud": pygame.font.SysFont("consolas", 18, bold=True),
            "media": pygame.font.SysFont("consolas", 24, bold=True),
            "grande": pygame.font.SysFont("consolas", 42, bold=True),
            "titulo": pygame.font.SysFont("consolas", 40, bold=True),
        }

        self.estrellas = [Estrella(ANCHO_VENTANA, ALTO_VENTANA) for _ in range(90)]
        self.gestor_puntuaciones = GestorPuntuaciones()
        self.menu = Menu(self.pantalla, self.fuentes, self.gestor_puntuaciones)

        self.estado = ESTADO_MENU
        self.nave_seleccionada = "equilibrada"
        self.record_nuevo = False

        self._reiniciar_variables_partida()

    def _reiniciar_variables_partida(self):
        self.jugador = None
        self.grupo_todos = pygame.sprite.Group()
        self.grupo_balas_jugador = pygame.sprite.Group()
        self.grupo_balas_enemigas = pygame.sprite.Group()
        self.grupo_enemigos = pygame.sprite.Group()
        self.grupo_jefe = pygame.sprite.GroupSingle()
        self.grupo_explosiones = pygame.sprite.Group()
        self.grupo_particulas = pygame.sprite.Group()

        self.puntuacion = 0
        self.ultimo_spawn_enemigo = pygame.time.get_ticks()
        self.nivel_jefe_actual = 0
        self.puntuacion_siguiente_jefe = PUNTOS_PRIMER_JEFE
        self.jefe_activo = False
        self.record_nuevo = False

    def iniciar_partida(self):
        self._reiniciar_variables_partida()
        self.jugador = Player(ANCHO_VENTANA, ALTO_VENTANA, self.nave_seleccionada)
        self.estado = ESTADO_JUGANDO

    def spawnear_enemigos(self):
        if self.jefe_activo:
            return
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_spawn_enemigo >= INTERVALO_SPAWN_ENEMIGO:
            self.ultimo_spawn_enemigo = ahora
            probabilidad_mediano = min(0.5, 0.15 + self.puntuacion / 1000.0)
            if random.random() < probabilidad_mediano:
                enemigo = EnemigoMediano(ANCHO_VENTANA)
            else:
                enemigo = EnemigoPequeno(ANCHO_VENTANA)
            self.grupo_enemigos.add(enemigo)
            self.grupo_todos.add(enemigo)

    def comprobar_aparicion_jefe(self):
        if not self.jefe_activo and self.puntuacion >= self.puntuacion_siguiente_jefe:
            self.jefe_activo = True
            self.nivel_jefe_actual += 1
            jefe = Jefe(ANCHO_VENTANA, nivel=self.nivel_jefe_actual)
            self.grupo_jefe.add(jefe)
            self.grupo_todos.add(jefe)
            for enemigo in list(self.grupo_enemigos):
                enemigo.kill()

    def usar_bomba_inteligente(self):
        """Activa una bomba inteligente limpiando balas enemigas y dañando rivales."""
        if self.jugador and self.jugador.bombas > 0:
            self.jugador.bombas -= 1
            # Destruir todas las balas enemigas
            for bala in self.grupo_balas_enemigas:
                self.grupo_explosiones.add(Explosion(bala.rect.centerx, bala.rect.centery, escala=0.4, color_base=COLOR_BOMBA))
                bala.kill()
            # Dañar enemigos normales en pantalla
            for enemigo in self.grupo_enemigos:
                self.puntuacion += enemigo.puntos
                self.grupo_explosiones.add(Explosion(enemigo.rect.centerx, enemigo.rect.centery, escala=1.2, color_base=COLOR_BOMBA))
                enemigo.kill()
            # Dañar al jefe si está presente
            jefe = self.grupo_jefe.sprite
            if jefe is not None:
                if jefe.recibir_dano(15):  # Daño masivo al jefe
                    self.puntuacion += jefe.puntos
                    self.grupo_explosiones.add(Explosion(jefe.rect.centerx, jefe.rect.centery, escala=2.5, color_base=COLOR_BOMBA))
                    jefe.kill()
                    self.jefe_activo = False
                    self.puntuacion_siguiente_jefe = self.puntuacion + INCREMENTO_PUNTOS_JEFE
            # Generar chispas estéticas por toda la pantalla
            for _ in range(40):
                self.grupo_particulas.add(Particula(random.randint(0, ANCHO_VENTANA), random.randint(0, ALTO_VENTANA), COLOR_BOMBA))

    def crear_explosion_con_particulas(self, x, y, escala=1.0, color=ROJO_EXPLOSION):
        self.grupo_explosiones.add(Explosion(x, y, escala=escala, color_base=color))
        for _ in range(random.randint(6, 12)):
            self.grupo_particulas.add(Particula(x, y, color))

    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.estado == ESTADO_MENU:
                self._eventos_menu_principal(evento)
            elif self.estado == ESTADO_SELECCION_NAVE:
                self._eventos_seleccion_nave(evento)
            elif self.estado == ESTADO_PUNTUACIONES:
                self._eventos_puntuaciones(evento)
            elif self.estado == ESTADO_JUGANDO:
                self._eventos_jugando(evento)
            elif self.estado == ESTADO_GAMEOVER:
                self._eventos_gameover(evento)

    def _eventos_menu_principal(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.menu.indice_seleccionado = (self.menu.indice_seleccionado - 1) % len(self.menu.opciones_principal)
            elif evento.key == pygame.K_DOWN:
                self.menu.indice_seleccionado = (self.menu.indice_seleccionado + 1) % len(self.menu.opciones_principal)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activar_opcion_principal(self.menu.indice_seleccionado)
            elif evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif evento.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(getattr(self.menu, "rects_opciones", [])):
                if rect.collidepoint(evento.pos):
                    self.menu.indice_seleccionado = i
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(getattr(self.menu, "rects_opciones", [])):
                if rect.collidepoint(evento.pos):
                    self._activar_opcion_principal(i)

    def _activar_opcion_principal(self, indice):
        opcion = self.menu.opciones_principal[indice]
        if opcion == "Iniciar Juego":
            self.iniciar_partida()
        elif opcion == "Seleccionar Nave":
            self.menu.nave_resaltada = ORDEN_NAVES.index(self.nave_seleccionada)
            self.estado = ESTADO_SELECCION_NAVE
        elif opcion == "Puntuaciones Máximas":
            self.estado = ESTADO_PUNTUACIONES
        elif opcion == "Salir":
            pygame.quit()
            sys.exit()

    def _eventos_seleccion_nave(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.menu.nave_resaltada = (self.menu.nave_resaltada - 1) % len(ORDEN_NAVES)
            elif evento.key == pygame.K_DOWN:
                self.menu.nave_resaltada = (self.menu.nave_resaltada + 1) % len(ORDEN_NAVES)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.nave_seleccionada = ORDEN_NAVES[self.menu.nave_resaltada]
            elif evento.key == pygame.K_ESCAPE:
                self.estado = ESTADO_MENU
        elif evento.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(getattr(self.menu, "rects_naves", [])):
                if rect.collidepoint(evento.pos):
                    self.menu.nave_resaltada = i
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(getattr(self.menu, "rects_naves", [])):
                if rect.collidepoint(evento.pos):
                    self.nave_seleccionada = ORDEN_NAVES[i]

    def _eventos_puntuaciones(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.estado = ESTADO_MENU
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            self.estado = ESTADO_MENU

    def _eventos_jugando(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif evento.key == pygame.K_x:  # Tecla X para usar Bomba Inteligente
                self.usar_bomba_inteligente()

    def _eventos_gameover(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                self.iniciar_partida()
            elif evento.key == pygame.K_m:
                self.estado = ESTADO_MENU
            elif evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def actualizar(self):
        for estrella in self.estrellas:
            estrella.actualizar()

        if self.estado != ESTADO_JUGANDO:
            return

        teclas = pygame.key.get_pressed()
        self.jugador.manejar_input(teclas)
        if teclas[pygame.K_SPACE] and self.jugador.puede_disparar():
            self.jugador.disparar(self.grupo_balas_jugador, self.grupo_todos)
        self.jugador.update()

        self.spawnear_enemigos()
        self.comprobar_aparicion_jefe()

        self.grupo_enemigos.update()
        self.grupo_balas_jugador.update()
        self.grupo_balas_enemigas.update()
        self.grupo_explosiones.update()
        self.grupo_particulas.update()

        jefe = self.grupo_jefe.sprite
        if jefe is not None:
            jefe.update()
            jefe.update_ataque(self.grupo_balas_enemigas, self.grupo_todos)

        self._procesar_colisiones()

        if self.jugador.vida <= 0:
            self._finalizar_partida()

    def _procesar_colisiones(self):
        for enemigo in list(self.grupo_enemigos):
            balas_impacto = pygame.sprite.spritecollide(enemigo, self.grupo_balas_jugador, True)
            for bala in balas_impacto:
                if enemigo.recibir_dano(bala.danio):
                    self.puntuacion += enemigo.puntos
                    self.crear_explosion_con_particulas(enemigo.rect.centerx, enemigo.rect.centery)
                    enemigo.kill()

        jefe = self.grupo_jefe.sprite
        if jefe is not None:
            balas_impacto = pygame.sprite.spritecollide(jefe, self.grupo_balas_jugador, True)
            for bala in balas_impacto:
                self.crear_explosion_con_particulas(bala.rect.centerx, bala.rect.centery, escala=0.6)
                if jefe.recibir_dano(bala.danio):
                    self.puntuacion += jefe.puntos
                    self.crear_explosion_con_particulas(jefe.rect.centerx, jefe.rect.centery, escala=2.5, color=MORADO_JEFE)
                    jefe.kill()
                    self.jefe_activo = False
                    self.puntuacion_siguiente_jefe = self.puntuacion + INCREMENTO_PUNTOS_JEFE
                    self.ultimo_spawn_enemigo = pygame.time.get_ticks()

        enemigos_impactados = pygame.sprite.spritecollide(
            self.jugador, self.grupo_enemigos, True,
            collided=pygame.sprite.collide_rect_ratio(0.75)
        )
        for enemigo in enemigos_impactados:
            if self.jugador.recibir_dano(1):
                self.crear_explosion_con_particulas(enemigo.rect.centerx, enemigo.rect.centery)

        if jefe is not None and self.jugador.rect.colliderect(jefe.rect):
            self.jugador.recibir_dano(1)

        balas_enemigas_impacto = pygame.sprite.spritecollide(self.jugador, self.grupo_balas_enemigas, True)
        for bala in balas_enemigas_impacto:
            if self.jugador.recibir_dano(bala.danio):
                self.crear_explosion_con_particulas(self.jugador.rect.centerx, self.jugador.rect.centery, escala=0.7)

    def _finalizar_partida(self):
        self.crear_explosion_con_particulas(self.jugador.rect.centerx, self.jugador.rect.centery, escala=1.8)
        self.record_nuevo = self.gestor_puntuaciones.agregar_puntuacion(self.puntuacion)
        self.estado = ESTADO_GAMEOVER

    def dibujar_hud(self):
        texto_puntos = self.fuentes["hud"].render(f"PUNTOS: {self.puntuacion}", True, BLANCO)
        self.pantalla.blit(texto_puntos, (12, 10))

        texto_vidas = self.fuentes["hud"].render(f"VIDA: {max(self.jugador.vida, 0)}/{self.jugador.vida_max}", True, BLANCO)
        rect_vidas = texto_vidas.get_rect(topright=(ANCHO_VENTANA - 12, 10))
        self.pantalla.blit(texto_vidas, rect_vidas)

        texto_bombas = self.fuentes["hud"].render(f"BOMBAS [X]: {self.jugador.bombas}", True, COLOR_BOMBA)
        self.pantalla.blit(texto_bombas, (12, 34))

        jefe = self.grupo_jefe.sprite
        if jefe is not None:
            ancho_barra = 260
            x_barra = (ANCHO_VENTANA - ancho_barra) // 2
            y_barra = 34
            proporcion = max(0, jefe.vida) / jefe.vida_max
            pygame.draw.rect(self.pantalla, GRIS_OSCURO, (x_barra, y_barra, ancho_barra, 14), border_radius=4)
            pygame.draw.rect(self.pantalla, MORADO_JEFE, (x_barra, y_barra, int(ancho_barra * proporcion), 14), border_radius=4)
            pygame.draw.rect(self.pantalla, BLANCO, (x_barra, y_barra, ancho_barra, 14), width=2, border_radius=4)
            etiqueta = self.fuentes["hud"].render(f"JEFE Nv.{jefe.nivel}", True, MORADO_JEFE)
            rect_etiqueta = etiqueta.get_rect(center=(ANCHO_VENTANA // 2, y_barra - 12))
            self.pantalla.blit(etiqueta, rect_etiqueta)

    def dibujar_pantalla_game_over(self):
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.pantalla.blit(overlay, (0, 0))

        texto1 = self.fuentes["grande"].render("GAME OVER", True, ROJO_ENEMIGO)
        rect1 = texto1.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 70))
        self.pantalla.blit(texto1, rect1)

        texto2 = self.fuentes["media"].render(f"Puntuación final: {self.puntuacion}", True, BLANCO)
        rect2 = texto2.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 20))
        self.pantalla.blit(texto2, rect2)

        if self.record_nuevo:
            texto_record = self.fuentes["hud"].render("¡NUEVO RÉCORD!", True, AMARILLO)
            rect_record = texto_record.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 15))
            self.pantalla.blit(texto_record, rect_record)

        texto3 = self.fuentes["hud"].render("R: reintentar   M: menú   ESC: salir", True, GRIS)
        rect3 = texto3.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 60))
        self.pantalla.blit(texto3, rect3)

    def dibujar(self):
        if self.estado == ESTADO_MENU:
            self.menu.dibujar_principal(self.estrellas, self.nave_seleccionada)
        elif self.estado == ESTADO_SELECCION_NAVE:
            self.menu.dibujar_seleccion_nave(self.estrellas, self.nave_seleccionada)
        elif self.estado == ESTADO_PUNTUACIONES:
            self.menu.dibujar_puntuaciones(self.estrellas)
        elif self.estado in (ESTADO_JUGANDO, ESTADO_GAMEOVER):
            self.pantalla.fill(NEGRO)
            for estrella in self.estrellas:
                estrella.dibujar(self.pantalla)

            self.grupo_enemigos.draw(self.pantalla)
            self.grupo_jefe.draw(self.pantalla)
            self.grupo_balas_jugador.draw(self.pantalla)
            self.grupo_balas_enemigas.draw(self.pantalla)
            self.grupo_particulas.draw(self.pantalla)
            self.grupo_explosiones.draw(self.pantalla)
            self.jugador.dibujar(self.pantalla)

            self.dibujar_hud()

            if self.estado == ESTADO_GAMEOVER:
                self.dibujar_pantalla_game_over()

        pygame.display.flip()

    def ejecutar(self):
        while True:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)


if __name__ == "__main__":
    juego = Game()
    juego.ejecutar()