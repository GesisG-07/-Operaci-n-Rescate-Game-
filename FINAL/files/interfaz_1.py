"""
interfaz_1.py — Operación Rescate: Cumbres Salvajes
Versión con sistema de MISIONES desbloqueables.

Incluye:
- Menú principal
- Mapa de misiones
- Misiones bloqueadas/desbloqueadas
- Drag & Drop
- Harmony Meter
- Análisis IA con Backtracking
- Pantalla de resultado
- Botón continuar para desbloquear la siguiente misión

Ejecutar:
    python interfaz_1.py

Debe estar junto a:
    Algoritmo_1.py
    assets/
"""

import pygame
import sys
import math
from pathlib import Path

try:
    from Algoritmo_1 import resolver_distribucion
    ALGORITMO_DISPONIBLE = True
except Exception:
    ALGORITMO_DISPONIBLE = False

pygame.init()

ANCHO, ALTO = 1366, 768
FPS = 60

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

CANTIDAD_EQUIPOS = 2
PERSONAS_POR_EQUIPO = 3

BLANCO = (245, 248, 252)
PANEL = (17, 25, 38)
PANEL2 = (22, 34, 50)
BORDE = (95, 120, 150)
DORADO = (255, 194, 72)
NARANJA = (255, 130, 55)
VERDE = (88, 220, 120)
AZUL = (80, 170, 250)
MORADO = (190, 105, 235)
ROJO = (230, 78, 75)
AMARILLO = (245, 210, 70)
GRIS = (165, 178, 198)

ROLES = {
    "Rastreadora": (VERDE, "R", "Rutas"),
    "Rastreador": (VERDE, "R", "Rutas"),
    "Paramédico": (AZUL, "+", "Soporte"),
    "Paramédica": (AZUL, "+", "Soporte"),
    "Escaladora": (NARANJA, "A", "Altura"),
    "Escalador": (NARANJA, "A", "Altura"),
    "Cargador": (MORADO, "C", "Carga"),
    "Cargadora": (MORADO, "C", "Carga"),
}

RESCATISTAS = [
    {"nombre": "Ana", "habilidad": 72, "rol": "Rastreadora"},
    {"nombre": "Luis", "habilidad": 68, "rol": "Paramédico"},
    {"nombre": "Marta", "habilidad": 75, "rol": "Escaladora"},
    {"nombre": "Carlos", "habilidad": 40, "rol": "Cargador"},
    {"nombre": "Sofía", "habilidad": 55, "rol": "Rastreadora"},
    {"nombre": "Tomás", "habilidad": 80, "rol": "Escalador"},
]

MISIONES = [
    {
        "nombre": "Sendero del Bosque",
        "sub": "Rescate del cachorro perdido",
        "bg": "bg_bosque.png",
        "objetivo": "Encuentra al cachorro antes del anochecer.",
        "tiempo": 120,
        "color": VERDE,
        "icono": "1",
    },
    {
        "nombre": "Campamento Bajo Tormenta",
        "sub": "Evacuación de campistas",
        "bg": "bg_nieve.png",
        "objetivo": "Evacúa a los campistas antes de la tormenta.",
        "tiempo": 100,
        "color": AZUL,
        "icono": "2",
    },
    {
        "nombre": "Risco Alto",
        "sub": "Gato atrapado en la cornisa",
        "bg": "bg_montana.png",
        "objetivo": "Rescata al gato sin romper el equilibrio del equipo.",
        "tiempo": 90,
        "color": NARANJA,
        "icono": "3",
    },
    {
        "nombre": "La Gran Avalancha",
        "sub": "Misión final de montaña",
        "bg": "bg_avalancha.png",
        "objetivo": "Forma el equipo perfecto para salvar montañistas.",
        "tiempo": 75,
        "color": ROJO,
        "icono": "F",
    },
]

FONTS = {}

def font(n, b=False):
    key = (n, b)
    if key not in FONTS:
        FONTS[key] = pygame.font.SysFont("segoeui", n, bold=b)
    return FONTS[key]

def text(s, t, x, y, n=18, c=BLANCO, b=False, align="center"):
    img = font(n, b).render(str(t), True, c)
    r = img.get_rect()
    if align == "center":
        r.center = (x, y)
    elif align == "left":
        r.midleft = (x, y)
    elif align == "right":
        r.midright = (x, y)
    s.blit(img, r)

