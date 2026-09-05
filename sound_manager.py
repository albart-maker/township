"""
Township - Procedural Sound Manager
Generates crisp synthesized audio cues using numpy and pygame.mixer.
Falls back gracefully if sound hardware is absent or disabled.
"""

import math
import numpy as np
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._generate_all_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio initialization notice: {e}. Running in silent mode.")
            self.enabled = False

    def _generate_all_sounds(self):
        sr = 44100

        def make_sound(samples):
            # samples is float32 between -1.0 and 1.0
            samples = np.clip(samples, -1.0, 1.0)
            int16_samples = (samples * 32767).astype(np.int16)
            stereo = np.column_stack((int16_samples, int16_samples))
            return pygame.sndarray.make_sound(stereo)

        # 1. Click
        t = np.linspace(0, 0.04, int(sr * 0.04), False)
        env = np.exp(-t * 100)
        wave = np.sin(2 * np.pi * 1200 * t) * env * 0.3
        self.sounds['click'] = make_sound(wave)

        # 2. Harvest (soft warm pluck/whoosh)
        t = np.linspace(0, 0.14, int(sr * 0.14), False)
        env = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 1.5
        freqs = np.linspace(400, 800, len(t))
        wave = np.sin(2 * np.pi * freqs * t) * env * 0.4
        self.sounds['harvest'] = make_sound(wave)

        # 3. Coin jingle (double high bell: B5 -> E6)
        dur1 = int(sr * 0.08)
        dur2 = int(sr * 0.18)
        t1 = np.linspace(0, 0.08, dur1, False)
        t2 = np.linspace(0, 0.18, dur2, False)
        bell1 = np.sin(2 * np.pi * 987 * t1) * np.exp(-t1 * 30) * 0.35
        bell2 = np.sin(2 * np.pi * 1318 * t2) * np.exp(-t2 * 18) * 0.4
        self.sounds['coin'] = make_sound(np.concatenate((bell1, bell2)))

        # 4. Level up fanfare (C5, E5, G5, C6 arpeggio)
        tones = [523.25, 659.25, 783.99, 1046.5]
        pieces = []
        for i, f in enumerate(tones):
            dur = 0.10 if i < 3 else 0.35
            tt = np.linspace(0, dur, int(sr * dur), False)
            decay = 15 if i < 3 else 8
            w = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * decay) * 0.45
            pieces.append(w)
        self.sounds['level_up'] = make_sound(np.concatenate(pieces))

        # 5. Helicopter rotor (rhythmic chop)
        dur = 0.6
        tt = np.linspace(0, dur, int(sr * dur), False)
        rotor_mod = (np.sin(2 * np.pi * 18 * tt) > 0).astype(float)
        base = np.sin(2 * np.pi * 110 * tt) * (0.3 + 0.7 * rotor_mod)
        env = np.sin(np.pi * np.linspace(0, 1, len(tt)))
        self.sounds['helicopter'] = make_sound(base * env * 0.3)

        # 6. Pop (bubble pop)
        t = np.linspace(0, 0.08, int(sr * 0.08), False)
        freq = np.linspace(700, 250, len(t))
        env = np.exp(-t * 40)
        self.sounds['pop'] = make_sound(np.sin(2 * np.pi * freq * t) * env * 0.35)

        # 7. Match-3 chime
        t = np.linspace(0, 0.18, int(sr * 0.18), False)
        w = (np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1760 * t)) * np.exp(-t * 20) * 0.35
        self.sounds['match'] = make_sound(w)

        # 8. Match-3 Combo sparkling chord
        t = np.linspace(0, 0.3, int(sr * 0.3), False)
        w = (np.sin(2 * np.pi * 659 * t) + np.sin(2 * np.pi * 880 * t) + np.sin(2 * np.pi * 1318 * t)) * np.exp(-t * 12) * 0.25
        self.sounds['combo'] = make_sound(w)

        # 9. Speedup whoosh
        t = np.linspace(0, 0.22, int(sr * 0.22), False)
        freq = np.linspace(300, 1200, len(t))
        env = np.sin(np.pi * np.linspace(0, 1, len(t)))
        self.sounds['speedup'] = make_sound(np.sin(2 * np.pi * freq * t) * env * 0.35)

        # 10. Error / Buzz
        t = np.linspace(0, 0.12, int(sr * 0.12), False)
        env = np.exp(-t * 25)
        buzz = (np.sin(2 * np.pi * 160 * t) > 0).astype(float) * 2 - 1
        self.sounds['error'] = make_sound(buzz * env * 0.25)

    def play(self, sound_name: str):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def toggle_sound(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

# Singleton instance
_sound_instance = None

def get_sound_manager() -> SoundManager:
    global _sound_instance
    if _sound_instance is None:
        _sound_instance = SoundManager()
    return _sound_instance
