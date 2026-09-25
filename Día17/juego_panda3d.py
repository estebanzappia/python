from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import AmbientLight, DirectionalLight, Vec4, Vec3, TextNode
import random
import json
import os

class ThunderaxCompleto(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Configuración visual del espacio
        self.setBackgroundColor(0.02, 0.02, 0.08)
        self.camera.setPos(0, -35, 25)
        self.camera.lookAt(0, 0, 0)

        # Iluminación
        luz_ambiente = AmbientLight("luz_amb")
        luz_ambiente.setColor(Vec4(0.8, 0.8, 0.9, 1))
        self.render.setLight(self.render.attachNewNode(luz_ambiente))

        luz_dir = DirectionalLight("luz_dir")
        luz_dir.setColor(Vec4(1, 0.9, 0.8, 1))
        dlnp = self.render.attachNewNode(luz_dir)
        dlnp.setHpr(45, -60, 0)
        self.render.setLight(dlnp)

        # Variables de estado y datos
        self.estado_juego = "MENU" # Estados: "MENU", "JUGANDO", "GAMEOVER"
        self.vidas = 3
        self.puntaje = 0
        self.nivel = 1
        self.max_score = self.cargar_record()
        
        # Opciones de colores para el jugador (RGBA)
        self.colores_disponibles = [
            ("Clásico (Blanco)", Vec4(1, 1, 1, 1)),
            ("Dorado Épico", Vec4(1, 0.8, 0.1, 1)),
            ("Ciber Verde", Vec4(0.1, 1, 0.4, 1)),
            ("Neón Magenta", Vec4(1, 0.1, 0.8, 1))
        ]
        self.color_seleccionado_idx = 0

        self.velocidad_nave = 20
        self.key_map = {"left": 0, "right": 0, "up": 0, "down": 0, "fire": 0}
        
        self.balas_jugador = []
        self.balas_enemigas = []
        self.enemigos = []
        self.asteroides = []
        self.particulas_explosion = []
        self.ultimo_disparo = 0

        # Crear modelos base (ocultos inicialmente o gestionados por estado)
        self.player = self.loader.loadModel("models/panda-model")
        self.player.reparentTo(self.render)
        self.player.setScale(0.004, 0.004, 0.004)
        self.player.hide()

        # Crear Interfaz Gráfica (HUD y Menús)
        self.crear_textos_interfaz()
        self.crear_entorno_asteroides()

        # Controles globales y de menú
        self.accept("arrow_left", self.actualizar_tecla, ["left", 1])
        self.accept("arrow_right", self.actualizar_tecla, ["right", 1])
        self.accept("arrow_up", self.actualizar_tecla, ["up", 1])
        self.accept("arrow_down", self.actualizar_tecla, ["down", 1])
        self.accept("arrow_left-up", self.actualizar_tecla, ["left", 0])
        self.accept("arrow_right-up", self.actualizar_tecla, ["right", 0])
        self.accept("arrow_up-up", self.actualizar_tecla, ["up", 0])
        self.accept("arrow_down-up", self.actualizar_tecla, ["down", 0])
        self.accept("space", self.actualizar_tecla, ["fire", 1])
        self.accept("space-up", self.actualizar_tecla, ["fire", 0])

        # Teclas del menú y opciones
        self.accept("enter", self.iniciar_partida)
        self.accept("c", self.cambiar_color)
        self.accept("r", self.reiniciar_juego)
        self.accept("m", self.ir_al_menu)

        # Bucle principal del juego
        self.taskMgr.add(self.actualizar_juego, "ActualizarJuego")

    def crear_textos_interfaz(self):
        # Texto del HUD durante la partida
        self.hud_texto = OnscreenText(
            text="", pos=(-1.3, 0.9), scale=0.05,
            fg=(1, 1, 1, 1), align=TextNode.ALeft, shadow=(0, 0, 0, 1)
        )
        
        # Texto del Menú Principal
        nombre_color, _ = self.colores_disponibles[self.color_seleccionado_idx]
        self.menu_texto = OnscreenText(
            text=(f"=== THUNDERAX ARCADE ===\n\n"
                  f"Presiona [ ENTER ] para Jugar\n"
                  f"Presiona [ C ] para cambiar color de nave\n"
                  f"Color actual: {nombre_color}\n\n"
                  f"Record Actual: {self.max_score} pts"),
            pos=(0, 0.2), scale=0.07,
            fg=(1, 1, 0.3, 1), align=TextNode.ACenter, shadow=(0, 0, 0, 1)
        )

        # Texto de Game Over
        self.gameover_texto = OnscreenText(
            text="", pos=(0, 0.2), scale=0.08,
            fg=(1, 0.2, 0.2, 1), align=TextNode.ACenter, shadow=(0, 0, 0, 1)
        )
        self.gameover_texto.hide()

    def cambiar_color(self):
        if self.estado_juego == "MENU":
            self.color_seleccionado_idx = (self.color_seleccionado_idx + 1) % len(self.colores_disponibles)
            nombre_color, _ = self.colores_disponibles[self.color_seleccionado_idx]
            self.menu_texto.setText(
                f"=== THUNDERAX ARCADE ===\n\n"
                f"Presiona [ ENTER ] para Jugar\n"
                f"Presiona [ C ] para cambiar color de nave\n"
                f"Color actual: {nombre_color}\n\n"
                f"Record Actual: {self.max_score} pts"
            )

    def iniciar_partida(self):
        if self.estado_juego == "MENU":
            self.estado_juego = "JUGANDO"
            self.menu_texto.hide()
            
            # Aplicar color elegido
            _, color_rgba = self.colores_disponibles[self.color_seleccionado_idx]
            self.player.setColor(color_rgba)
            self.player.setPos(0, -10, 0)
            self.player.setHpr(180, 0, 0)
            self.player.show()
            
            # Resetear valores de juego
            self.vidas = 3
            self.puntaje = 0
            self.nivel = 1
            self.hud_texto.setText(self.actualizar_texto_hud())

    def ir_al_menu(self):
        if self.estado_juego == "GAMEOVER":
            self.gameover_texto.hide()
            self.estado_juego = "MENU"
            self.menu_texto.show()
            self.limpiar_elementos_combate()

    def reiniciar_juego(self):
        if self.estado_juego == "GAMEOVER":
            self.gameover_texto.hide()
            self.limpiar_elementos_combate()
            self.estado_juego = "JUGANDO"
            self.vidas = 3
            self.puntaje = 0
            self.nivel = 1
            self.player.setPos(0, -10, 0)
            self.player.show()
            self.hud_texto.setText(self.actualizar_texto_hud())

    def limpiar_elementos_combate(self):
        for b in self.balas_jugador: b.removeNode()
        for b in self.balas_enemigas: b.removeNode()
        for en in self.enemigos: en.removeNode()
        for pt in self.particulas_explosion: pt["node"].removeNode()
        self.balas_jugador.clear()
        self.balas_enemigas.clear()
        self.enemigos.clear()
        self.particulas_explosion.clear()

    def cargar_record(self):
        if os.path.exists("highscores.json"):
            try:
                with open("highscores.json", "r") as f:
                    data = json.load(f)
                    return data.get("max_score", 0)
            except:
                return 0
        return 0

    def guardar_record(self):
        if self.puntaje > self.max_score:
            self.max_score = self.puntaje
            data = {"max_score": self.max_score}
            try:
                with open("highscores.json", "w") as f:
                    json.dump(data, f)
            except Exception as e:
                print("Error al guardar JSON:", e)

    def actualizar_texto_hud(self):
        return f"VIDAS: {self.vidas}  |  PUNTAJE: {self.puntaje}  |  NIVEL: {self.nivel}  |  RECORD: {self.max_score}"

    def actualizar_tecla(self, tecla, estado):
        self.key_map[tecla] = estado

    def crear_entorno_asteroides(self):
        for _ in range(12):
            ast = self.loader.loadModel("models/box")
            ast.reparentTo(self.render)
            escala = random.uniform(0.5, 1.5)
            ast.setScale(escala)
            tinte = random.uniform(0.3, 0.6)
            ast.setColor(tinte, tinte, tinte + 0.1, 1)
            ast.setPos(random.choice([random.uniform(-14, -10), random.uniform(10, 14)]), random.uniform(-15, 20), random.uniform(-3, 3))
            self.asteroides.append({"node": ast, "vel_z": random.uniform(6, 12)})

    def crear_explosion(self, posicion):
        for _ in range(6):
            p = self.loader.loadModel("models/box")
            p.reparentTo(self.render)
            p.setScale(0.12)
            p.setColor(1, random.uniform(0.2, 0.6), 0, 1)
            p.setPos(posicion)
            dir_p = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.5, 0.5))
            dir_p.normalize()
            self.particulas_explosion.append({"node": p, "dir": dir_p * 15, "vida": 0.3})

    def actualizar_juego(self, task):
        dt = globalClock.getDt()

        # Mover asteroides de fondo siempre
        for ast in self.asteroides:
            node = ast["node"]
            node.setY(node.getY() - ast["vel_z"] * dt)
            if node.getY() < -20:
                node.setY(25)
                node.setX(random.choice([random.uniform(-14, -10), random.uniform(10, 14)]))

        # Si estamos en el menú o game over, no actualizamos la lógica de combate
        if self.estado_juego != "JUGANDO":
            return Task.cont

        # Movimiento del jugador
        pos = self.player.getPos()
        dir_x = self.key_map["right"] - self.key_map["left"]
        dir_y = self.key_map["up"] - self.key_map["down"]
        nx = max(-9, min(9, pos.x + dir_x * self.velocidad_nave * dt))
        ny = max(-14, min(2, pos.y + dir_y * self.velocidad_nave * dt))
        self.player.setPos(nx, ny, 0)

        # Metralleta
        if self.key_map["fire"] and (task.time - self.ultimo_disparo > 0.12):
            self.ultimo_disparo = task.time
            bala = self.loader.loadModel("models/panda-model")
            bala.reparentTo(self.render)
            bala.setScale(0.001, 0.002, 0.001)
            bala.setColor(0, 1, 1, 1)
            bala.setPos(self.player.getX(), self.player.getY() + 1, 0)
            self.balas_jugador.append(bala)

        # Actualizar balas jugador
        for b in list(self.balas_jugador):
            b.setY(b.getY() + 40 * dt)
            if b.getY() > 20:
                b.removeNode()
                self.balas_jugador.remove(b)

        # Actualizar balas enemigas y daño
        for b in list(self.balas_enemigas):
            b.setY(b.getY() - 25 * dt)
            if (b.getPos() - self.player.getPos()).length() < 1.2:
                self.crear_explosion(self.player.getPos())
                b.removeNode()
                self.balas_enemigas.remove(b)
                self.vidas -= 1
                self.hud_texto.setText(self.actualizar_texto_hud())
                if self.vidas <= 0:
                    self.guardar_record()
                    self.player.hide()
                    self.estado_juego = "GAMEOVER"
                    self.gameover_texto.setText(
                        f"¡JUEGO TERMINADO!\n\n"
                        f"Puntaje Final: {self.puntaje}\n"
                        f"Record: {self.max_score}\n\n"
                        f"Presiona [ R ] para Reintentar\n"
                        f"Presiona [ M ] para ir al Menú"
                    )
                    self.gameover_texto.show()
                continue
            if b.getY() < -20:
                b.removeNode()
                self.balas_enemigas.remove(b)

        # Partículas
        for pt in list(self.particulas_explosion):
            pt["vida"] -= dt
            pt["node"].setPos(pt["node"].getPos() + pt["dir"] * dt)
            if pt["vida"] <= 0:
                pt["node"].removeNode()
                self.particulas_explosion.remove(pt)

        # Generar enemigos
        prob_spawn = 0.02 + (self.nivel * 0.008)
        lim_en = 4 + self.nivel
        if random.random() < prob_spawn and len(self.enemigos) < lim_en:
            en = self.loader.loadModel("models/panda-model")
            en.reparentTo(self.render)
            en.setScale(0.004, 0.004, 0.004)
            en.setColor(1, 0.2, 0.2, 1) # Panda enemigo rojo
            en.setPos(random.uniform(-8, 8), 18, 0)
            self.enemigos.append(en)

        # Actualizar enemigos
        for en in list(self.enemigos):
            vel_en = 8 + (self.nivel * 1.5)
            en.setY(en.getY() - vel_en * dt)
            
            # Disparo enemigo
            if random.random() < (0.015 + self.nivel * 0.003):
                b_en = self.loader.loadModel("models/panda-model")
                b_en.reparentTo(self.render)
                b_en.setScale(0.001, 0.002, 0.001)
                b_en.setColor(1, 0.5, 0, 1)
                b_en.setPos(en.getX(), en.getY() - 1, 0)
                self.balas_enemigas.append(b_en)

            # Colisiones
            for b in list(self.balas_jugador):
                if (en.getPos() - b.getPos()).length() < 1.5:
                    self.crear_explosion(en.getPos())
                    en.removeNode()
                    self.enemigos.remove(en)
                    b.removeNode()
                    self.balas_jugador.remove(b)
                    
                    self.puntaje += 100
                    self.nivel = 1 + (self.puntaje // 500)
                    self.hud_texto.setText(self.actualizar_texto_hud())
                    break

            if en in self.enemigos and en.getY() < -18:
                en.removeNode()
                self.enemigos.remove(en)

        return Task.cont

if __name__ == "__main__":
    app = ThunderaxCompleto()
    app.run()