def rr(s, r, c, rad=18, b=0, bc=BORDE):
    pygame.draw.rect(s, c, r, border_radius=rad)
    if b:
        pygame.draw.rect(s, bc, r, width=b, border_radius=rad)

def shadow(s, r, a=90, dy=8):
    lay = pygame.Surface((r.w + 22, r.h + 22), pygame.SRCALPHA)
    pygame.draw.rect(lay, (0, 0, 0, a), lay.get_rect(), border_radius=24)
    s.blit(lay, (r.x - 6, r.y + dy))

def star(cx, cy, rad):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = rad if i % 2 == 0 else rad * .45
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return pts

def skill_color(v):
    return VERDE if v >= 70 else AMARILLO if v >= 45 else ROJO

def nombre_archivo(nombre):
    """Quita tildes para armar el nombre de archivo (evita problemas de
    codificación al descomprimir .zip en distintos sistemas operativos)."""
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
    return nombre.translate(reemplazos)


class Button:
    def __init__(self, r, label, c, h):
        self.rect = pygame.Rect(r)
        self.label = label
        self.c = c
        self.h = h
        self.over = False

    def event(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.over = self.rect.collidepoint(e.pos)
        return e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos)

    def draw(self, s):
        shadow(s, self.rect, 70, 8)
        rr(s, self.rect, self.h if self.over else self.c, 16, 2, BORDE)
        text(s, self.label, self.rect.centerx, self.rect.centery, 18, BLANCO, True)


class Card:
    W, H = 155, 216

    def __init__(self, d, x, y):
        self.d = d
        self.origin = (x, y)
        self.rect = pygame.Rect(x, y, self.W, self.H)
        self.drag = False
        self.off = (0, 0)
        self.zone = None
        self.portrait = pygame.transform.smoothscale(
            pygame.image.load(ASSETS / f"{nombre_archivo(d['nombre'])}.png").convert_alpha(),
            (130, 150)
        )

    @property
    def nombre(self):
        return self.d["nombre"]

    @property
    def habilidad(self):
        return self.d["habilidad"]

    @property
    def rol(self):
        return self.d["rol"]

    def start(self, pos):
        if self.zone:
            self.zone.remove(self)
            self.zone = None
        self.drag = True
        self.off = (self.rect.x - pos[0], self.rect.y - pos[1])

    def move(self, pos):
        if self.drag:
            self.rect.x = pos[0] + self.off[0]
            self.rect.y = pos[1] + self.off[1]

    def drop(self, zones):
        self.drag = False
        for z in zones:
            if self.rect.colliderect(z.rect) and z.can():
                z.add(self)
                self.zone = z
                self.rect.center = z.slot(len(z.cards) - 1)
                return True

        self.rect.topleft = self.origin
        return False

    def draw(self, s):
        color, icon, desc = ROLES[self.rol]
        base = (28, 40, 58) if not self.rect.collidepoint(pygame.mouse.get_pos()) else (42, 58, 80)

        if self.drag:
            shadow(s, self.rect, 160, 12)
            base = (48, 68, 94)

        rr(s, self.rect, base, 20, 2, color)

        glow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 26), glow.get_rect(), border_radius=20)
        s.blit(glow, self.rect)

        pygame.draw.rect(s, color, (self.rect.x, self.rect.y, self.rect.w, 8), border_radius=7)
        s.blit(self.portrait, (self.rect.x + 12, self.rect.y + 12))

        text(s, self.rol.upper(), self.rect.x + 14, self.rect.y + 132, 10, color, True, "left")
        text(s, self.nombre, self.rect.x + 14, self.rect.y + 158, 24, BLANCO, True, "left")

        pygame.draw.circle(s, color, (self.rect.right - 30, self.rect.y + 158), 24)
        text(s, self.habilidad, self.rect.right - 30, self.rect.y + 158, 16, BLANCO, True)

        stars = max(1, min(5, round(self.habilidad / 20)))
        for i in range(5):
            pygame.draw.polygon(
                s,
                DORADO if i < stars else (68, 76, 90),
                star(self.rect.x + 20 + i * 21, self.rect.y + 188, 8),
            )

        bar = pygame.Rect(self.rect.x + 14, self.rect.bottom - 16, self.rect.w - 28, 8)
        rr(s, bar, (8, 14, 22), 5)
        fill = pygame.Rect(bar.x, bar.y, int(bar.w * self.habilidad / 100), bar.h)
        rr(s, fill, skill_color(self.habilidad), 5)


