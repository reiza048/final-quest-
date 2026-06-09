"""
engine/renderer.py - Rendering Pipeline
========================================
Mengelola rendering ke layar, termasuk camera system dan layer management.
"""

import pygame


# ============================================================
# KONSTANTA GAME
# ============================================================

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
FPS = 60
GAME_TITLE = "Final Quest"

# ============================================================
# PALET WARNA (Final Fantasy Style)
# ============================================================

COLORS = {
    'black':        (0, 0, 0),
    'white':        (255, 255, 255),
    'gray':         (128, 128, 128),
    'dark_gray':    (64, 64, 64),
    'light_gray':   (192, 192, 192),

    # UI Colors (FF-style dark blue panels)
    'ui_bg':            (10, 10, 50),
    'ui_bg_dark':       (5, 5, 30),
    'ui_border':        (80, 120, 200),
    'ui_border_light':  (140, 180, 240),
    'ui_highlight':     (60, 80, 150),
    'ui_text':          (255, 255, 255),
    'ui_text_dim':      (160, 170, 200),
    'ui_text_gold':     (255, 215, 80),

    # HP / MP bars
    'hp_full':      (50, 220, 100),
    'hp_mid':       (240, 200, 40),
    'hp_low':       (230, 60, 40),
    'mp_full':      (80, 140, 255),
    'mp_low':       (30, 50, 140),

    # Elements
    'fire':         (255, 100, 30),
    'fire_light':   (255, 200, 80),
    'ice':          (100, 200, 255),
    'ice_light':    (200, 240, 255),
    'thunder':      (255, 255, 100),
    'thunder_light':(255, 255, 200),
    'heal':         (100, 255, 150),
    'heal_light':   (180, 255, 220),
    'dark':         (120, 50, 180),

    # Map colors
    'grass':        (60, 140, 60),
    'grass_dark':   (40, 110, 40),
    'path':         (180, 160, 120),
    'path_dark':    (150, 130, 90),
    'water':        (40, 100, 200),
    'water_light':  (70, 140, 230),
    'wall':         (100, 90, 80),
    'wall_dark':    (70, 60, 50),
    'door':         (150, 100, 50),
    'roof':         (160, 60, 50),

    # Character colors
    'warrior':      (200, 60, 60),
    'mage':         (120, 60, 200),
    'healer':       (60, 180, 100),

    # Battle
    'battle_bg_top':    (20, 10, 40),
    'battle_bg_bot':    (40, 30, 60),
    'damage':           (255, 50, 50),
    'exp_gold':         (255, 215, 0),
}


class Renderer:
    """Manages the rendering pipeline."""

    def __init__(self):
        self.screen = None
        self.clock = None
        self.font_small = None
        self.font_medium = None
        self.font_large = None
        self.font_title = None
        self.font_damage = None

    def init(self):
        """Initialize pygame display and fonts."""
        pygame.display.set_caption(GAME_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Load fonts
        try:
            font_name = pygame.font.match_font('arial', bold=False)
            if not font_name:
                font_name = pygame.font.get_default_font()
        except Exception:
            font_name = pygame.font.get_default_font()

        self.font_small = pygame.font.Font(font_name, 16)
        self.font_medium = pygame.font.Font(font_name, 22)
        self.font_large = pygame.font.Font(font_name, 30)
        self.font_title = pygame.font.Font(font_name, 56)
        self.font_damage = pygame.font.Font(font_name, 28)

    def clear(self, color=None):
        """Clear screen with color."""
        self.screen.fill(color or COLORS['black'])

    def present(self):
        """Flip display buffer and cap FPS."""
        pygame.display.flip()
        self.clock.tick(FPS)

    def get_fps(self):
        """Return current FPS."""
        return self.clock.get_fps()

    def draw_text(self, text, x, y, color=None, font=None, center=False, shadow=True):
        """Draw text with optional shadow."""
        color = color or COLORS['ui_text']
        font = font or self.font_medium

        if shadow:
            shadow_surf = font.render(text, True, (0, 0, 0))
            if center:
                rect = shadow_surf.get_rect(center=(x + 2, y + 2))
                self.screen.blit(shadow_surf, rect)
            else:
                self.screen.blit(shadow_surf, (x + 2, y + 2))

        text_surf = font.render(text, True, color)
        if center:
            rect = text_surf.get_rect(center=(x, y))
            self.screen.blit(text_surf, rect)
        else:
            self.screen.blit(text_surf, (x, y))

        return text_surf.get_size()

    def create_surface(self, width, height, alpha=True):
        """Create a new surface."""
        if alpha:
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
        else:
            surf = pygame.Surface((width, height))
        return surf
