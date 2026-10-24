"""
Geração da disposição de obstáculos e da posição do alvo para cada
combinação (fase, rodada). A dificuldade cresce com a fase (obstáculos
mais altos/numerosos) e um pouco também dentro da fase (alvo mais longe).
"""

from entities import Obstacle, Target
from settings import GROUND_Y


# Posicao do chimpanze desenhado no cenario da fase 7.
PHASE_7_TARGET_X = 860
PHASE_7_TARGET_Y = 132
# Multiplicador da gravidade: 1.0 e o padrao; maior cai mais rapido, menor mais devagar.
PHASE_7_TARGET_FALL_SPEED_MULTIPLIER = 1.0

PHASE_INTROS = [
    {
        "scientist": "Marie Curie",
        "fact": (
            "Foi pioneira no estudo da radioatividade e descobriu os elementos "
            "polônio e rádio. Foi a primeira pessoa a receber dois Prêmios Nobel "
            "em áreas científicas diferentes."
        ),
        "objective": "Acerte o botão para ligar a máquina de raio-X.",
    },
    {
        "scientist": "Emmy Noether",
        "fact": (
            "Matemática que revolucionou a álgebra. Seu teorema relaciona as "
            "simetrias da natureza às leis de conservação da física, como a "
            "conservação da energia."
        ),
        "objective": "Acerte o alvo para derrubar o giz e registrar o teorema.",
    },
    {
        "scientist": "Rosalind Franklin",
        "fact": (
            "Suas imagens de difração de raios X, incluindo a Foto 51, revelaram "
            "pistas fundamentais sobre a estrutura em dupla hélice do DNA."
        ),
        "objective": "Acerte o botão para baixar a barra e liberar a câmera.",
    },
    {
        "scientist": "Ada Lovelace",
        "fact": (
            "Escreveu o que é considerado o primeiro algoritmo destinado a ser "
            "executado por uma máquina e é reconhecida como pioneira da programação."
        ),
        "objective": (
            "Acerte a bolha para trazer a princesa e acender o carvão da "
            "Máquina Analítica."
        ),
    },
    {
        "scientist": "Lise Meitner",
        "fact": (
            "Ajudou a explicar teoricamente a fissão nuclear e a energia liberada "
            "nesse processo, contribuição essencial para a física nuclear."
        ),
        "objective": "Lance um nêutron por cima da barreira e acerte o átomo.",
    },
    {
        "scientist": "Barbara McClintock",
        "fact": (
            "Descobriu os transposons, segmentos de DNA capazes de mudar de "
            "posição no genoma, também conhecidos como genes saltadores."
        ),
        "objective": (
            "Acerte o alvo para baixar a barra e liberar o caminho até o "
            "microscópio."
        ),
    },
    {
        "scientist": "Jane Goodall",
        "fact": (
            "Estudou chimpanzés selvagens por décadas e mostrou que eles fabricam "
            "e usam ferramentas, transformando o conhecimento sobre esses animais."
        ),
        "objective": "Ajuste o lançamento da teia para alcançar o chimpanzé.",
    },
]

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
        "scientist_position": (700, 450),
        "scientist_machine_position": (760, 408),
        "machine_position": (835, 309),
        "target": (600, 500),
    },
    # Fase 2: barra horizontal bloqueia o caminho ate o alvo.
    {
        "obstacles": [(100, 235, 500, 30)],
        "target": (700, 430),
        "scientist_position": (30, 382),
        "scientist_end_x": 685,
        "blackboard_position": (750, 338),
        "chalk_position": (350, 209),
    },
    # Fase 3: duas barras sobre o chao, alvo ao lado da barra alta e camera suspensa.
    {
        "obstacles": [
            (240, 390, 32, 130),
            (470, 220, 32, 300),
            # Ajuste manual: (x, y, largura, altura) da barra sobre o botao.
            (550, 300, 100, 16),
        ],
        "target": (690, GROUND_Y - 36),
        "scientist_position": (420, 370),
        "scientist_end_x": 770,
        # A camera mede 150 px de altura; mantenha a base alinhada ao chao.
        "camera_position": (850, GROUND_Y - 150),
        "button_press_duration": 0.25,
        "bar_fall_duration": 0.8,
        "walk_duration": 2.0,
        "photo_duration": 0.75,
    },
    # Fase 4: Ada aciona a bolha para trazer a princesa e alimentar a maquina.
    {
        "obstacles": [  (240, 220, 32, 300),
                      (470, 390, 32, 130),
                      
                   
        ],
        "target": (450, 448),
        "scientist_position": (355, 380),
        "scientist_machine_x": 785,
        "machine_position": (830, 315),
        "furnace_position": (618, 342),
        "princess_x": 585,
        "princess_landing_y": GROUND_Y,
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
        "target": (600, 500),  # alvo para liberar Barbara e a passagem
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
        "scientist_position": (110, 310),
        "cliff_position": (90, 448),
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
