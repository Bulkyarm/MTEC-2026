"""
Geração da disposição de obstáculos e da posição do alvo para cada
combinação (fase, rodada). A dificuldade cresce com a fase (obstáculos
mais altos/numerosos) e um pouco também dentro da fase (alvo mais longe).
"""

from entities import Obstacle, Target


# Cada item representa uma fase. Para criar mais cenarios, adicione outro
# dicionario com obstaculos e alvo seguindo este mesmo formato.
# Obstaculos: (x, y, largura, altura). O y indica o topo do obstaculo.
# Alvo: (x, y). As coordenadas sao pixels na tela.
FIXED_SCENARIOS = [
    {
        "obstacles": [(260, 235, 30, 100)],
        "target": (865, 455),
    },
    {
        "obstacles": [(235, 235, 30, 200), (500, 355, 30, 85)],
        "target": (900, 430),
    },
    {
        "obstacles": [(225, 335, 30, 80), (420, 230, 30, 185), (650, 310, 30, 105)],
        "target": (850, 405),
    },
    {
        "obstacles": [(215, 210, 30, 190), (395, 320, 30, 95), (575, 180, 30, 220)],
        "target": (910, 450),
    },
    {
        "obstacles": [
            (205, 275, 30, 125),
            (365, 165, 30, 235),
            (530, 255, 30, 145),
            (700, 205, 30, 195),
        ],
        "target": (875, 390),
    },
]


def build_round(phase_index: int, round_index: int, scientist_name: str, seed=None):
    """
    Retorna (obstacles, target) para o cenario fixo da fase atual.
    O round_index e o seed continuam na assinatura para manter compatibilidade
    com chamadas e testes existentes.
    """
    scenario = FIXED_SCENARIOS[phase_index % len(FIXED_SCENARIOS)]
    obstacles = [Obstacle(x, y, width, height) for x, y, width, height in scenario["obstacles"]]
    target_x, target_y = scenario["target"]
    target = Target(target_x, int(target_y), scientist_name)

    return obstacles, target
