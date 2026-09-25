"""
Estado global do jogo: fase atual, rodada atual, pontuação e cientistas
já desbloqueadas. Persistido em um arquivo JSON simples.
"""

import json
import os
from settings import SAVE_FILE, ROUNDS_PER_PHASE, TOTAL_PHASES, POINTS_PER_HIT
from data.scientists import PHASES


class GameState:
    def __init__(self):
        self.phase_index = 0
        self.round_index = 0
        self.score = 0
        self.unlocked = []  # lista de dicts: {"phase", "name", "fact"}
        self.load()

    # ---------- Progressão ----------

    def current_phase(self):
        return PHASES[self.phase_index]

    def current_scientist(self):
        return self.current_phase()["scientists"][self.round_index]

    def register_hit(self):
        """Chamado quando o jogador acerta o alvo: pontua e desbloqueia a cientista."""
        self.score += POINTS_PER_HIT
        scientist = self.current_scientist()
        entry = {
            "phase": self.current_phase()["area"],
            "name": scientist["name"],
            "fact": scientist["fact"],
        }
        if entry not in self.unlocked:
            self.unlocked.append(entry)
        self.save()

    def advance_round(self):
        """Avança para a próxima rodada/fase. Retorna False se o jogo acabou."""
        self.round_index += 1
        if self.round_index >= ROUNDS_PER_PHASE:
            self.round_index = 0
            self.phase_index += 1
        self.save()
        return self.phase_index < TOTAL_PHASES

    def is_game_complete(self):
        return self.phase_index >= TOTAL_PHASES

    def reset(self):
        self.phase_index = 0
        self.round_index = 0
        self.score = 0
        self.unlocked = []
        self.save()

    # ---------- Persistência ----------

    def to_dict(self):
        return {
            "phase_index": self.phase_index,
            "round_index": self.round_index,
            "score": self.score,
            "unlocked": self.unlocked,
        }

    def save(self):
        os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.phase_index = data.get("phase_index", 0)
            self.round_index = data.get("round_index", 0)
            self.score = data.get("score", 0)
            self.unlocked = data.get("unlocked", [])
        except (json.JSONDecodeError, OSError):
            # save corrompido: começa do zero em vez de travar o jogo
            self.reset()

    def has_saved_progress(self):
        return os.path.exists(SAVE_FILE) and (self.score > 0 or self.unlocked)
