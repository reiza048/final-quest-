"""
main.py - Entry Point untuk Final Quest RPG
=============================================
Game RPG turn-based bergaya Final Fantasy.
Proyek Akhir Grafika Komputer dan Multimedia.

Penggunaan:
    python main.py              # Jalankan game
    python main.py --demo       # Mode demo algoritma grafika

Kontrol:
    Arrow Keys / WASD  : Navigasi / Bergerak
    Enter / Z          : Konfirmasi / Interaksi
    ESC / X            : Batal / Menu
"""

import sys
import math
import pygame

from engine.game import Game, GameState, StateHandler
from engine.graphics import GraphicsEngine
from engine.transform import Transform2D
from engine.renderer import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from ui.menu import MainMenuHandler, GameOverHandler
from ui.hud import ExplorationHandler
from ui.battle_ui import BattleHandler
from ui.components import UIPanel


# ============================================================
# DEMO MODE - Presentasi Algoritma Grafika
# ============================================================

class DemoHandler(StateHandler):
    """Mode demo untuk menampilkan semua algoritma grafika."""

    def __init__(self):
        super().__init__()
        self.tab = 0
        self.tabs = ["Lines", "Curves", "Fill", "Transform"]
        self.timer = 0
        self.dragging = -1
        # Bezier control points (draggable)
        self.bezier_points = [(200, 500), (350, 200), (600, 200), (750, 500)]
        self.transform_angle = 0
        self.transform_scale = 1.0
        self.transform_tx = 0
        self.transform_ty = 0
        self.scale_dir = 1

    def on_enter(self, data):
        self.tab = 0
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        inp = self.game.input

        if inp.is_cancel():
            self.game.change_state(GameState.MAIN_MENU)
            return

        if inp.is_right():
            self.tab = (self.tab + 1) % len(self.tabs)
            self.game.audio.play_sound('menu_move')
        elif inp.is_left():
            self.tab = (self.tab - 1) % len(self.tabs)
            self.game.audio.play_sound('menu_move')

        # Drag bezier control points with mouse
        if self.tab == 1:
            mx, my = inp.get_mouse_pos()
            if inp.mouse_clicked:
                if self.dragging == -1:
                    for i, (px, py) in enumerate(self.bezier_points):
                        if abs(mx - px) < 15 and abs(my - py) < 15:
                            self.dragging = i
                            break
                if self.dragging >= 0:
                    self.bezier_points[self.dragging] = (mx, my)
            else:
                self.dragging = -1

        # Animate transforms
        if self.tab == 3:
            self.transform_angle += 60 * dt
            self.transform_scale += 0.5 * dt * self.scale_dir
            if self.transform_scale > 2.0:
                self.scale_dir = -1
            elif self.transform_scale < 0.5:
                self.scale_dir = 1
            self.transform_tx = math.sin(self.timer) * 100
            self.transform_ty = math.cos(self.timer) * 50

    def render(self, renderer):
        screen = renderer.screen
        GraphicsEngine.draw_gradient_rect_fast(
            screen, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            (10, 10, 35), (5, 5, 20), vertical=True
        )

        # Tab bar
        for i, tab_name in enumerate(self.tabs):
            tx = 50 + i * 200
            is_sel = i == self.tab
            c = COLORS['ui_text_gold'] if is_sel else COLORS['ui_text_dim']
            if is_sel:
                UIPanel.draw(screen, tx - 10, 10, 180, 35)
            renderer.draw_text(tab_name, tx + 70, 18, c, renderer.font_medium, center=True)

        # Content area
        if self.tab == 0:
            self._render_lines(screen, renderer)
        elif self.tab == 1:
            self._render_curves(screen, renderer)
        elif self.tab == 2:
            self._render_fill(screen, renderer)
        elif self.tab == 3:
            self._render_transform(screen, renderer)

        # Bottom info
        renderer.draw_text("← → : Switch Tab  |  ESC: Back to Menu",
                          SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20,
                          COLORS['ui_text_dim'], renderer.font_small, center=True)

    def _render_lines(self, screen, renderer):
        """Demo: DDA vs Bresenham line algorithms."""
        renderer.draw_text("Algoritma Garis", SCREEN_WIDTH // 2, 70,
                          COLORS['ui_text_gold'], renderer.font_large, center=True)

        # DDA Lines (left side)
        UIPanel.draw(screen, 30, 100, 460, 300)
        renderer.draw_text("DDA Algorithm", 260, 115, COLORS['ui_text'], renderer.font_medium, center=True)

        # Animated lines using DDA
        for i in range(8):
            angle = self.timer + i * math.pi / 4
            ex = 260 + math.cos(angle) * 120
            ey = 270 + math.sin(angle) * 100
            r = int(128 + 127 * math.sin(angle))
            g = int(128 + 127 * math.sin(angle + 2))
            b = int(128 + 127 * math.sin(angle + 4))
            GraphicsEngine.draw_line_dda(screen, 260, 270, int(ex), int(ey), (r, g, b), 2)

        # Bresenham Lines (right side)
        UIPanel.draw(screen, 530, 100, 460, 300)
        renderer.draw_text("Bresenham Algorithm", 760, 115, COLORS['ui_text'], renderer.font_medium, center=True)

        for i in range(8):
            angle = self.timer + i * math.pi / 4
            ex = 760 + math.cos(angle) * 120
            ey = 270 + math.sin(angle) * 100
            r = int(128 + 127 * math.cos(angle))
            g = int(128 + 127 * math.cos(angle + 2))
            b = int(128 + 127 * math.cos(angle + 4))
            GraphicsEngine.draw_line_bresenham(screen, 760, 270, int(ex), int(ey), (r, g, b), 2)

        # Line styles demo
        UIPanel.draw(screen, 30, 420, 960, 250)
        renderer.draw_text("Visual Attributes: Line Styles & Thickness", SCREEN_WIDTH // 2, 435,
                          COLORS['ui_text'], renderer.font_medium, center=True)

        y = 475
        # Solid lines with different thickness
        for t in range(1, 5):
            renderer.draw_text(f"Solid (thickness={t})", 60, y, COLORS['ui_text_dim'], renderer.font_small, shadow=False)
            GraphicsEngine.draw_line_bresenham(screen, 280, y + 8, 480, y + 8, COLORS['ui_border_light'], t)
            y += 30

        # Dashed line
        renderer.draw_text("Dashed", 60, y, COLORS['ui_text_dim'], renderer.font_small, shadow=False)
        GraphicsEngine.draw_dashed_line(screen, 280, y + 8, 480, y + 8, COLORS['fire'], thickness=2)
        y += 30

        # Dotted line
        renderer.draw_text("Dotted", 60, y, COLORS['ui_text_dim'], renderer.font_small, shadow=False)
        GraphicsEngine.draw_dotted_line(screen, 280, y + 8, 480, y + 8, COLORS['ice'], spacing=5, thickness=2)

        # Circle demo (right)
        renderer.draw_text("Midpoint Circle", 750, 460, COLORS['ui_text_dim'], renderer.font_small, shadow=False)
        for r in range(20, 100, 15):
            hue = (r * 3 + int(self.timer * 50)) % 360
            rgb = pygame.Color(0)
            rgb.hsva = (hue, 80, 100, 100)
            GraphicsEngine.draw_circle(screen, 780, 570, r, (rgb.r, rgb.g, rgb.b), thickness=2)

    def _render_curves(self, screen, renderer):
        """Demo: Bezier and B-Spline curves."""
        renderer.draw_text("Algoritma Kurva (Drag Control Points!)", SCREEN_WIDTH // 2, 70,
                          COLORS['ui_text_gold'], renderer.font_large, center=True)

        # Bezier curve
        UIPanel.draw(screen, 30, 100, 960, 350)
        renderer.draw_text("Bezier Curve (De Casteljau Algorithm)", SCREEN_WIDTH // 2, 115,
                          COLORS['ui_text'], renderer.font_medium, center=True)

        # Draw control polygon (dashed lines)
        for i in range(len(self.bezier_points) - 1):
            p1 = self.bezier_points[i]
            p2 = self.bezier_points[i + 1]
            GraphicsEngine.draw_dashed_line(screen, p1[0], p1[1], p2[0], p2[1],
                                           COLORS['ui_text_dim'], dash=6, gap=4)

        # Draw the Bezier curve
        GraphicsEngine.draw_bezier(screen, self.bezier_points, COLORS['fire'], segments=80, thickness=3)

        # Draw control points
        for i, (px, py) in enumerate(self.bezier_points):
            color = COLORS['ui_text_gold'] if i == self.dragging else COLORS['ui_border_light']
            GraphicsEngine.draw_circle(screen, px, py, 8, color, fill=True)
            GraphicsEngine.draw_circle(screen, px, py, 8, COLORS['white'], thickness=1)
            renderer.draw_text(f"P{i}", px - 5, py - 25, COLORS['ui_text'], renderer.font_small, shadow=False)

        # B-Spline
        UIPanel.draw(screen, 30, 470, 960, 230)
        renderer.draw_text("B-Spline Curve", SCREEN_WIDTH // 2, 485,
                          COLORS['ui_text'], renderer.font_medium, center=True)

        # Animated B-Spline control points
        bspline_pts = []
        for i in range(7):
            bx = 100 + i * 120
            by = 600 + math.sin(self.timer * 2 + i * 0.8) * 40
            bspline_pts.append((bx, by))

        # Control polygon
        for i in range(len(bspline_pts) - 1):
            GraphicsEngine.draw_dashed_line(screen, bspline_pts[i][0], bspline_pts[i][1],
                                           bspline_pts[i+1][0], bspline_pts[i+1][1], COLORS['ui_text_dim'])

        # B-Spline curve
        GraphicsEngine.draw_bspline(screen, bspline_pts, COLORS['ice'], degree=3, segments=80, thickness=3)

        # Control points
        for i, (px, py) in enumerate(bspline_pts):
            GraphicsEngine.draw_circle(screen, int(px), int(py), 5, COLORS['heal'], fill=True)

    def _render_fill(self, screen, renderer):
        """Demo: Fill algorithms."""
        renderer.draw_text("Algoritma Fill Area", SCREEN_WIDTH // 2, 70,
                          COLORS['ui_text_gold'], renderer.font_large, center=True)

        # Scanline fill demo
        UIPanel.draw(screen, 30, 100, 460, 550)
        renderer.draw_text("Scanline Fill (Polygon)", 260, 115,
                          COLORS['ui_text'], renderer.font_medium, center=True)

        # Animated polygon
        cx, cy = 260, 350
        sides = 6
        for s in range(3, sides + 1):
            pts = []
            r = 50 + s * 20
            for i in range(s):
                angle = self.timer * (0.3 + s * 0.1) + i * 2 * math.pi / s
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                pts.append((px, py))

            hue = (s * 50 + int(self.timer * 30)) % 360
            rgb = pygame.Color(0)
            rgb.hsva = (hue, 70, 80, 100)
            GraphicsEngine.scanline_fill(screen, pts, (rgb.r, rgb.g, rgb.b))
            GraphicsEngine.draw_polygon(screen, pts, COLORS['white'], 1)

        # Flood fill demo (right side)
        UIPanel.draw(screen, 530, 100, 460, 550)
        renderer.draw_text("Flood Fill + Shapes", 760, 115,
                          COLORS['ui_text'], renderer.font_medium, center=True)

        # Draw some filled shapes
        # Star using scanline fill
        star_pts = []
        star_cx, star_cy = 760, 300
        for i in range(5):
            outer_angle = -math.pi/2 + i * 2 * math.pi / 5
            inner_angle = outer_angle + math.pi / 5
            star_pts.append((star_cx + math.cos(outer_angle) * 80,
                           star_cy + math.sin(outer_angle) * 80))
            star_pts.append((star_cx + math.cos(inner_angle) * 35,
                           star_cy + math.sin(inner_angle) * 35))

        rot_pts = Transform2D.rotate(star_pts, self.timer * 30, (star_cx, star_cy))
        GraphicsEngine.scanline_fill(screen, rot_pts, COLORS['exp_gold'])
        GraphicsEngine.draw_polygon(screen, rot_pts, COLORS['white'], 1)

        # Filled circles
        for i in range(4):
            r = 20 + i * 10
            cx2 = 660 + i * 55
            cy2 = 500
            hue = (i * 80 + int(self.timer * 50)) % 360
            rgb = pygame.Color(0)
            rgb.hsva = (hue, 80, 90, 100)
            GraphicsEngine.draw_circle(screen, cx2, cy2, r, (rgb.r, rgb.g, rgb.b), fill=True)
            GraphicsEngine.draw_circle(screen, cx2, cy2, r, COLORS['white'])

    def _render_transform(self, screen, renderer):
        """Demo: 2D Transformations."""
        renderer.draw_text("Transformasi 2D (Matriks Homogen 3x3)", SCREEN_WIDTH // 2, 70,
                          COLORS['ui_text_gold'], renderer.font_large, center=True)

        # Original shape (house)
        house = [(0, 0), (60, 0), (60, -40), (30, -60), (0, -40)]
        center = (30, -20)

        # Translation demo
        UIPanel.draw(screen, 30, 100, 300, 280)
        renderer.draw_text("Translasi", 180, 115, COLORS['ui_text'], renderer.font_medium, center=True)
        tx = self.transform_tx
        ty = self.transform_ty
        translated = Transform2D.translate(house, 150 + tx, 280 + ty)
        GraphicsEngine.scanline_fill(screen, translated, COLORS['warrior'])
        GraphicsEngine.draw_polygon(screen, translated, COLORS['white'], 2)
        renderer.draw_text(f"tx={int(tx)}, ty={int(ty)}", 180, 360, COLORS['ui_text_dim'], renderer.font_small, center=True)

        # Rotation demo
        UIPanel.draw(screen, 362, 100, 300, 280)
        renderer.draw_text("Rotasi", 512, 115, COLORS['ui_text'], renderer.font_medium, center=True)
        rot_center = (512, 270)
        placed = Transform2D.translate(house, rot_center[0] - 30, rot_center[1] + 20)
        rotated = Transform2D.rotate(placed, self.transform_angle, rot_center)
        GraphicsEngine.scanline_fill(screen, rotated, COLORS['mage'])
        GraphicsEngine.draw_polygon(screen, rotated, COLORS['white'], 2)
        # Show rotation center
        GraphicsEngine.draw_circle(screen, rot_center[0], rot_center[1], 3, COLORS['ui_text_gold'], fill=True)
        renderer.draw_text(f"angle={int(self.transform_angle % 360)}°", 512, 360, COLORS['ui_text_dim'], renderer.font_small, center=True)

        # Scale demo
        UIPanel.draw(screen, 694, 100, 300, 280)
        renderer.draw_text("Scaling", 844, 115, COLORS['ui_text'], renderer.font_medium, center=True)
        sc_center = (844, 270)
        placed2 = Transform2D.translate(house, sc_center[0] - 30, sc_center[1] + 20)
        scaled = Transform2D.scale(placed2, self.transform_scale, self.transform_scale, sc_center)
        GraphicsEngine.scanline_fill(screen, scaled, COLORS['healer'])
        GraphicsEngine.draw_polygon(screen, scaled, COLORS['white'], 2)
        renderer.draw_text(f"scale={self.transform_scale:.1f}x", 844, 360, COLORS['ui_text_dim'], renderer.font_small, center=True)

        # Composite transformation demo
        UIPanel.draw(screen, 30, 400, 960, 300)
        renderer.draw_text("Komposisi Transformasi (Translate + Rotate + Scale)", SCREEN_WIDTH // 2, 415,
                          COLORS['ui_text'], renderer.font_medium, center=True)

        # Multiple shapes with composed transformations
        shape = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
        for i in range(8):
            t = self.timer + i * 0.5
            cx = SCREEN_WIDTH // 2 + math.cos(t) * 200
            cy = 580 + math.sin(t * 1.5) * 60
            angle = t * 45
            sc = 0.8 + math.sin(t * 2) * 0.3

            # Compose: translate to position, then rotate, then scale
            mat = Transform2D.compose(
                Transform2D.translation_matrix(cx, cy),
                Transform2D.rotation_matrix(angle),
                Transform2D.scale_matrix(sc, sc)
            )
            transformed = Transform2D.apply_matrix(shape, mat)

            hue = (i * 45 + int(self.timer * 20)) % 360
            rgb = pygame.Color(0)
            rgb.hsva = (hue, 80, 90, 100)
            GraphicsEngine.scanline_fill(screen, transformed, (rgb.r, rgb.g, rgb.b))
            GraphicsEngine.draw_polygon(screen, transformed, COLORS['white'])


