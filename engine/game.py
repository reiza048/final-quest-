# Game State Machine
import pygame
import sys
from engine.renderer import Renderer, SCREEN_WIDTH, SCREEN_HEIGHT
from engine.input_handler import InputHandler
from engine.audio import AudioManager
from engine.animation import ScreenTransition

class GameState:
    MAIN_MENU = 'main_menu'
    EXPLORATION = 'exploration'
    BATTLE = 'battle'
    GAME_OVER = 'game_over'
    VICTORY = 'victory'
    DEMO = 'demo'
    CREDITS = 'credits'

class Game:

    def __init__(self):
        pygame.init()
        self.renderer = Renderer()
        self.renderer.init()
        self.input = InputHandler()
        self.audio = AudioManager()
        self.audio.init()

        # Generate beep sounds untuk menu
        self.audio.generate_beep('menu_move', 500, 50)
        self.audio.generate_beep('menu_select', 700, 80)
        self.audio.generate_beep('menu_cancel', 300, 80)
        self.audio.generate_beep('hit', 200, 100)
        self.audio.generate_beep('heal', 800, 200)
        self.audio.generate_beep('levelup', 600, 300)

        self.state = GameState.MAIN_MENU
        self.running = True
        self.dt = 0

        # State handlers (akan di-set oleh main.py)
        self.state_handlers = {}
        self.transition = None
        self.pending_state = None
        self.pending_data = None

    def register_state(self, state_name, handler):
        self.state_handlers[state_name] = handler
        handler.game = self

    def change_state(self, new_state, transition_type='fade_out', duration=0.4, data=None):
        self.pending_state = new_state
        self.pending_data = data

        if transition_type:
            self.transition = ScreenTransition(
                transition_type, duration,
                on_complete=self._complete_transition
            )
            self.transition.start((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self._complete_transition()

    def _complete_transition(self):
        old_state = self.state
        self.state = self.pending_state

        # Notify handlers
        if old_state in self.state_handlers:
            self.state_handlers[old_state].on_exit()
        if self.state in self.state_handlers:
            self.state_handlers[self.state].on_enter(self.pending_data)

        # Fade in setelah state berubah
        self.transition = ScreenTransition('fade_in', 0.3)
        self.transition.start((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pending_state = None
        self.pending_data = None

    def run(self):
        # Enter initial state
        if self.state in self.state_handlers:
            self.state_handlers[self.state].on_enter(None)

        while self.running:
            # Delta time (dalam detik)
            self.dt = self.renderer.clock.tick(60) / 1000.0
            self.dt = min(self.dt, 0.05)  # Cap dt

            # Input
            self.input.update()
            if self.input.quit_requested:
                self.running = False
                break

            # Update transition
            if self.transition and self.transition.animation.active:
                self.transition.update(self.dt)

            # Update current state
            if self.state in self.state_handlers:
                # Jangan update game logic saat transisi fade_out
                if not (self.transition and self.pending_state):
                    self.state_handlers[self.state].update(self.dt)

            # Render
            self.renderer.clear()
            if self.state in self.state_handlers:
                self.state_handlers[self.state].render(self.renderer)

            # Render transition overlay
            if self.transition and self.transition.animation.active:
                self.transition.render(self.renderer.screen)

            self.renderer.present()

        self.shutdown()

    def shutdown(self):
        self.audio.cleanup()
        pygame.quit()
        sys.exit()

class StateHandler:

    def __init__(self):
        self.game = None

    def on_enter(self, data):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        pass

    def render(self, renderer):
        pass
