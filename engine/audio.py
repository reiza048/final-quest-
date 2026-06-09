"""
engine/audio.py - Audio Manager
================================
Mengelola musik latar dan efek suara.
Menggunakan pygame.mixer untuk playback.
"""

import pygame
import os


class AudioManager:
    """Mengelola BGM dan SFX."""

    def __init__(self):
        self.initialized = False
        self.bgm_volume = 0.5
        self.sfx_volume = 0.7
        self.sounds = {}

    def init(self):
        """Initialize audio mixer."""
        try:
            pygame.mixer.init(44100, -16, 2, 512)
            self.initialized = True
        except pygame.error:
            print("[Audio] Mixer gagal diinisialisasi, audio dinonaktifkan.")
            self.initialized = False

    def load_sound(self, name, filepath):
        """Load sound effect."""
        if not self.initialized:
            return
        if os.path.exists(filepath):
            try:
                self.sounds[name] = pygame.mixer.Sound(filepath)
                self.sounds[name].set_volume(self.sfx_volume)
            except pygame.error:
                print(f"[Audio] Gagal load sound: {filepath}")

    def play_sound(self, name):
        """Play sound effect."""
        if not self.initialized:
            return
        if name in self.sounds:
            self.sounds[name].play()

    def play_bgm(self, filepath, loops=-1):
        """Play background music."""
        if not self.initialized:
            return
        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(loops)
            except pygame.error:
                print(f"[Audio] Gagal load BGM: {filepath}")

    def stop_bgm(self):
        """Stop background music."""
        if self.initialized:
            pygame.mixer.music.stop()

    def set_bgm_volume(self, vol):
        """Set volume BGM (0.0 - 1.0)."""
        self.bgm_volume = max(0, min(1, vol))
        if self.initialized:
            pygame.mixer.music.set_volume(self.bgm_volume)

    def set_sfx_volume(self, vol):
        """Set volume SFX (0.0 - 1.0)."""
        self.sfx_volume = max(0, min(1, vol))
        for s in self.sounds.values():
            s.set_volume(self.sfx_volume)

    def generate_beep(self, name, frequency=440, duration_ms=100):
        """Generate simple beep sound (untuk menu navigation)."""
        if not self.initialized:
            return
        try:
            import numpy as np
            sample_rate = 44100
            n_samples = int(sample_rate * duration_ms / 1000)
            t = np.linspace(0, duration_ms / 1000, n_samples, False)
            wave = np.sin(2 * np.pi * frequency * t) * 0.3
            # Fade in/out
            fade = min(n_samples // 10, 200)
            wave[:fade] *= np.linspace(0, 1, fade)
            wave[-fade:] *= np.linspace(1, 0, fade)
            # Convert ke int16 stereo
            samples = (wave * 32767).astype(np.int16)
            stereo = np.column_stack((samples, samples))
            sound = pygame.sndarray.make_sound(stereo)
            sound.set_volume(self.sfx_volume * 0.5)
            self.sounds[name] = sound
        except Exception:
            pass

    def cleanup(self):
        """Cleanup audio."""
        if self.initialized:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
