"""
Configurações globais do jogo: tela, cores, física e caminhos.
"""

# ---------- Janela ----------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Lançamento das Cientistas"

# ---------- Cores (R, G, B) ----------
COLOR_BG = (18, 24, 38)
COLOR_BG_GRADIENT_TOP = (30, 40, 66)
COLOR_GROUND = (46, 58, 89)
COLOR_WHITE = (240, 240, 245)
COLOR_BLACK = (10, 10, 15)
COLOR_GRAY = (120, 128, 145)
COLOR_LIGHT_GRAY = (200, 205, 215)
COLOR_ACCENT = (255, 196, 61)      # amarelo destaque (arco/flecha)
COLOR_OBSTACLE = (110, 80, 60)
COLOR_TARGET = (231, 76, 120)
COLOR_TARGET_HIT = (76, 201, 120)
COLOR_INPUT_BG = (35, 42, 64)
COLOR_INPUT_ACTIVE = (60, 72, 108)
COLOR_BUTTON = (76, 130, 201)
COLOR_BUTTON_HOVER = (96, 155, 230)
COLOR_DIALOG_BG = (25, 30, 48)
COLOR_SUCCESS = (76, 201, 120)
COLOR_FAIL = (220, 90, 90)

# ---------- Física ----------
GRAVITY = 9.8              # m/s^2 (valor "real", usado nas fórmulas mostradas ao jogador)
PIXELS_PER_METER = 12      # fator de conversão metros -> pixels na tela
MIN_ANGLE = 1
MAX_ANGLE = 89
MIN_VELOCITY = 5
MAX_VELOCITY = 60

# ---------- Jogo ----------
ARCHER_X = 90
ARCHER_Y = SCREEN_HEIGHT - 120
GROUND_Y = SCREEN_HEIGHT - 80

ROUNDS_PER_PHASE = 5
TOTAL_PHASES = 5
POINTS_PER_HIT = 10

SAVE_FILE = "save/progresso.json"
