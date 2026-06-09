"""
ui/hud.py - Exploration with smooth movement, party following, interactions.
"""
import math, pygame
from engine.game import StateHandler, GameState
from engine.graphics import GraphicsEngine
from engine.renderer import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from engine.sprites import SpriteManager
from game.player import Party
from game.world import (WorldManager, TILE_GRASS, TILE_WALL, TILE_WATER,
    TILE_PATH, TILE_DOOR, TILE_NPC, TILE_CHEST, TILE_DUNGEON_ENTRANCE,
    TILE_FLOOR, TILE_STAIRS_DOWN, TILE_STAIRS_UP, TILE_BOSS, TILE_SAVE_POINT,
    TILE_HOUSE, TILE_TREE, TILE_FLOWER, TILE_FENCE, TILE_BRIDGE, TILE_SIGN,
    TILE_BARREL, TILE_LAMP, TILE_FOUNTAIN, TILE_SHOP)
from game.monster import get_random_encounter, create_monster
from ui.components import UIPanel, HPBar, DialogBox

class ExplorationHandler(StateHandler):
    def __init__(self):
        super().__init__()
        self.party = None; self.world = WorldManager(); self.dialog = DialogBox()
        self.sprites = SpriteManager(); self.initialized = False
        self.move_cooldown = 0; self.step_count = 0; self.timer = 0
        self.anim_frame = 0; self.anim_timer = 0
        self.camera_x = 0; self.camera_y = 0
        self.show_menu = False; self.pause_menu_index = 0
        self.current_dungeon_floor = -1
        self.message = ""; self.message_timer = 0; self.is_moving = False
        self.position_history = []; self.trail_spacing = 2
        # Smooth movement
        self.visual_x = 0.0; self.visual_y = 0.0
        self.follower_vx = []; self.follower_vy = []
        self.lerp_speed = 10.0
        # Inventory sub-menu
        self.inv_mode = False; self.inv_index = 0; self.inv_target = 0

    def on_enter(self, data):
        if not self.initialized:
            self.world.init(); self.sprites.init(); self.initialized = True
        if data and 'party' in data:
            self.party = data['party']
            if data.get('new_game'):
                self.position_history = []
                self.follower_vx = []
                self.follower_vy = []
        elif not self.party:
            self.party = Party.create_default_party()
            self.party.position = [23, 19]

        if self.party.current_map == 'town':
            self.current_dungeon_floor = -1
        elif self.party.current_map.startswith('dungeon_'):
            self.current_dungeon_floor = int(self.party.current_map.split('_')[1])
        self.visual_x = float(self.party.position[0])
        self.visual_y = float(self.party.position[1])
        if not self.position_history:
            self.position_history = [(self.party.position[0], self.party.position[1], self.party.direction)] * (self.trail_spacing * 3 + 1)
        if not self.follower_vx:
            for _ in range(len(self.party.members)):
                self.follower_vx.append(float(self.party.position[0]))
                self.follower_vy.append(float(self.party.position[1]))
        if self.party.current_map != 'town' and self.party.current_map.startswith('dungeon'):
            self.world.switch_map(self.party.current_map)
        elif self.party.current_map == 'town':
            self.world.switch_map('town')
        self.dialog.active = False; self.show_menu = False
        self._update_camera()
        self._play_map_bgm()

    def _play_map_bgm(self):
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if self.party.current_map == 'town':
                bgm_path = os.path.join(base_dir, 'bgm', 'vilage.ogg')
                self.game.audio.play_bgm(bgm_path)
            elif self.party.current_map == 'dungeon_0':
                bgm_path = os.path.join(base_dir, 'bgm', 'song dungeon b1.ogg')
                self.game.audio.play_bgm(bgm_path)
            elif self.party.current_map == 'dungeon_1':
                bgm_path = os.path.join(base_dir, 'bgm', 'song dungeon B2 .ogg')
                self.game.audio.play_bgm(bgm_path)
            elif self.party.current_map == 'dungeon_2':
                bgm_path = os.path.join(base_dir, 'bgm', 'song dungeon B3.ogg')
                self.game.audio.play_bgm(bgm_path)
            else:
                self.game.audio.stop_bgm()
        except Exception:
            pass

    def _update_camera(self):
        tw = SCREEN_WIDTH // TILE_SIZE; th = SCREEN_HEIGHT // TILE_SIZE
        self.camera_x = max(0, min(self.visual_x - tw // 2, self.world.current_map.width - tw))
        self.camera_y = max(0, min(self.visual_y - th // 2, self.world.current_map.height - th))

    def _record_position(self):
        self.position_history.append((self.party.position[0], self.party.position[1], self.party.direction))
        mx = self.trail_spacing * len(self.party.members) + 5
        if len(self.position_history) > mx:
            self.position_history = self.position_history[-mx:]

    def update(self, dt):
        self.timer += dt; self.move_cooldown = max(0, self.move_cooldown - dt)
        if self.message_timer > 0: self.message_timer -= dt
        self.anim_timer += dt
        if self.anim_timer >= 0.2:
            self.anim_timer -= 0.2
            self.anim_frame = (self.anim_frame + 1) % 4 if self.is_moving else 0
        # Smooth lerp leader
        tx, ty = float(self.party.position[0]), float(self.party.position[1])
        sp = min(1.0, self.lerp_speed * dt)
        self.visual_x += (tx - self.visual_x) * sp
        self.visual_y += (ty - self.visual_y) * sp
        if abs(self.visual_x - tx) < 0.01: self.visual_x = tx
        if abs(self.visual_y - ty) < 0.01: self.visual_y = ty
        # Smooth lerp followers
        for i in range(1, len(self.party.members)):
            hi = len(self.position_history)-1-i*self.trail_spacing
            if 0 <= hi < len(self.position_history) and i < len(self.follower_vx):
                hx, hy, _ = self.position_history[hi]
                self.follower_vx[i] += (float(hx) - self.follower_vx[i]) * sp
                self.follower_vy[i] += (float(hy) - self.follower_vy[i]) * sp
        self._update_camera()

        if self.dialog.active:
            self.dialog.update(dt)
            if self.game.input.is_confirm(): self.dialog.advance()
            return
        if self.show_menu: self._update_pause_menu(); return

        inp = self.game.input
        if inp.is_cancel(): self.show_menu = True; self.pause_menu_index = 0; return

        self.is_moving = False
        if self.move_cooldown <= 0:
            dx, dy = 0, 0
            if inp.is_move_up(): dy, self.party.direction = -1, 'up'
            elif inp.is_move_down(): dy, self.party.direction = 1, 'down'
            elif inp.is_move_left(): dx, self.party.direction = -1, 'left'
            elif inp.is_move_right(): dx, self.party.direction = 1, 'right'
            if dx != 0 or dy != 0:
                nx, ny = self.party.position[0]+dx, self.party.position[1]+dy
                if self.world.current_map.is_walkable(nx, ny):
                    self.party.position = [nx, ny]; self.move_cooldown = 0.15
                    self.step_count += 1; self.is_moving = True
                    self._record_position(); self._check_tile_event(nx, ny)
        if inp.is_confirm(): self._interact()

    def _check_tile_event(self, x, y):
        cm = self.world.current_map; tile = cm.get_tile(x, y)
        if cm.encounters and self.step_count % 3 == 0 and cm.check_encounter():
            monsters = get_random_encounter('dungeon', cm.floor)
            self.game.change_state(GameState.BATTLE, transition_type='battle_swirl', duration=0.6,
                data={'party': self.party, 'monsters': monsters, 'sprites': self.sprites})
            return
        if tile == TILE_DUNGEON_ENTRANCE: self._enter_dungeon()
        elif tile == TILE_STAIRS_DOWN: self._go_deeper()
        elif tile == TILE_STAIRS_UP: self._go_up()
        elif tile == TILE_SAVE_POINT:
            self.party.full_restore(); self.party.save_to_file()
            self._show_msg("★ Game Saved! HP & MP Recovered ★")
            self.game.audio.play_sound('heal')
        elif tile == TILE_BOSS:
            boss = create_monster('dragon')
            self.game.change_state(GameState.BATTLE, transition_type='battle_swirl', duration=0.8,
                data={'party': self.party, 'monsters': [boss], 'sprites': self.sprites, 'is_boss': True})
        elif tile == TILE_CHEST:
            if (x, y) not in cm.opened_chests:
                cm.opened_chests.add((x, y)); import random
                loot = random.choice(['Potion','Ether','Phoenix Down'])
                for it in self.party.inventory:
                    if it['name'] == loot: it['count'] += 1; break
                self._show_msg(f"Ditemukan {loot}!"); self.game.audio.play_sound('levelup')
        elif tile == TILE_FOUNTAIN:
            self.party.full_restore(); self._show_msg("Air fountain menyembuhkanmu!")

    def _interact(self):
        dd = {'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
        dx, dy = dd.get(self.party.direction, (0,0))
        fx, fy = self.party.position[0]+dx, self.party.position[1]+dy
        cm = self.world.current_map; tile = cm.get_tile(fx, fy)
        if tile == TILE_NPC:
            npc = cm.npcs.get((fx, fy))
            if npc:
                self.dialog.show(npc['name'], npc['dialog']); self.game.audio.play_sound('menu_select')
                if npc.get('action') == 'heal': self.party.full_restore()
                elif npc.get('action') == 'shop':
                    for it in self.party.inventory:
                        if it['name'] == 'Potion': it['count'] += 3
                        elif it['name'] == 'Ether': it['count'] += 2
        elif tile == TILE_SIGN:
            npc = cm.npcs.get((fx, fy))
            if npc: self.dialog.show(npc['name'], npc['dialog']); self.game.audio.play_sound('menu_select')
        elif tile == TILE_BARREL:
            self._show_msg("Barrel kosong..."); self.game.audio.play_sound('menu_move')
        elif tile == TILE_DOOR:
            self._show_msg("Pintu terkunci..."); self.game.audio.play_sound('menu_move')
        elif tile == TILE_FOUNTAIN:
            self.party.full_restore(); self._show_msg("HP & MP dipulihkan!")
            self.game.audio.play_sound('heal')
        elif tile == TILE_SAVE_POINT:
            self.party.full_restore(); self.party.save_to_file()
            self._show_msg("★ Game Saved! HP & MP Recovered ★")
            self.game.audio.play_sound('heal')

    def _enter_dungeon(self):
        self.current_dungeon_floor = 0; self.party.current_map = 'dungeon_0'
        self.world.switch_map('dungeon_0'); self.party.position = [3, 3]
        self.visual_x = 3.0; self.visual_y = 3.0
        self.position_history = [(3,3,'down')]*(self.trail_spacing*3+1)
        self._show_msg("Dungeon B1...")
        self._play_map_bgm()

    def _go_deeper(self):
        self.current_dungeon_floor += 1; mn = f'dungeon_{self.current_dungeon_floor}'
        if self.world.get_map(mn):
            self.party.current_map = mn; self.world.switch_map(mn); m = self.world.current_map
            for y in range(m.height):
                for x in range(m.width):
                    if m.get_tile(x,y) == TILE_STAIRS_UP:
                        self.party.position = [x,y]; self.visual_x=float(x); self.visual_y=float(y); break
            self.position_history = [(self.party.position[0],self.party.position[1],'down')]*(self.trail_spacing*3+1)
            self._show_msg(f"Dungeon B{self.current_dungeon_floor+1}")
            self._play_map_bgm()

    def _go_up(self):
        if self.current_dungeon_floor <= 0:
            self.party.current_map = 'town'; self.world.switch_map('town')
            self.party.position = [44,33]; self.visual_x=44.0; self.visual_y=33.0
            self.current_dungeon_floor = -1
        else:
            self.current_dungeon_floor -= 1; mn = f'dungeon_{self.current_dungeon_floor}'
            self.party.current_map = mn; self.world.switch_map(mn); m = self.world.current_map
            for y in range(m.height):
                for x in range(m.width):
                    if m.get_tile(x,y) == TILE_STAIRS_DOWN:
                        self.party.position = [x,y]; self.visual_x=float(x); self.visual_y=float(y); break
        self.position_history = [(self.party.position[0],self.party.position[1],'down')]*(self.trail_spacing*3+1)
        self._show_msg("Naik ke atas...")
        self._play_map_bgm()

    def _show_msg(self, t): self.message = t; self.message_timer = 2.5

    def _update_pause_menu(self):
        inp = self.game.input
        if self.inv_mode:
            self._update_inventory(inp); return
        opts = 4
        if inp.is_up(): self.pause_menu_index = (self.pause_menu_index-1)%opts; self.game.audio.play_sound('menu_move')
        elif inp.is_down(): self.pause_menu_index = (self.pause_menu_index+1)%opts; self.game.audio.play_sound('menu_move')
        elif inp.is_confirm():
            self.game.audio.play_sound('menu_select')
            if self.pause_menu_index == 0: self.show_menu = False
            elif self.pause_menu_index == 1: self.inv_mode = True; self.inv_index = 0; self.inv_target = -1
            elif self.pause_menu_index == 2: self.show_menu = False
            elif self.pause_menu_index == 3: self.game.change_state(GameState.MAIN_MENU)
        elif inp.is_cancel(): self.show_menu = False

    def _update_inventory(self, inp):
        usable = [it for it in self.party.inventory if it['count'] > 0]
        if not usable: self.inv_mode = False; return
        if self.inv_target >= 0:
            # Choosing target member
            targets = self.party.members
            if not targets: self.inv_target = -1; return
            if inp.is_up(): self.inv_target = (self.inv_target-1)%len(targets); self.game.audio.play_sound('menu_move')
            elif inp.is_down(): self.inv_target = (self.inv_target+1)%len(targets); self.game.audio.play_sound('menu_move')
            elif inp.is_confirm():
                item = usable[self.inv_index]; target = targets[self.inv_target]
                if item['type'] == 'heal_hp':
                    target.heal(item['power']); item['count'] -= 1
                    self._show_msg(f"{target.name} healed!"); self.game.audio.play_sound('heal')
                elif item['type'] == 'heal_mp':
                    target.restore_mp(item['power']); item['count'] -= 1
                    self._show_msg(f"{target.name} MP restored!"); self.game.audio.play_sound('heal')
                elif item['type'] == 'revive' and not target.alive:
                    target.alive = True; target.hp = int(target.max_hp * item['power']); item['count'] -= 1
                    self._show_msg(f"{target.name} revived!"); self.game.audio.play_sound('heal')
                self.inv_target = -1
            elif inp.is_cancel(): self.inv_target = -1
        else:
            if inp.is_up(): self.inv_index = (self.inv_index-1)%len(usable); self.game.audio.play_sound('menu_move')
            elif inp.is_down(): self.inv_index = (self.inv_index+1)%len(usable); self.game.audio.play_sound('menu_move')
            elif inp.is_confirm(): self.inv_target = 0; self.game.audio.play_sound('menu_select')
            elif inp.is_cancel(): self.inv_mode = False

    def render(self, renderer):
        screen = renderer.screen; cm = self.world.current_map
        tw = SCREEN_WIDTH // TILE_SIZE + 2; th = SCREEN_HEIGHT // TILE_SIZE + 2
        cx_off = self.camera_x * TILE_SIZE; cy_off = self.camera_y * TILE_SIZE
        for ty in range(th):
            for tx in range(tw):
                mx, my = int(self.camera_x) + tx, int(self.camera_y) + ty
                tile = cm.get_tile(mx, my)
                sx = int(tx * TILE_SIZE - (cx_off % TILE_SIZE))
                sy = int(ty * TILE_SIZE - (cy_off % TILE_SIZE))
                self._draw_tile(screen, tile, sx, sy, mx, my)
        # Followers (smooth)
        for i in range(len(self.party.members)-1, 0, -1):
            hi = len(self.position_history)-1-i*self.trail_spacing
            if 0 <= hi < len(self.position_history) and i < len(self.follower_vx):
                _, _, hdir = self.position_history[hi]
                fx = (self.follower_vx[i] - self.camera_x) * TILE_SIZE
                fy = (self.follower_vy[i] - self.camera_y) * TILE_SIZE
                m = self.party.members[i]
                if m.alive:
                    spr = self.sprites.get_char_frame(m.char_class, hdir, self.anim_frame if self.is_moving else 0)
                    sw, sh = spr.get_size()
                    screen.blit(spr, (int(fx+TILE_SIZE//2-sw//2), int(fy+TILE_SIZE//2-sh//2-6)))
        # Player (smooth)
        px = (self.visual_x - self.camera_x) * TILE_SIZE
        py = (self.visual_y - self.camera_y) * TILE_SIZE
        leader = self.party.members[0]
        spr = self.sprites.get_char_frame(leader.char_class, self.party.direction, self.anim_frame if self.is_moving else 0)
        sw, sh = spr.get_size()
        screen.blit(spr, (int(px+TILE_SIZE//2-sw//2), int(py+TILE_SIZE//2-sh//2-6)))
        # HUD
        self._draw_hud(screen, renderer)
        self.dialog.draw(screen, renderer.font_medium, SCREEN_WIDTH, SCREEN_HEIGHT)
        if self.message_timer > 0:
            a = min(230, int(self.message_timer * 200))
            UIPanel.draw(screen, SCREEN_WIDTH//2-220, 20, 440, 40, a)
            renderer.draw_text(self.message, SCREEN_WIDTH//2, 30, COLORS['ui_text_gold'], renderer.font_medium, center=True)
        if self.show_menu: self._draw_pause_menu(screen, renderer)

    def _draw_tile(self, screen, tile, sx, sy, mx, my):
        s = TILE_SIZE; var = ((mx*7+my*13)%20)-10
        if tile == TILE_GRASS:
            c=COLORS['grass']; pygame.draw.rect(screen,(max(0,c[0]+var),max(0,c[1]+var),max(0,c[2]+var)),(sx,sy,s,s))
            if (mx+my)%5==0: GraphicsEngine.draw_line_bresenham(screen,sx+s//2,sy+s-3,sx+s//2-2,sy+s-8,(80,160,80))
        elif tile == TILE_WALL:
            pygame.draw.rect(screen,COLORS['wall'],(sx,sy,s,s))
            GraphicsEngine.draw_line_bresenham(screen,sx,sy+s//2,sx+s,sy+s//2,COLORS['wall_dark'])
        elif tile == TILE_WATER:
            wv=int(math.sin(self.timer*2+mx)*10); c=COLORS['water']
            pygame.draw.rect(screen,(max(0,c[0]+wv),max(0,c[1]+wv),min(255,c[2]+wv+20)),(sx,sy,s,s))
            wy=sy+s//3+int(math.sin(self.timer*3+mx)*2)
            GraphicsEngine.draw_line_dda(screen,sx,wy,sx+s,wy,COLORS['water_light'])
        elif tile == TILE_PATH:
            pygame.draw.rect(screen,COLORS['path'],(sx,sy,s,s))
        elif tile == TILE_FLOOR:
            pygame.draw.rect(screen,(max(0,60+var),max(0,55+var),max(0,50+var)),(sx,sy,s,s))
        elif tile in (TILE_HOUSE, TILE_SHOP):
            wc=COLORS['wall'] if tile==TILE_HOUSE else (140,120,80)
            pygame.draw.rect(screen,wc,(sx,sy+8,s,s-8))
            roof=[(sx,sy+8),(sx+s//2,sy),(sx+s,sy+8)]
            rc=COLORS['roof'] if tile==TILE_HOUSE else (60,60,180)
            GraphicsEngine.scanline_fill(screen,roof,rc); GraphicsEngine.draw_polygon(screen,roof,COLORS['wall_dark'])
        elif tile == TILE_NPC:
            pygame.draw.rect(screen,COLORS['path'],(sx,sy,s,s))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+8,6,(230,190,150),fill=True)
            pygame.draw.rect(screen,(60,60,200),(sx+s//2-5,sy+15,10,14))
            bob=int(math.sin(self.timer*4)*2)
            pygame.draw.rect(screen,(255,255,100),(sx+s//2-1,sy-6+bob,3,6))
            pygame.draw.rect(screen,(255,255,100),(sx+s//2-1,sy+2+bob,3,2))
        elif tile == TILE_CHEST:
            pygame.draw.rect(screen,(60,55,50),(sx,sy,s,s))
            op = (mx,my) in self.world.current_map.opened_chests
            cc=(80,70,50) if op else (160,130,50)
            pygame.draw.rect(screen,cc,(sx+6,sy+12,20,14))
            pygame.draw.rect(screen,(200,170,60),(sx+6,sy+10,20,6))
            if not op: GraphicsEngine.draw_circle(screen,sx+s//2,sy+20,2,(255,215,0),fill=True)
        elif tile == TILE_DUNGEON_ENTRANCE:
            pygame.draw.rect(screen,COLORS['grass'],(sx,sy,s,s))
            pygame.draw.rect(screen,(30,20,20),(sx+4,sy+4,s-8,s-4))
            GraphicsEngine.draw_bezier(screen,[(sx+4,sy+s),(sx+s//2,sy),(sx+s-4,sy+s)],(100,80,60),20,2)
        elif tile in (TILE_STAIRS_DOWN, TILE_STAIRS_UP):
            pygame.draw.rect(screen,(60,55,50),(sx,sy,s,s))
            for i in range(4): pygame.draw.rect(screen,(80+i*10,75+i*10,70+i*10),(sx+i*2,sy+i*8,s-i*4,8))
        elif tile == TILE_BOSS:
            pygame.draw.rect(screen,(50,30,30),(sx,sy,s,s))
            glow=int(128+127*math.sin(self.timer*3))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,10,(min(255,glow),50,50),fill=True)
        elif tile == TILE_SAVE_POINT:
            bg=COLORS['path'] if self.party.current_map=='town' else (60,55,50)
            pygame.draw.rect(screen,bg,(sx,sy,s,s))
            glow=int(128+127*math.sin(self.timer*3))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,10,(min(255,glow),255,min(255,glow)),thickness=2)
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,5,(100,255,100),fill=True)
        elif tile == TILE_DOOR:
            pygame.draw.rect(screen,COLORS.get('door',(120,80,40)),(sx+6,sy+2,s-12,s-2))
            GraphicsEngine.draw_circle(screen,sx+s//2+4,sy+s//2,2,(200,180,50),fill=True)
        elif tile == TILE_TREE:
            pygame.draw.rect(screen,COLORS['grass'],(sx,sy,s,s))
            pygame.draw.rect(screen,(80,50,30),(sx+12,sy+18,8,14))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+12,12,(30,100,30),fill=True)
            GraphicsEngine.draw_circle(screen,sx+s//2-4,sy+8,8,(40,120,40),fill=True)
        elif tile == TILE_FLOWER:
            c=COLORS['grass']; pygame.draw.rect(screen,c,(sx,sy,s,s))
            fc=[(255,100,100),(255,200,80),(200,100,255),(100,200,255)]; ci=(mx*3+my*7)%4
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,4,fc[ci],fill=True)
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,2,(255,255,100),fill=True)
        elif tile == TILE_FENCE:
            pygame.draw.rect(screen,COLORS['grass'],(sx,sy,s,s))
            pygame.draw.rect(screen,(140,100,60),(sx+2,sy+10,s-4,4))
            pygame.draw.rect(screen,(140,100,60),(sx+2,sy+20,s-4,4))
            pygame.draw.rect(screen,(120,80,40),(sx+4,sy+6,4,22))
            pygame.draw.rect(screen,(120,80,40),(sx+s-8,sy+6,4,22))
        elif tile == TILE_BRIDGE:
            pygame.draw.rect(screen,(120,90,50),(sx,sy,s,s))
        elif tile == TILE_SIGN:
            pygame.draw.rect(screen,COLORS['path'],(sx,sy,s,s))
            pygame.draw.rect(screen,(120,90,50),(sx+8,sy+6,16,12))
            pygame.draw.rect(screen,(100,70,40),(sx+14,sy+18,4,10))
        elif tile == TILE_BARREL:
            pygame.draw.rect(screen,COLORS['path'],(sx,sy,s,s))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2+2,10,(120,80,40),fill=True)
        elif tile == TILE_LAMP:
            pygame.draw.rect(screen,COLORS['grass'],(sx,sy,s,s))
            pygame.draw.rect(screen,(60,60,60),(sx+13,sy+10,6,22))
            glow=int(200+55*math.sin(self.timer*5+mx))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+8,6,(min(255,glow),max(0,glow-40),50),fill=True)
        elif tile == TILE_FOUNTAIN:
            pygame.draw.rect(screen,COLORS['path'],(sx,sy,s,s))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,12,(80,80,100),fill=True)
            wg=int(180+75*math.sin(self.timer*4))
            GraphicsEngine.draw_circle(screen,sx+s//2,sy+s//2,8,(60,100,min(255,wg)),fill=True)
        else:
            pygame.draw.rect(screen,(30,30,30),(sx,sy,s,s))

    def _draw_hud(self, screen, renderer):
        UIPanel.draw(screen,10,10,200,30,180)
        renderer.draw_text(self.world.current_map.name,20,14,COLORS['ui_text'],renderer.font_small,shadow=False)
        pw=160
        UIPanel.draw(screen,SCREEN_WIDTH-pw-10,10,pw,len(self.party.members)*22+10,180)
        for i,h in enumerate(self.party.members):
            hy2=16+i*22; hx2=SCREEN_WIDTH-pw-4
            renderer.draw_text(h.name[:6],hx2,hy2,COLORS['ui_text'] if h.alive else COLORS['ui_text_dim'],renderer.font_small,shadow=False)
            HPBar.draw(screen,hx2+55,hy2+2,60,8,h.hp_ratio,'hp')
            HPBar.draw(screen,hx2+55,hy2+12,60,4,h.mp_ratio,'mp')
        renderer.draw_text("Z:Talk ESC:Menu",SCREEN_WIDTH//2,SCREEN_HEIGHT-14,(80,80,120),renderer.font_small,center=True)

    def _draw_pause_menu(self, screen, renderer):
        ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,150)); screen.blit(ov,(0,0))
        mx2,my2=SCREEN_WIDTH//2-120,SCREEN_HEIGHT//2-120
        UIPanel.draw(screen,mx2,my2,240,240)
        renderer.draw_text("PAUSE",SCREEN_WIDTH//2,my2+15,COLORS['ui_text_gold'],renderer.font_large,center=True)
        opts=["Resume","Inventory","Status","Back to Title"]
        for i,opt in enumerate(opts):
            oy=my2+55+i*35
            if i==self.pause_menu_index and not self.inv_mode:
                hl=pygame.Surface((220,30),pygame.SRCALPHA); hl.fill((60,80,150,100)); screen.blit(hl,(mx2+10,oy-2))
            renderer.draw_text(opt,mx2+35,oy,COLORS['ui_text'],renderer.font_medium,shadow=False)
        if self.inv_mode:
            self._draw_inventory(screen, renderer)

    def _draw_inventory(self, screen, renderer):
        ix, iy = SCREEN_WIDTH//2+140, SCREEN_HEIGHT//2-120
        usable = [it for it in self.party.inventory if it['count'] > 0]
        UIPanel.draw(screen, ix, iy, 250, len(usable)*30+40)
        renderer.draw_text("Inventory", ix+125, iy+8, COLORS['ui_text_gold'], renderer.font_medium, center=True)
        for i, it in enumerate(usable):
            oy = iy+35+i*30
            if i == self.inv_index and self.inv_target < 0:
                hl=pygame.Surface((230,26),pygame.SRCALPHA); hl.fill((60,80,150,100)); screen.blit(hl,(ix+10,oy-2))
            renderer.draw_text(f"{it['name']} x{it['count']}", ix+20, oy, COLORS['ui_text'], renderer.font_small, shadow=False)
        if self.inv_target >= 0:
            tx, ty = ix, iy+len(usable)*30+50
            targets = self.party.members
            UIPanel.draw(screen, tx, ty, 250, len(targets)*28+35)
            renderer.draw_text("Use on:", tx+10, ty+8, COLORS['ui_text_gold'], renderer.font_small, shadow=False)
            for i, h in enumerate(targets):
                oy = ty+30+i*28
                if i == self.inv_target:
                    hl=pygame.Surface((230,24),pygame.SRCALPHA); hl.fill((60,80,150,100)); screen.blit(hl,(tx+10,oy-2))
                color = COLORS['ui_text'] if h.alive else COLORS['ui_text_dim']
                renderer.draw_text(f"{h.name} HP:{h.hp}/{h.max_hp}", tx+20, oy, color, renderer.font_small, shadow=False)
