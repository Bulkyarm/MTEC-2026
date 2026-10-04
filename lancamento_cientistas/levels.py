"""
Geração da disposição de obstáculos e da posição do alvo para cada
combinação (fase, rodada). A dificuldade cresce com a fase (obstáculos
mais altos/numerosos) e um pouco também dentro da fase (alvo mais longe).
"""

from entities import Obstacle, Target


# Posicao inicial da bolinha na Fase 7, em pixels (centro x, centro y).
PHASE_7_TARGET_X = 780
PHASE_7_TARGET_Y = 100
# Multiplicador da gravidade: 1.0 e o padrao; maior cai mais rapido, menor mais devagar.
PHASE_7_TARGET_FALL_SPEED_MULTIPLIER = 1.0

# Cada item representa uma fase. Para criar mais cenarios, adicione outro
# dicionario com obstaculos e alvo seguindo este mesmo formato.
# Obstaculos: (x, y, largura, altura[, angulo]). O y indica o topo.
# Alvo: (x, y). As coordenadas sao pixels na tela.
FIXED_SCENARIOS = [
    # Fase 1: sem obstaculos; apenas ajuste target para mudar onde a bolinha aparece.
    {
        "obstacles": [],
        "target": (865, 455),
    },
    # Fase 2: uma barra horizontal bloqueia o caminho; x/y movem a barra,
    # largura/comprimento e altura mudam seu tamanho, e target move a bolinha.
    {
        "obstacles": [(100, 235, 500, 30)],
        "target": (900, 430),
    },
    # Fase 3: primeira parede baixa, segunda bem mais alta e barra inclinada
    # suspensa acima do alvo. Cada tupla controla posicao/tamanho; o ultimo
    # valor da barra superior altera sua inclinacao em graus.
    {
        "obstacles": [
            (230, 405, 30, 115),  # parede proxima: altura menor
            (455, 295, 30, 225),  # parede mais distante: altura maior
            (680, 335, 100, 24, -18),  # barreira inclinada, com espaco abaixo
        ],
        "target": (860, 488),
    },
    # Fase 4: corredor entre paredes; alvo fica no chao entre elas.
    # A primeira parede e alta, a segunda menor; alterar x muda a largura do corredor.
    {
        "obstacles": [
            (250, 275, 30, 245),  # parede alta antes do alvo
            (550, 405, 30, 115),  # parede menor depois do alvo
        ],
        "target": (450, 488),
    },
    # Fase 5: parede alta entre arqueiro e alvo elevado; o espaco depois dela
    # permite subir e ajustar o alcance para acertar a bolinha no ar.
    {
        "obstacles": [
            (390, 235, 32, 285),  # parede alta que exige uma trajetoria elevada
        ],
        "target": (845, 260),  # alvo no ar, aproximadamente na altura do topo
    },
    # Fase 6: teto comprido e duas paredes no chao deixam um corredor vertical
    # estreito. A primeira parede e alta; a segunda, menor, restringe o caminho.
    {
        "obstacles": [
            (250, 390, 32, 130),  # parede alta proxima do lancador
            (500, 440, 32, 80),  # parede menor mais adiante
            (100, 270, 650, 24),  # teto horizontal sobre as duas paredes
        ],
        "target": (700, 488),  # alvo no chao, depois das paredes e sob o teto
    },
    # Fase 7: sem obstaculos; target define a posicao da bolinha.
    {
        "obstacles": [],
        "target": (PHASE_7_TARGET_X, PHASE_7_TARGET_Y),
        "target_fall_speed_multiplier": PHASE_7_TARGET_FALL_SPEED_MULTIPLIER,
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
        fall_speed_multiplier=scenario.get("target_fall_speed_multiplier", 1.0),
    )

    return obstacles, target
