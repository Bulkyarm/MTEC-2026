"""Audio synth utilities for the game, generated at runtime with Pygame."""

import array
import logging
import math

import pygame


LOGGER = logging.getLogger(__name__)


class GameAudio:
    SAMPLE_RATE = 22050
    MAX_TENSION_ERRORS = 4
    TEMPO_PER_ERROR = 0.18

    def __init__(self):
        self.available = False
        self.volume = 0.7
        self.muted = False
        self.tension_errors = 0
        self._next_effect_channel = 0
        self._effect_channels = []

        try:
            if pygame.mixer.get_init() != (self.SAMPLE_RATE, -16, 1):
                pygame.mixer.quit()
                pygame.mixer.init(
                    frequency=self.SAMPLE_RATE,
                    size=-16,
                    channels=1,
                    buffer=512,
                )
        except pygame.error as error:
            LOGGER.error("Audio mixer could not be initialized: %s", error)
            return

        pygame.mixer.set_num_channels(6)
        self._music_channel = pygame.mixer.Channel(0)
        self._effect_channels = [
            pygame.mixer.Channel(index) for index in range(1, 6)
        ]
        self._sounds = self._create_sounds()
        self._music_tracks = [
            self._make_music(1 + self.TEMPO_PER_ERROR * errors)
            for errors in range(self.MAX_TENSION_ERRORS + 1)
        ]
        self.available = True
        self._update_channel_volumes()
        self._music_channel.play(self._music_tracks[0], loops=-1)

    def _make_tone(self, frequency, duration, volume=0.3, end_frequency=None):
        sample_count = max(1, round(self.SAMPLE_RATE * duration))
        samples = array.array("h")
        for index in range(sample_count):
            progress = index / sample_count
            current_frequency = frequency
            if end_frequency is not None:
                current_frequency += (end_frequency - frequency) * progress
            envelope = min(1.0, index / (self.SAMPLE_RATE * 0.012))
            envelope *= min(1.0, (sample_count - index) / (self.SAMPLE_RATE * 0.025))
            sample = math.sin(
                2 * math.pi * current_frequency * index / self.SAMPLE_RATE
            )
            samples.append(round(32767 * volume * envelope * sample))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _make_music(self, tempo=1.0):
        melody = (
            (261.63, 0.55), (329.63, 0.55), (392.00, 0.55), (329.63, 0.55),
            (293.66, 0.55), (349.23, 0.55), (440.00, 0.55), (349.23, 0.55),
        )
        samples = array.array("h")
        for note_index, (frequency, duration) in enumerate(melody):
            duration /= tempo
            count = round(self.SAMPLE_RATE * duration)
            for index in range(count):
                progress = index / count
                envelope = min(1.0, index / (self.SAMPLE_RATE * 0.04))
                envelope *= min(
                    1.0, (count - index) / (self.SAMPLE_RATE * 0.06)
                )
                time = index / self.SAMPLE_RATE
                pad_frequency = 130.81 if note_index < 4 else 146.83
                value = (
                    math.sin(2 * math.pi * frequency * time) * 0.16
                    + math.sin(2 * math.pi * pad_frequency * time) * 0.08
                )
                samples.append(round(32767 * envelope * value))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _make_sequence(self, notes):
        sounds = [
            self._make_tone(frequency, duration, volume)
            for frequency, duration, volume in notes
        ]
        total_samples = sum(len(sound.get_raw()) for sound in sounds)
        buffer = bytearray()
        for sound in sounds:
            buffer.extend(sound.get_raw())
        if not buffer or total_samples == 0:
            raise ValueError("Audio sequence must contain at least one note.")
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_sounds(self):
        return {
            "launch": self._make_tone(
                620, 0.32, volume=0.35, end_frequency=170,
            ),
            "hit": self._make_sequence((
                (660, 0.10, 0.3),
                (880, 0.16, 0.28),
            )),
            "miss": self._make_tone(
                260, 0.26, volume=0.25, end_frequency=145,
            ),
            "ui": self._make_tone(740, 0.045, volume=0.16),
            "phase": self._make_sequence((
                (523.25, 0.12, 0.24),
                (659.25, 0.12, 0.24),
                (783.99, 0.22, 0.24),
            )),
        }

    def _update_channel_volumes(self):
        if not self.available:
            return
        volume = 0.0 if self.muted else self.volume
        self._music_channel.set_volume(volume * 0.22)
        for channel in self._effect_channels:
            channel.set_volume(volume)

    def play(self, sound_name):
        if not self.available or self.muted:
            return
        sound = self._sounds[sound_name]
        channel = self._effect_channels[self._next_effect_channel]
        self._next_effect_channel = (
            self._next_effect_channel + 1
        ) % len(self._effect_channels)
        channel.play(sound)

    def set_tension(self, errors):
        tension_errors = min(self.MAX_TENSION_ERRORS, max(0, errors))
        if tension_errors == self.tension_errors:
            return
        self.tension_errors = tension_errors
        if self.available and self._music_channel.get_busy():
            self._music_channel.play(
                self._music_tracks[self.tension_errors], loops=-1,
            )

    def change_volume(self, amount):
        self.volume = min(1.0, max(0.0, self.volume + amount))
        self._update_channel_volumes()

    def toggle_mute(self):
        self.muted = not self.muted
        self._update_channel_volumes()
