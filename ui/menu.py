"""
ui/menu.py - Main Menu Handler
================================
State handler untuk main menu dan game over screen.
"""

import math
import pygame
from engine.game import StateHandler, GameState
from engine.graphics import GraphicsEngine
from engine.renderer import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from engine.transform import Transform2D
from ui.components import UIPanel, MenuList, MenuItem


class MainMenuHandler(StateHandler):
    """Handler untuk state MAIN_MENU."""

    def __init__(self):
        super().__init__()
        self.menu = None
        self.timer = 0
        self.stars = []
        self._init_stars()

    def _init_stars(self):
        """Generate background stars."""
        import random
        self.stars = []
        for _ in range(80):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.2, 1.0),
                'brightness': random.randint(100, 255),
            })

    def on_enter(self, data):
        items = [
            MenuItem("New Game", 'new_game'),
            MenuItem("Load Game", 'load_game'),
            MenuItem("Demo Graphics", 'demo'),
            MenuItem("Quit", 'quit'),
        ]
        self.menu = MenuList(items, SCREEN_WIDTH // 2 - 110, 420, 220, 40)
        self.timer = 0
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bgm_path = os.path.join(base_dir, 'bgm', 'menu theme.ogg')
            self.game.audio.play_bgm(bgm_path)
        except Exception as e:
            pass

    def update(self, dt):
        self.timer += dt
        inp = self.game.input

        if inp.is_up():
            self.menu.move_up()
            self.game.audio.play_sound('menu_move')
        elif inp.is_down():
            self.menu.move_down()
            self.game.audio.play_sound('menu_move')
        elif inp.is_confirm():
            self.game.audio.play_sound('menu_select')
            sel = self.menu.get_selected()
            if sel:
                if sel.value == 'new_game':
                    self.game.audio.stop_bgm()
                    from game.player import Party
                    new_party = Party.create_default_party()
                    new_party.current_map = 'town'
                    new_party.position = [23, 19]
                    self.game.change_state(GameState.EXPLORATION, transition_type='fade_out', duration=0.6, data={'party': new_party, 'new_game': True})
                elif sel.value == 'load_game':
                    from game.player import Party
                    loaded_party = Party.load_from_file()
                    if loaded_party:
                        self.game.audio.stop_bgm()
                        self.game.change_state(GameState.EXPLORATION, transition_type='fade_out', duration=0.6, data={'party': loaded_party})
                    else:
                        self.game.audio.play_sound('menu_cancel')
                elif sel.value == 'demo':
                    self.game.audio.stop_bgm()
                    self.game.change_state(GameState.DEMO, transition_type='fade_out')
                elif sel.value == 'quit':
                    self.game.running = False

        # Animate stars
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                import random
                star['x'] = random.randint(0, SCREEN_WIDTH)

    def render(self, renderer):
        screen = renderer.screen

        # Dark gradient background
        GraphicsEngine.draw_gradient_rect_fast(
            screen, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            (5, 5, 30), (20, 10, 50), vertical=True
        )

        # Stars
        for star in self.stars:
            b = max(0, min(255, int(star['brightness'] * (0.5 + 0.5 * math.sin(self.timer * 2 + star['x'])))))
            b2 = min(255, b + 30)
            GraphicsEngine.draw_circle(screen, int(star['x']), int(star['y']),
                                       star['size'], (b, b, b2), fill=True)

        # Decorative Bezier curves (demonstrates Bezier)
        t_offset = self.timer * 20
        for i in range(3):
            wave = math.sin(self.timer + i) * 40
            points = [
                (0, 300 + i * 40 + wave),
                (SCREEN_WIDTH * 0.3, 250 + i * 40 - wave),
                (SCREEN_WIDTH * 0.7, 350 + i * 40 + wave),
                (SCREEN_WIDTH, 300 + i * 40 - wave),
            ]
            alpha = 40 + i * 15
            color = (80 + i * 20, 100 + i * 30, 200 + i * 20)
            GraphicsEngine.draw_bezier(screen, points, color, segments=60, thickness=1)

        # Title
        title_y = 150 + math.sin(self.timer * 1.5) * 8
        renderer.draw_text("FINAL QUEST", SCREEN_WIDTH // 2, title_y,
                          COLORS['ui_text_gold'], renderer.font_title, center=True)

        # Subtitle with B-Spline underline decoration
        renderer.draw_text("~ Crystal Chronicles ~", SCREEN_WIDTH // 2, title_y + 60,
                          COLORS['ui_border_light'], renderer.font_medium, center=True)

        # Decorative line under title (DDA line demonstration)
        line_w = 300
        lx = SCREEN_WIDTH // 2 - line_w // 2
        ly = title_y + 90
        GraphicsEngine.draw_line_dda(screen, lx, ly, lx + line_w, ly, COLORS['ui_border'], 1)
        # Dotted decoration
        GraphicsEngine.draw_dotted_line(screen, lx, ly + 4, lx + line_w, ly + 4,
                                        COLORS['ui_border_light'], spacing=6)

        # Menu
        self.menu.draw(screen, renderer.font_large)

        # Bottom info
        renderer.draw_text("Arrow Keys: Navigate  |  Enter/Z: Select",
                          SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
                          COLORS['ui_text_dim'], renderer.font_small, center=True)

        # Version / credit
        renderer.draw_text("Proyek Grafika Komputer 2026",
                          SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20,
                          (80, 80, 120), renderer.font_small, center=True)


class GameOverHandler(StateHandler):
    """Handler untuk GAME_OVER screen."""

    def __init__(self):
        super().__init__()
        self.timer = 0

    def on_enter(self, data):
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.game.input.is_confirm() and self.timer > 1.0:
            from game.player import Party
            loaded_party = Party.load_from_file()
            if loaded_party:
                self.game.change_state(GameState.EXPLORATION, transition_type='fade_out', duration=0.6, data={'party': loaded_party})
            else:
                self.game.change_state(GameState.MAIN_MENU)

    def render(self, renderer):
        screen = renderer.screen
        GraphicsEngine.draw_gradient_rect_fast(
            screen, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            (40, 0, 0), (10, 0, 0), vertical=True
        )
        renderer.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
                          (200, 40, 40), renderer.font_title, center=True)
        if self.timer > 1.0:
            bob = math.sin(self.timer * 3) * 3
            import os
            if os.path.exists('savegame.json'):
                renderer.draw_text("Press Enter to load last save",
                                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40 + bob,
                                  COLORS['ui_text'], renderer.font_medium, center=True)
            else:
                renderer.draw_text("Press Enter to return to title",
                                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40 + bob,
                                  COLORS['ui_text_dim'], renderer.font_medium, center=True)