class Zone:
    def __init__(self, r, title, color):
        self.rect = pygame.Rect(r)
        self.title = title
        self.color = color
        self.cards = []
        self.active = False

    def can(self):
        return len(self.cards) < PERSONAS_POR_EQUIPO

    def add(self, c):
        self.cards.append(c)

    def remove(self, c):
        if c in self.cards:
            self.cards.remove(c)
            self.reflow()

    def reflow(self):
        for i, c in enumerate(self.cards):
            c.rect.center = self.slot(i)

    def slot(self, i):
        return self.rect.centerx, self.rect.y + 92 + i * 94

    def deviation(self):
        if len(self.cards) <= 1:
            return 0
        vals = [c.habilidad for c in self.cards]
        return max(vals) - min(vals)

    def draw(self, s):
        shadow(s, self.rect, 80, 8)
        rr(s, self.rect, (14, 32, 28) if self.active else (14, 22, 34), 18, 2, self.color)

        text(s, self.title, self.rect.centerx, self.rect.y + 26, 20, self.color, True)
        text(s, f"{len(self.cards)} / {PERSONAS_POR_EQUIPO}", self.rect.centerx, self.rect.y + 54, 14, BLANCO, True)

        for i in range(PERSONAS_POR_EQUIPO):
            sl = pygame.Rect(0, 0, self.rect.w - 38, 72)
            sl.center = self.slot(i)

            if i < len(self.cards):
                continue

            rr(s, sl, (10, 18, 28), 13, 2, (68, 84, 108))
            pygame.draw.circle(s, (55, 65, 82), (sl.centerx, sl.centery - 8), 15)
            pygame.draw.rect(s, (55, 65, 82), (sl.centerx - 24, sl.centery + 9, 48, 20), border_radius=8)


class Harmony:
    def __init__(self, r):
        self.rect = pygame.Rect(r)
        self.val = 0
        self.dev = 0
        self.opt = 0

    def update(self, zones, opt):
        self.dev = sum(z.deviation() for z in zones)
        self.opt = opt
        target = min(self.dev / 100, 1)
        self.val += (target - self.val) * .08

    def draw(self, s):
        shadow(s, self.rect, 95, 8)
        rr(s, self.rect, (16, 25, 39), 18, 2, BORDE)

        text(s, "HARMONY METER", self.rect.x + 26, self.rect.y + 32, 22, DORADO, True, "left")
        text(s, "Equilibrio total de equipos", self.rect.x + 26, self.rect.y + 60, 14, GRIS, False, "left")

        center = (self.rect.x + 170, self.rect.y + 158)
        radius = 98

        for i in range(0, 101, 2):
            ang = math.radians(200 - i * 2.2)
            x1 = center[0] + math.cos(ang) * (radius - 13)
            y1 = center[1] - math.sin(ang) * (radius - 13)
            x2 = center[0] + math.cos(ang) * radius
            y2 = center[1] - math.sin(ang) * radius
            c = VERDE if i < 35 else AMARILLO if i < 65 else ROJO
            pygame.draw.line(s, c, (x1, y1), (x2, y2), 4)

        ang = math.radians(200 - self.val * 220)
        px = center[0] + math.cos(ang) * (radius - 28)
        py = center[1] - math.sin(ang) * (radius - 28)

        c = VERDE if self.val < .35 else AMARILLO if self.val < .65 else ROJO
        pygame.draw.line(s, c, center, (px, py), 7)
        pygame.draw.circle(s, BLANCO, center, 12)
        pygame.draw.circle(s, c, center, 7)

        pct = max(0, 100 - self.dev)
        text(s, f"{pct}%", self.rect.right - 100, self.rect.y + 118, 42, c, True)

        state = "ARMONIOSO" if self.val < .35 else "MODERADO" if self.val < .65 else "RIESGOSO"
        text(s, state, self.rect.right - 100, self.rect.y + 163, 18, c, True)
        text(s, f"Desviación: {self.dev}", self.rect.right - 100, self.rect.y + 204, 14, GRIS)
        text(s, f"Óptimo IA: {self.opt}" if self.opt else "Sin analizar", self.rect.right - 100, self.rect.y + 228, 14, VERDE if self.opt else GRIS, True)


