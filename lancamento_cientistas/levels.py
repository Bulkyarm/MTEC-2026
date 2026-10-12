"""
Geração da disposição de obstáculos e da posição do alvo para cada
combinação (fase, rodada). A dificuldade cresce com a fase (obstáculos
mais altos/numerosos) e um pouco também dentro da fase (alvo mais longe).
"""

from entities import Obstacle, Target


# Posicao do chimpanze desenhado no cenario da fase 7.
PHASE_7_TARGET_X = 860
PHASE_7_TARGET_Y = 132
# Multiplicador da gravidade: 1.0 e o padrao; maior cai mais rapido, menor mais devagar.
PHASE_7_TARGET_FALL_SPEED_MULTIPLIER = 1.0

# Cada item representa uma fase. Para criar mais cenarios, adicione outro
# dicionario com obstaculos e alvo seguindo este mesmo formato.
# Obstaculos: (x, y, largura, altura[, angulo]). O y indica o topo.
# Alvo: (x, y). As coordenadas sao pixels na tela.
FIXED_SCENARIOS = [
    # Fase 1: ajuste aqui as posicoes (em pixels) da Marie e da maquina.
    # scientist_position e machine_position usam o canto superior esquerdo;
    # scientist_machine_position define onde a Marie termina a caminhada;
    # target e o centro do botao de ligar o raio-X.
    {
        "obstacles": [],
        "scientist_position": (700, 408),
        "scientist_machine_position": (785, 408),
        "machine_position": (835, 309),
        "target": (670, 400),
    },
    # Fase 2: barra horizontal bloqueia o caminho ate o alvo.
    {
        "obstacles": [(100, 235, 500, 30)],
        "target": (900, 430),
        "scientist_position": (30, 382),
        "scientist_end_x": 720,
        "blackboard_position": (790, 115),
        "chalk_position": (350, 211),
    },
    # Fase 3: Rosalind fica entre as barras; a maior desce ao acertar o botao.
    {
        "obstacles": [
            (250, 315, 28, 205),
            (675, 205, 30, 315),
        ],
        "target": (510, 438),
        "scientist_position": (420, 370),
        "scientist_end_x": 770,
        "camera_position": (805, 347),
        "button_size": (72, 72),
        "button_press_duration": 0.25,
        "bar_fall_duration": 0.8,
        "walk_duration": 2.0,
        "photo_duration": 0.75,
    },
    # Fase 4: Ada aciona a bolha para trazer a princesa e alimentar a maquina.
    {
        "obstacles": [],
        "target": (450, 448),
        "scientist_position": (355, 380),
        "scientist_machine_x": 785,
        "machine_position": (830, 315),
        "furnace_position": (618, 342),
        "princess_x": 585,
        "princess_landing_y": 510,
        "princess_fall_duration": 1.6,
        "fire_duration": 0.7,
        "machine_duration": 2.0,
    },
    # Fase 5: Lise dispara neutrons contra o atomo, transpondo a parede alta.
    {
        "obstacles": [
            (390, 235, 32, 285),  # barreira que exige uma trajetoria elevada
        ],
        "target": (845, 260),
        "target_radius": 40,
        "scientist_position": (22, 384),
    },
    # Fase 6: Barbara fica entre as paredes; a menor desce para abrir passagem
    # ate o laboratorio sem remover o teto nem a parede alta.
    {
        "obstacles": [
            (250, 390, 32, 130),  # parede alta proxima do lancador
            (500, 440, 32, 80),  # parede menor mais adiante
            (100, 270, 650, 24),  # teto horizontal sobre as duas paredes
        ],
        "target": (675, 370),  # alvo para liberar Barbara e a passagem
        "scientist_position": (345, 394),
        "scientist_end_x": 722,
        "laboratory_position": (704, 322),
        "bar_fall_duration": 0.8,
        "walk_duration": 2.4,
        "sit_duration": 0.7,
        "microscope_duration": 0.8,
        "transposon_frame_duration": 0.8,
    },
    # Fase 7: Jane observa um chimpanze na copa da arvore.
    {
        "obstacles": [],
        "target": (PHASE_7_TARGET_X, PHASE_7_TARGET_Y),
        "target_radius": 34,
        "target_fall_speed_multiplier": PHASE_7_TARGET_FALL_SPEED_MULTIPLIER,
        "scientist_position": (110, 374),
        "forest_position": (0, 0),
    },
]


def build_round(phase_index: int, round_index: int, scientist_name: str, seed=None):
    """
    Retorna (obstacles, target) para o cenario fixo da fase atual.
    O round_index e o seed continuam na assinatura para manter compatibilidade
    com chamadas e testes existentes.
    """
    scenario = FIXED_SCENARIOS[phase_index % len(FIXED_SCENARIOS)]
    obstacles = [Obstacle(*obstacle) for obstacle in scenario["obstacles"]]
    target_x, target_y = scenario["target"]
    target = Target(
        target_x,
        int(target_y),
        scientist_name,
        radius=scenario.get("target_radius", 32),
        fall_speed_multiplier=scenario.get("target_fall_speed_multiplier", 1.0),
    )

    return obstacles, target