# ============================================================
# CREDITS SCENE
# ============================================================

class CreditsHandler(StateHandler):
    """Credits scene after defeating the boss."""

    def __init__(self):
        super().__init__()
        self.timer = 0
        self.scroll_y = 0
        self.stars = []
        self.credits_lines = [
            ("", ""),
            ("", "FINAL QUEST"),
            ("", "~ Crystal Chronicles ~"),
            ("", ""),
            ("", "★ CONGRATULATIONS! ★"),
            ("", "You have defeated the Crystal Dragon"),
            ("", "and saved the kingdom!"),
            ("", ""),
            ("", "─────────────────"),
            ("", ""),
            ("DIRECTOR", ""),
            ("", "Proyek Grafika Komputer"),
            ("", ""),
            ("GAME DESIGN", ""),
            ("", "Turn-Based RPG System"),
            ("", ""),
            ("GRAPHICS ENGINE", ""),
            ("", "DDA Line Algorithm"),
            ("", "Bresenham Line Algorithm"),
            ("", "Bezier Curve (De Casteljau)"),
            ("", "B-Spline Curve"),
            ("", "Scanline Fill Algorithm"),
            ("", "Flood Fill Algorithm"),
            ("", "Midpoint Circle Algorithm"),
            ("", ""),
            ("2D TRANSFORMATIONS", ""),
            ("", "Translation Matrix"),
            ("", "Rotation Matrix"),
            ("", "Scaling Matrix"),
            ("", "Composite Transformations"),
            ("", ""),
            ("CHARACTERS", ""),
            ("", "Aric — Warrior"),
            ("", "Luna — Mage"),
            ("", "Sage — Healer"),
            ("", ""),
            ("MONSTERS", ""),
            ("", "Slime, Goblin, Skeleton"),
            ("", "Dark Knight"),
            ("", "Crystal Dragon (Boss)"),
            ("", ""),
            ("BUILT WITH", ""),
            ("", "Python + Pygame"),
            ("", "Manual Graphics Algorithms"),
            ("", ""),
            ("", "─────────────────"),
            ("", ""),
            ("", "Thank you for playing!"),
            ("", ""),
            ("", "Press Enter to return to title"),
            ("", ""),
            ("", ""),
        ]

    def _init_stars(self):
        import random
        self.stars = []
        for _ in range(60):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.1, 0.5),
                'b': random.randint(120, 255),
            })

    def on_enter(self, data):
        self.timer = 0
        self.scroll_y = SCREEN_HEIGHT
        self._init_stars()
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            bgm_path = os.path.join(base_dir, 'bgm', 'kredit scene song.ogg')
            print(f"Loading BGM from: {bgm_path}")
            self.game.audio.play_bgm(bgm_path)
            print(f"BGM get_busy: {pygame.mixer.music.get_busy()}")
        except Exception as e:
            print(f"BGM Error: {e}")

    def update(self, dt):
        self.timer += dt
        self.scroll_y -= 40 * dt  # Scroll speed

        # Stars twinkle
        for s in self.stars:
            s['y'] += s['speed']
            if s['y'] > SCREEN_HEIGHT:
                s['y'] = 0
                import random
                s['x'] = random.randint(0, SCREEN_WIDTH)

        # Allow skip after 3 seconds
        if self.timer > 3.0 and self.game.input.is_confirm():
            self.game.audio.stop_bgm()
            self.game.change_state(GameState.MAIN_MENU, transition_type='fade_out', duration=1.0)

        # Auto-return after all credits scrolled
        total_h = len(self.credits_lines) * 40
        if self.scroll_y < -total_h:
            self.game.audio.stop_bgm()
            self.game.change_state(GameState.MAIN_MENU, transition_type='fade_out', duration=1.0)

    def render(self, renderer):
        screen = renderer.screen

        # Dark background
        screen.fill((5, 5, 15))

        # Stars
        for s in self.stars:
            b = max(0, min(255, int(s['b'] * (0.6 + 0.4 * math.sin(self.timer * 2 + s['x'])))))
            pygame.draw.circle(screen, (b, b, min(255, b + 20)), (int(s['x']), int(s['y'])), s['size'])

        # Scrolling credits
        y = self.scroll_y
        for label, text in self.credits_lines:
            if -40 < y < SCREEN_HEIGHT + 40:
                if label:
                    # Category header (gold)
                    renderer.draw_text(label, SCREEN_WIDTH // 2, int(y),
                                      COLORS['ui_text_gold'], renderer.font_large, center=True)
                if text:
                    # Content (white or special)
                    if text == "FINAL QUEST":
                        renderer.draw_text(text, SCREEN_WIDTH // 2, int(y),
                                          COLORS['ui_text_gold'], renderer.font_title, center=True)
                    elif text.startswith("★"):
                        renderer.draw_text(text, SCREEN_WIDTH // 2, int(y),
                                          (255, 255, 100), renderer.font_large, center=True)
                    elif text.startswith("─"):
                        # Decorative line
                        GraphicsEngine.draw_line_dda(screen, SCREEN_WIDTH//2 - 150, int(y) + 8,
                                                    SCREEN_WIDTH//2 + 150, int(y) + 8,
                                                    COLORS['ui_border_light'], 1)
                    else:
                        renderer.draw_text(text, SCREEN_WIDTH // 2, int(y),
                                          COLORS['ui_text'], renderer.font_medium, center=True)
            y += 40

        # Skip hint (after 3s)
        if self.timer > 3.0:
            alpha = int(128 + 127 * math.sin(self.timer * 3))
            renderer.draw_text("Press Enter to skip", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25,
                              (alpha, alpha, alpha), renderer.font_small, center=True)


# ============================================================
# MAIN
# ============================================================

def main():
    """Entry point utama."""
    game = Game()

    # Register state handlers
    game.register_state(GameState.MAIN_MENU, MainMenuHandler())
    game.register_state(GameState.EXPLORATION, ExplorationHandler())
    game.register_state(GameState.BATTLE, BattleHandler())
    game.register_state(GameState.GAME_OVER, GameOverHandler())
    game.register_state(GameState.DEMO, DemoHandler())
    game.register_state(GameState.CREDITS, CreditsHandler())

    # Start game
    game.run()


if __name__ == '__main__':
    main()