class Game:
    def __init__(self):
        pygame.display.set_caption("Operación Rescate: Cumbres Salvajes — Misiones")
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        self.clock = pygame.time.Clock()

        self.state = "menu"
        self.mission_i = 0
        self.mission = MISIONES[0]

        self.unlocked = 1
        self.stars_by_mission = [0 for _ in MISIONES]

        self.backgrounds = {
            m["bg"]: pygame.transform.smoothscale(pygame.image.load(ASSETS / m["bg"]).convert(), (ANCHO, ALTO))
            for m in MISIONES
        }

        self.btn_play = Button((ANCHO // 2 - 150, 445, 300, 64), "JUGAR", (165, 88, 42), (220, 118, 55))
        self.btn_missions = Button((ANCHO // 2 - 150, 525, 300, 56), "MAPA DE MISIONES", (56, 91, 140), (72, 124, 190))
        self.btn_exit = Button((ANCHO // 2 - 150, 595, 300, 56), "SALIR", (78, 86, 104), (110, 122, 145))

        self.btn_back = Button((35, 28, 150, 44), "← MENÚ", (70, 86, 108), (98, 118, 145))
        self.btn_back_game = Button((25, 122, 160, 44), "← MISIONES", (70, 86, 108), (98, 118, 145))

        self.btn_ai = Button((780, 650, 220, 55), "ANALIZAR IA", (48, 145, 75), (80, 205, 110))
        self.btn_send = Button((1020, 650, 220, 55), "ENVIAR", (38, 115, 180), (62, 160, 235))
        self.btn_clear = Button((1247, 650, 95, 55), "LIMPIAR", (78, 86, 104), (110, 122, 145))
        self.btn_continue = Button((ANCHO // 2 - 145, 605, 290, 58), "CONTINUAR", (165, 88, 42), (220, 118, 55))

        self.new()

    def new(self):
        self.cards = [
            Card(d.copy(), 280 + (i % 3) * 165, 150 + (i // 3) * 235)
            for i, d in enumerate(RESCATISTAS)
        ]

        self.zones = [
            Zone((870, 205, 185, 380), "EQUIPO 1", VERDE),
            Zone((1085, 205, 185, 380), "EQUIPO 2", AZUL),
        ]

        self.harmony = Harmony((275, 575, 470, 160))
        self.drag = None
        self.opt = 0
        self.ai = None
        self.result = False
        self.analysis = False
        self.analysis_start = 0
        self.start = pygame.time.get_ticks()
        self.kits = 3
        self.last_stars = 0

    def run_ai(self):
        if not ALGORITMO_DISPONIBLE:
            print("⚠️ Algoritmo_1.py no encontrado.")
            return

        try:
            res = resolver_distribucion(
                [{"nombre": c.nombre, "habilidad": c.habilidad} for c in self.cards],
                cantidad_equipos=CANTIDAD_EQUIPOS,
                guardar_historial=False,
            )
            self.ai = res
            self.opt = res["mejor_desviacion"]
            print("✅ IA:", self.opt, res["estadisticas"])
        except Exception as e:
            print("❌ Error IA:", e)

    def complete(self):
        return all(len(z.cards) == PERSONAS_POR_EQUIPO for z in self.zones)

    def dev(self):
        return sum(z.deviation() for z in self.zones)

    def stars(self):
        if self.opt == 0:
            return 3 if self.dev() == 0 else 1
        ratio = self.dev() / self.opt
        if ratio <= 1:
            return 3
        if ratio <= 1.5:
            return 2
        return 1

    def finish_mission(self):
        self.last_stars = self.stars()
        if self.last_stars > self.stars_by_mission[self.mission_i]:
            self.stars_by_mission[self.mission_i] = self.last_stars
        if self.mission_i + 1 < len(MISIONES):
            self.unlocked = max(self.unlocked, self.mission_i + 2)

    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if e.key == pygame.K_r and self.state == "game":
                    self.new()

            if self.state == "menu":
                if self.btn_play.event(e):
                    self.state = "missions"
                if self.btn_missions.event(e):
                    self.state = "missions"
                if self.btn_exit.event(e):
                    pygame.quit()
                    sys.exit()

            elif self.state == "missions":
                if self.btn_back.event(e):
                    self.state = "menu"

                for i, m in enumerate(MISIONES):
                    rect = self.mission_card_rect(i)
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and rect.collidepoint(e.pos):
                        if i < self.unlocked:
                            self.mission_i = i
                            self.mission = MISIONES[i]
                            self.new()
                            self.state = "game"
                        else:
                            print("🔒 Misión bloqueada. Completa la anterior.")

            elif self.state == "game":
                if self.btn_back_game.event(e):
                    self.state = "missions"

                if self.result:
                    if self.btn_continue.event(e):
                        self.state = "missions"
                    continue

                if self.btn_ai.event(e) and not self.analysis:
                    self.analysis = True
                    self.analysis_start = pygame.time.get_ticks()

                if self.btn_clear.event(e):
                    self.new()

                if self.btn_send.event(e):
                    if self.complete():
                        if self.ai is None:
                            self.run_ai()
                        self.finish_mission()
                        self.result = True
                    else:
                        print("⚠️ Completa los dos equipos.")

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not self.analysis:
                    for z in self.zones:
                        for c in reversed(z.cards):
                            if c.rect.collidepoint(e.pos):
                                c.start(e.pos)
                                self.drag = c
                                return

                    for c in reversed(self.cards):
                        if c.rect.collidepoint(e.pos) and c.zone is None:
                            c.start(e.pos)
                            self.drag = c
                            return

                if e.type == pygame.MOUSEMOTION and self.drag:
                    self.drag.move(e.pos)
                    for z in self.zones:
                        z.active = z.rect.collidepoint(e.pos)

                if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.drag:
                    self.drag.drop(self.zones)
                    self.drag = None
                    for z in self.zones:
                        z.active = False

    def menu(self):
        self.screen.blit(self.backgrounds["bg_bosque.png"], (0, 0))
        shade = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 92))
        self.screen.blit(shade, (0, 0))

        box = pygame.Rect(ANCHO // 2 - 290, 105, 580, 300)
        shadow(self.screen, box, 150, 12)
        rr(self.screen, box, (15, 24, 36), 30, 3, DORADO)

        text(self.screen, "OPERACIÓN", box.centerx, box.y + 92, 68, DORADO, True)
        text(self.screen, "RESCATE", box.centerx, box.y + 170, 82, NARANJA, True)
        text(self.screen, "CUMBRES SALVAJES", box.centerx, box.y + 240, 26, BLANCO, True)

        text(self.screen, "Sistema de misiones con Backtracking y Podas", ANCHO // 2, 420, 19, BLANCO)
        self.btn_play.draw(self.screen)
        self.btn_missions.draw(self.screen)
        self.btn_exit.draw(self.screen)

        text(
            self.screen,
            "Algoritmo_1.py conectado ✓" if ALGORITMO_DISPONIBLE else "Algoritmo_1.py no encontrado",
            ANCHO // 2,
            690,
            16,
            VERDE if ALGORITMO_DISPONIBLE else ROJO,
            True,
        )

    def mission_card_rect(self, i):
        x = 170 + (i % 2) * 530
        y = 170 + (i // 2) * 210
        return pygame.Rect(x, y, 480, 155)

    def missions(self):
        self.screen.blit(self.backgrounds["bg_montana.png"], (0, 0))
        shade = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 115))
        self.screen.blit(shade, (0, 0))

        self.btn_back.draw(self.screen)

        text(self.screen, "MAPA DE MISIONES", ANCHO // 2, 80, 44, DORADO, True)
        text(self.screen, "Completa una misión para desbloquear la siguiente.", ANCHO // 2, 120, 18, BLANCO)

        for i, m in enumerate(MISIONES):
            rect = self.mission_card_rect(i)
            unlocked = i < self.unlocked
            completed = self.stars_by_mission[i] > 0

            color = m["color"] if unlocked else (75, 80, 95)
            shadow(self.screen, rect, 95, 8)
            rr(self.screen, rect, (18, 28, 42), 22, 3, color)

            pygame.draw.circle(self.screen, color, (rect.x + 58, rect.y + 58), 34)
            text(self.screen, m["icono"], rect.x + 58, rect.y + 58, 28, BLANCO, True)

            title = m["nombre"] if unlocked else "MISIÓN BLOQUEADA"
            sub = m["sub"] if unlocked else "Completa la misión anterior"
            text(self.screen, title, rect.x + 115, rect.y + 45, 23, BLANCO if unlocked else GRIS, True, "left")
            text(self.screen, sub, rect.x + 115, rect.y + 78, 16, GRIS, False, "left")
            text(self.screen, f"Tiempo: {m['tiempo']}s", rect.x + 115, rect.y + 108, 15, DORADO if unlocked else GRIS, True, "left")

            if completed:
                for st in range(3):
                    pygame.draw.polygon(
                        self.screen,
                        DORADO if st < self.stars_by_mission[i] else (70, 80, 95),
                        star(rect.right - 105 + st * 35, rect.y + 52, 13),
                    )
                text(self.screen, "COMPLETADA", rect.right - 85, rect.y + 105, 14, VERDE, True)
            elif unlocked:
                text(self.screen, "DISPONIBLE", rect.right - 85, rect.y + 80, 15, VERDE, True)
            else:
                text(self.screen, "BLOQUEADA", rect.right - 85, rect.y + 80, 15, ROJO, True)

    def hud(self):
        logo = pygame.Rect(25, 24, 210, 92)
        rr(self.screen, logo, (15, 24, 36), 18, 2, DORADO)
        text(self.screen, "OPERACIÓN", logo.centerx, logo.y + 32, 28, DORADO, True)
        text(self.screen, "RESCATE", logo.centerx, logo.y + 64, 35, NARANJA, True)

        mb = pygame.Rect(420, 25, 430, 80)
        rr(self.screen, mb, (15, 24, 36), 18, 2, self.mission["color"])
        text(self.screen, "MISIÓN ACTIVA", mb.centerx, mb.y + 25, 18, DORADO, True)
        text(self.screen, self.mission["nombre"].upper(), mb.centerx, mb.y + 55, 23, BLANCO, True)

        rem = max(0, self.mission["tiempo"] - (pygame.time.get_ticks() - self.start) // 1000)
        tb = pygame.Rect(900, 25, 160, 80)
        rr(self.screen, tb, (15, 24, 36), 18, 2, DORADO)
        text(self.screen, "TIEMPO", tb.centerx, tb.y + 25, 16, DORADO, True)
        text(self.screen, f"{rem}s", tb.centerx, tb.y + 58, 30, VERDE if rem > 45 else AMARILLO if rem > 20 else ROJO, True)

        kb = pygame.Rect(1090, 25, 160, 80)
        rr(self.screen, kb, (15, 24, 36), 18, 2, ROJO)
        text(self.screen, "KITS", kb.centerx, kb.y + 25, 16, DORADO, True)
        text(self.screen, f"{self.kits} / 3", kb.centerx, kb.y + 58, 30, BLANCO, True)

        self.btn_back_game.draw(self.screen)

    def objective(self):
        p = pygame.Rect(25, 548, 220, 160)
        shadow(self.screen, p, 100, 8)
        rr(self.screen, p, (18, 28, 42), 18, 2, DORADO)
        text(self.screen, "OBJETIVO", p.x + 18, p.y + 30, 18, DORADO, True, "left")

        words = self.mission["objetivo"].split()
        lines, line = [], ""
        for w in words:
            if len(line + " " + w) < 24:
                line += (" " if line else "") + w
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)

        for i, l in enumerate(lines[:4]):
            text(self.screen, l, p.x + 18, p.y + 68 + i * 23, 15, BLANCO, False, "left")

    def game(self):
        self.screen.blit(self.backgrounds[self.mission["bg"]], (0, 0))
        shade = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 45))
        self.screen.blit(shade, (0, 0))

        self.hud()
        self.objective()

        pc = pygame.Rect(260, 128, 535, 435)
        shadow(self.screen, pc, 80, 8)
        rr(self.screen, pc, (20, 30, 44), 22, 2, BORDE)
        text(self.screen, "RESCATISTAS DISPONIBLES", pc.x + 28, pc.y + 32, 22, DORADO, True, "left")

        pz = pygame.Rect(820, 128, 480, 500)
        shadow(self.screen, pz, 80, 8)
        rr(self.screen, pz, (20, 30, 44), 22, 2, BORDE)
        text(self.screen, "ZONA DE EXPEDICIÓN", pz.centerx, pz.y + 35, 28, DORADO, True)
        text(self.screen, "Arrastra los rescatistas para formar los equipos", pz.centerx, pz.y + 68, 15, BLANCO)

        for z in self.zones:
            z.draw(self.screen)

        self.harmony.update(self.zones, self.opt)
        self.harmony.draw(self.screen)

        self.btn_ai.draw(self.screen)
        self.btn_send.draw(self.screen)
        self.btn_clear.draw(self.screen)

        roles = pygame.Rect(1020, 565, 320, 75)
        rr(self.screen, roles, (18, 28, 42), 16, 2, DORADO)
        text(self.screen, "ROLES", roles.x + 18, roles.y + 22, 15, DORADO, True, "left")

        for i, (ic, c, d) in enumerate([("R", VERDE, "Rutas"), ("+", AZUL, "Soporte"), ("A", NARANJA, "Altura"), ("C", MORADO, "Carga")]):
            x = roles.x + 20 + i * 75
            pygame.draw.circle(self.screen, c, (x, roles.y + 52), 11)
            text(self.screen, ic, x, roles.y + 52, 12, BLANCO, True)
            text(self.screen, d, x + 18, roles.y + 52, 12, BLANCO, False, "left")

        for c in self.cards:
            if c.zone is None and not c.drag:
                c.draw(self.screen)

        for z in self.zones:
            for c in z.cards:
                if not c.drag:
                    self.compact(c)

        if self.drag:
            self.drag.draw(self.screen)

        if self.analysis:
            self.analysis_overlay()

        if self.result:
            self.result_overlay()

    def compact(self, c):
        r = pygame.Rect(0, 0, c.zone.rect.w - 38, 72)
        r.center = c.rect.center
        color = ROLES[c.rol][0]
        rr(self.screen, r, (25, 36, 52), 13, 2, color)
        pygame.draw.circle(self.screen, color, (r.x + 35, r.centery), 22)
        text(self.screen, ROLES[c.rol][1], r.x + 35, r.centery, 16, BLANCO, True)
        text(self.screen, c.nombre, r.x + 66, r.y + 26, 16, BLANCO, True, "left")
        text(self.screen, c.rol, r.x + 66, r.y + 50, 11, color, True, "left")
        text(self.screen, c.habilidad, r.right - 24, r.centery, 17, color, True)

    def analysis_overlay(self):
        e = pygame.time.get_ticks() - self.analysis_start

        if e > 1600:
            self.analysis = False
            self.run_ai()
            return

        ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        self.screen.blit(ov, (0, 0))

        b = pygame.Rect(ANCHO // 2 - 250, ALTO // 2 - 115, 500, 230)
        shadow(self.screen, b, 140, 12)
        rr(self.screen, b, (18, 28, 42), 24, 3, VERDE)

        text(self.screen, "ANALIZANDO COMBINACIONES", b.centerx, b.y + 55, 25, DORADO, True)
        text(self.screen, "Backtracking + podas en ejecución", b.centerx, b.y + 88, 17, BLANCO)

        prog = min(1, e / 1600)
        bar = pygame.Rect(b.x + 70, b.y + 140, b.w - 140, 24)
        rr(self.screen, bar, (10, 15, 22), 12)
        rr(self.screen, pygame.Rect(bar.x, bar.y, int(bar.w * prog), bar.h), VERDE, 12)

        text(self.screen, "Buscando equipo óptimo" + "." * (1 + (e // 300) % 3), b.centerx, b.y + 185, 16, GRIS)

    def result_overlay(self):
        ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 185))
        self.screen.blit(ov, (0, 0))

        p = pygame.Rect(ANCHO // 2 - 330, ALTO // 2 - 250, 660, 500)
        shadow(self.screen, p, 160, 12)
        rr(self.screen, p, (18, 28, 42), 26, 3, DORADO)

        text(self.screen, "MISIÓN COMPLETADA", p.centerx, p.y + 58, 40, DORADO, True)
        text(self.screen, self.mission["sub"], p.centerx, p.y + 98, 19, BLANCO)

        for i in range(3):
            pygame.draw.polygon(
                self.screen,
                DORADO if i < self.last_stars else (70, 80, 95),
                star(p.centerx - 90 + i * 90, p.y + 170, 38),
            )

        text(self.screen, f"Tu desviación total: {self.dev()}", p.centerx, p.y + 260, 22, BLANCO, True)
        text(self.screen, f"Óptimo IA: {self.opt}", p.centerx, p.y + 300, 22, VERDE, True)

        if self.mission_i + 1 < len(MISIONES):
            text(self.screen, "Nueva misión desbloqueada", p.centerx, p.y + 350, 20, VERDE, True)
        else:
            text(self.screen, "Todas las misiones completadas", p.centerx, p.y + 350, 20, VERDE, True)

        self.btn_continue.draw(self.screen)

    def draw(self):
        if self.state == "menu":
            self.menu()
        elif self.state == "missions":
            self.missions()
        elif self.state == "game":
            self.game()

        pygame.display.flip()

    def run(self):
        while True:
            self.events()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
