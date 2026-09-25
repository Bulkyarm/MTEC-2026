"""
Geração da disposição de obstáculos e da posição do alvo para cada
combinação (fase, rodada). A dificuldade cresce com a fase (obstáculos
mais altos/numerosos) e um pouco também dentro da fase (alvo mais longe).
"""

import random
from settings import SCREEN_WIDTH, GROUND_Y, ARCHER_X
from entities import Obstacle, Target


def build_round(phase_index: int, round_index: int, scientist_name: str, seed=None):
    """
    Retorna (obstacles, target) para a fase/rodada atual.
    O seed é opcional, útil para tornar o layout determinístico em testes.
    """
    if seed is not None:
        random.seed(seed)

    # Dificuldade cresce com a fase (0 a 4): mais obstáculos e mais altos.
    num_obstacles = 1 + phase_index  # fase 0 -> 1 obstáculo, fase 4 -> 5 obstáculos
    base_height = 60 + phase_index * 25
    height_variation = 20 + round_index * 5

    middle_start = ARCHER_X + 150
    middle_end = SCREEN_WIDTH - 200
    usable_width = middle_end - middle_start

    obstacles = []
    slot_width = usable_width / max(num_obstacles, 1)
    for i in range(num_obstacles):
        slot_x = middle_start + i * slot_width
        # posição do obstáculo dentro do seu "slot", com uma margem
        obs_width = 26
        obs_x = slot_x + random.uniform(10, max(11, slot_width - obs_width - 10))
        obs_height = base_height + random.uniform(0, height_variation)
        obstacles.append(Obstacle(int(obs_x), obs_width, int(obs_height)))

    # Alvo: um pouco mais longe/alto conforme a rodada avança dentro da fase.
    target_x = SCREEN_WIDTH - 80
    target_y = GROUND_Y - 60 - round_index * 15 - phase_index * 5
    target = Target(target_x, int(target_y), scientist_name)

    return obstacles, target
