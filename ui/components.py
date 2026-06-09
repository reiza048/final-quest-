# Reusable UI Components
import pygame
from engine.graphics import GraphicsEngine
from engine.renderer import COLORS

class UIPanel:

    @staticmethod
    def draw(surface, x, y, w, h, alpha=230):
        panel = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
        bg = COLORS['ui_bg']
        panel.fill((bg[0], bg[1], bg[2], alpha))
        surface.blit(panel, (int(x), int(y)))
        # Border menggunakan Bresenham
        GraphicsEngine.draw_line_bresenham(surface, x, y, x + w, y, COLORS['ui_border_light'], 2)
        GraphicsEngine.draw_line_bresenham(surface, x, y + h, x + w, y + h, COLORS['ui_border'], 2)
        GraphicsEngine.draw_line_bresenham(surface, x, y, x, y + h, COLORS['ui_border_light'], 2)
        GraphicsEngine.draw_line_bresenham(surface, x + w, y, x + w, y + h, COLORS['ui_border'], 2)
        # Corner circles (midpoint circle)
        corner_color = COLORS['ui_border_light']
        for cx, cy in [(x+3, y+3), (x+w-3, y+3), (x+3, y+h-3), (x+w-3, y+h-3)]:
            GraphicsEngine.draw_circle(surface, cx, cy, 2, corner_color, fill=True)

class HPBar:

    @staticmethod
    def draw(surface, x, y, w, h, ratio, bar_type='hp'):
        GraphicsEngine.fast_fill_rect(surface, x, y, w, h, COLORS['dark_gray'])
        fill_w = int(w * max(0, min(1, ratio)))
        if fill_w > 0:
            if bar_type == 'hp':
                if ratio > 0.5:
                    color1, color2 = COLORS['hp_full'], (100, 240, 140)
                elif ratio > 0.25:
                    color1, color2 = COLORS['hp_mid'], (255, 220, 80)
                else:
                    color1, color2 = COLORS['hp_low'], (255, 100, 60)
            else:
                color1, color2 = COLORS['mp_low'], COLORS['mp_full']
            GraphicsEngine.draw_gradient_rect_fast(surface, x, y, fill_w, h, color1, color2)
        GraphicsEngine.draw_rect(surface, x, y, w, h, COLORS['ui_border'])

class MenuItem:
    def __init__(self, text, value=None, enabled=True):
        self.text = text
        self.value = value
        self.enabled = enabled

class MenuList:

    def __init__(self, items, x, y, w=200, item_height=30):
        self.items = items
        self.x = x
        self.y = y
        self.w = w
        self.item_height = item_height
        self.selected = 0

    def move_up(self):
        self.selected = (self.selected - 1) % len(self.items)
        while not self.items[self.selected].enabled and len(self.items) > 1:
            self.selected = (self.selected - 1) % len(self.items)

    def move_down(self):
        self.selected = (self.selected + 1) % len(self.items)
        while not self.items[self.selected].enabled and len(self.items) > 1:
            self.selected = (self.selected + 1) % len(self.items)

    def get_selected(self):
        if 0 <= self.selected < len(self.items):
            return self.items[self.selected]
        return None

    def draw(self, surface, font, show_panel=True):
        h = len(self.items) * self.item_height + 20
        if show_panel:
            UIPanel.draw(surface, self.x, self.y, self.w, h)
        for i, item in enumerate(self.items):
            iy = self.y + 10 + i * self.item_height
            color = COLORS['ui_text'] if item.enabled else COLORS['ui_text_dim']
            if i == self.selected:
                hl = pygame.Surface((self.w - 10, self.item_height), pygame.SRCALPHA)
                hl.fill((60, 80, 150, 100))
                surface.blit(hl, (self.x + 5, iy))
                ax = self.x + 12
                ay = iy + self.item_height // 2
                GraphicsEngine.draw_line_bresenham(surface, ax, ay - 5, ax + 6, ay, COLORS['ui_text_gold'], 2)
                GraphicsEngine.draw_line_bresenham(surface, ax, ay + 5, ax + 6, ay, COLORS['ui_text_gold'], 2)
            text_surf = font.render(item.text, True, color)
            surface.blit(text_surf, (self.x + 25, iy + 4))

class DialogBox:

    def __init__(self):
        self.active = False
        self.lines = []
        self.current_line = 0
        self.speaker = ""
        self.char_index = 0
        self.char_timer = 0
        self.speed = 0.03

    def show(self, speaker, lines):
        self.active = True
        self.speaker = speaker
        self.lines = lines
        self.current_line = 0
        self.char_index = 0
        self.char_timer = 0

    def update(self, dt):
        if not self.active or self.current_line >= len(self.lines):
            return
        self.char_timer += dt
        if self.char_timer >= self.speed:
            self.char_timer -= self.speed
            if self.char_index < len(self.lines[self.current_line]):
                self.char_index += 1

    def advance(self):
        if not self.active:
            return False
        current_text = self.lines[self.current_line] if self.current_line < len(self.lines) else ""
        if self.char_index < len(current_text):
            self.char_index = len(current_text)
            return True
        self.current_line += 1
        self.char_index = 0
        if self.current_line >= len(self.lines):
            self.active = False
            return False
        return True

    def draw(self, surface, font, screen_w, screen_h):
        if not self.active:
            return
        panel_h = 120
        panel_y = screen_h - panel_h - 10
        UIPanel.draw(surface, 20, panel_y, screen_w - 40, panel_h)
        if self.speaker:
            name_surf = font.render(self.speaker, True, COLORS['ui_text_gold'])
            surface.blit(name_surf, (40, panel_y + 10))
        if self.current_line < len(self.lines):
            text = self.lines[self.current_line][:self.char_index]
            text_surf = font.render(text, True, COLORS['ui_text'])
            surface.blit(text_surf, (40, panel_y + 40))
            if self.char_index >= len(self.lines[self.current_line]):
                indicator = font.render("▼", True, COLORS['ui_text_gold'])
                surface.blit(indicator, (screen_w - 60, panel_y + panel_h - 30))
