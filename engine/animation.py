"""
engine/animation.py - Sistem Animasi
=====================================
Mengelola animasi sprite, efek visual, dan transisi.
Menggunakan transformasi (translate, rotate, scale) untuk animasi dinamis.
"""

import math
import pygame
from engine.transform import Transform2D


class Animation:
    """Animasi dasar dengan frame-based timing."""

    def __init__(self, duration, loop=False, on_complete=None):
        self.duration = duration  # dalam detik
        self.loop = loop
        self.on_complete = on_complete
        self.elapsed = 0
        self.active = True
        self.completed = False

    def update(self, dt):
        """Update animation timer. Returns progress 0-1."""
        if not self.active:
            return 1.0
        self.elapsed += dt
        if self.elapsed >= self.duration:
            if self.loop:
                self.elapsed = self.elapsed % self.duration
            else:
                self.elapsed = self.duration
                self.active = False
                self.completed = True
                if self.on_complete:
                    self.on_complete()
        return self.elapsed / self.duration if self.duration > 0 else 1.0

    def reset(self):
        self.elapsed = 0
        self.active = True
        self.completed = False


class SpriteAnimation:
    """Animasi frame-based untuk sprite sheets."""

    def __init__(self, frames, frame_duration=0.15, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.elapsed = 0

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1

    def get_frame(self):
        return self.frames[self.current_frame]


class DamageNumber:
    """Angka damage yang muncul dan naik ke atas lalu menghilang."""

    def __init__(self, text, x, y, color=(255, 50, 50)):
        self.text = str(text)
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.timer = Animation(1.0)
        self.scale = 1.5  # mulai besar lalu mengecil

    def update(self, dt):
        progress = self.timer.update(dt)
        # Naik ke atas
        self.y = self.start_y - 40 * progress
        # Scale: membesar lalu kembali normal
        if progress < 0.2:
            self.scale = 1.0 + progress * 3
        else:
            self.scale = max(0.8, 1.6 - progress)

    def is_done(self):
        return self.timer.completed

    def get_alpha(self):
        progress = self.timer.elapsed / self.timer.duration
        if progress > 0.7:
            return int(255 * (1 - (progress - 0.7) / 0.3))
        return 255


class ScreenTransition:
    """Efek transisi layar (fade in/out, battle swirl)."""

    def __init__(self, transition_type='fade', duration=0.5, on_complete=None):
        self.type = transition_type
        self.animation = Animation(duration, on_complete=on_complete)
        self.surface = None

    def start(self, screen_size):
        self.animation.reset()
        self.surface = pygame.Surface(screen_size, pygame.SRCALPHA)

    def update(self, dt):
        return self.animation.update(dt)

    def render(self, screen):
        if self.surface is None or not self.animation.active:
            return
        progress = self.animation.elapsed / self.animation.duration

        if self.type == 'fade_out':
            alpha = int(255 * progress)
            self.surface.fill((0, 0, 0, alpha))
            screen.blit(self.surface, (0, 0))

        elif self.type == 'fade_in':
            alpha = int(255 * (1 - progress))
            self.surface.fill((0, 0, 0, alpha))
            screen.blit(self.surface, (0, 0))

        elif self.type == 'battle_swirl':
            # Efek spiral untuk masuk battle (seperti FF klasik)
            alpha = int(255 * progress)
            self.surface.fill((0, 0, 0, 0))
            cx, cy = screen.get_width() // 2, screen.get_height() // 2
            max_radius = int(math.sqrt(cx * cx + cy * cy))
            radius = int(max_radius * progress)
            pygame.draw.circle(self.surface, (0, 0, 0, alpha), (cx, cy), radius)
            screen.blit(self.surface, (0, 0))

    @property
    def is_done(self):
        return self.animation.completed


class ParticleEffect:
    """Sistem partikel sederhana untuk efek visual."""

    def __init__(self, x, y, color, count=20, speed=100, lifetime=1.0, spread=360):
        self.particles = []
        self.timer = Animation(lifetime)
        import random
        for _ in range(count):
            angle = math.radians(random.uniform(0, spread))
            spd = random.uniform(speed * 0.5, speed)
            self.particles.append({
                'x': float(x),
                'y': float(y),
                'vx': math.cos(angle) * spd,
                'vy': math.sin(angle) * spd,
                'size': random.randint(2, 5),
                'color': color,
                'alpha': 255,
            })

    def update(self, dt):
        progress = self.timer.update(dt)
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 100 * dt  # gravity
            p['alpha'] = max(0, int(255 * (1 - progress)))
            p['size'] = max(1, p['size'] - dt * 2)

    def render(self, screen):
        for p in self.particles:
            if p['alpha'] > 0:
                surf = pygame.Surface((int(p['size'] * 2), int(p['size'] * 2)), pygame.SRCALPHA)
                c = p['color']
                pygame.draw.circle(surf, (c[0], c[1], c[2], p['alpha']),
                                   (int(p['size']), int(p['size'])), int(p['size']))
                screen.blit(surf, (int(p['x'] - p['size']), int(p['y'] - p['size'])))

    @property
    def is_done(self):
        return self.timer.completed


class FloatingText:
    """Teks yang mengambang naik (untuk heal, buff, dll)."""

    def __init__(self, text, x, y, color=(100, 255, 150), duration=1.5):
        self.text = text
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.timer = Animation(duration)

    def update(self, dt):
        progress = self.timer.update(dt)
        self.y = self.start_y - 50 * progress

    def get_alpha(self):
        progress = self.timer.elapsed / self.timer.duration
        if progress > 0.6:
            return int(255 * (1 - (progress - 0.6) / 0.4))
        return 255

    @property
    def is_done(self):
        return self.timer.completed
