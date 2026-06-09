import pygame

class InputHandler:
    """Mengelola semua input dari keyboard dan mouse."""

    def __init__(self):
        self.keys_pressed = {}
        self.keys_just_pressed = {}
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.mouse_just_clicked = False
        self.quit_requested = False

    def update(self):
        """Update input state. Panggil setiap frame."""
        self.keys_just_pressed = {}
        self.mouse_just_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                self.keys_just_pressed[event.key] = True

            elif event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_clicked = True
                    self.mouse_just_clicked = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_clicked = False

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def is_key_held(self, key):
        """Cek apakah tombol sedang ditekan (held down)."""
        return self.keys_pressed.get(key, False)

    def is_key_pressed(self, key):
        """Cek apakah tombol baru saja ditekan (1 frame)."""
        return self.keys_just_pressed.get(key, False)

    def is_mouse_clicked(self):
        """Cek apakah mouse baru saja diklik."""
        return self.mouse_just_clicked

    def get_mouse_pos(self):
        """Dapatkan posisi mouse saat ini."""
        return self.mouse_pos

    # Shortcut directional input
    def is_up(self):
        return self.is_key_pressed(pygame.K_UP) or self.is_key_pressed(pygame.K_w)

    def is_down(self):
        return self.is_key_pressed(pygame.K_DOWN) or self.is_key_pressed(pygame.K_s)

    def is_left(self):
        return self.is_key_pressed(pygame.K_LEFT) or self.is_key_pressed(pygame.K_a)

    def is_right(self):
        return self.is_key_pressed(pygame.K_RIGHT) or self.is_key_pressed(pygame.K_d)

    def is_confirm(self):
        return self.is_key_pressed(pygame.K_RETURN) or self.is_key_pressed(pygame.K_z)

    def is_cancel(self):
        return self.is_key_pressed(pygame.K_ESCAPE) or self.is_key_pressed(pygame.K_x)

    def is_move_up(self):
        return self.is_key_held(pygame.K_UP) or self.is_key_held(pygame.K_w)

    def is_move_down(self):
        return self.is_key_held(pygame.K_DOWN) or self.is_key_held(pygame.K_s)

    def is_move_left(self):
        return self.is_key_held(pygame.K_LEFT) or self.is_key_held(pygame.K_a)

    def is_move_right(self):
        return self.is_key_held(pygame.K_RIGHT) or self.is_key_held(pygame.K_d)
