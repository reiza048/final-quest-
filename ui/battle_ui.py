"""
ui/battle_ui.py - FF-Style Battle UI (fixed)
"""
import pygame, math, random
from engine.game import StateHandler, GameState
from engine.graphics import GraphicsEngine
from engine.renderer import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from engine.animation import DamageNumber, ParticleEffect, FloatingText
from game.battle import BattleSystem, BattleState
from ui.components import UIPanel, HPBar, MenuList, MenuItem

class BattleHandler(StateHandler):
    def __init__(self):
        super().__init__()
        self.battle=None; self.party=None; self.sprites=None; self.is_boss_fight=False
        self.effects=[]; self.damage_numbers=[]; self.floating_texts=[]
        self.action_menu=None; self.spell_menu=None; self.item_menu=None
        self.anim_timer=0; self.idle_timer=0; self.victory_timer=0
        self.flash_alpha=0; self.show_victory=False
        self.monster_positions=[]; self.hero_positions=[]
        self._pending_action=None; self._pending_spell=None
        self._pending_item=None; self._target_allies=False

    def on_enter(self, data):
        if not data: self.game.change_state(GameState.EXPLORATION); return
        self.party = data.get('party'); monsters = data.get('monsters',[])
        self.sprites = data.get('sprites'); self.is_boss_fight = data.get('is_boss', False)
        if not self.party or not monsters: self.game.change_state(GameState.EXPLORATION); return
        self.battle = BattleSystem(self.party, monsters)
        self.effects=[]; self.damage_numbers=[]; self.floating_texts=[]
        self.idle_timer=0; self.victory_timer=0; self.show_victory=False; self.flash_alpha=0
        self.monster_positions=[]
        for i,m in enumerate(monsters):
            if m.is_boss: self.monster_positions.append((200,250))
            else:
                mx=150+(i%2)*100; my=180+i*(100 if len(monsters)<=2 else 70)
                self.monster_positions.append((mx,my))
        self.hero_positions=[]
        for i in range(len(self.party.members)):
            self.hero_positions.append((SCREEN_WIDTH-200-i*40, 200+i*80))
        self.battle.state = BattleState.PLAYER_TURN; self.battle.next_turn()
        self._build_action_menu()
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bgm_name = 'boss music.ogg' if self.is_boss_fight else 'battle.ogg'
            bgm_path = os.path.join(base_dir, 'bgm', bgm_name)
            self.game.audio.play_bgm(bgm_path)
        except Exception:
            pass

    def _build_action_menu(self):
        items=[MenuItem("Attack",'attack'),MenuItem("Magic",'magic'),
               MenuItem("Item",'item'),MenuItem("Defend",'defend')]
        if self.battle.can_flee: items.append(MenuItem("Flee",'flee'))
        self.action_menu=MenuList(items,20,SCREEN_HEIGHT-185,150,28)

    def _build_spell_menu(self,ch):
        items=[MenuItem(f"{s['name']} ({s['mp_cost']}MP)",s) for s in ch.spells]
        items.append(MenuItem("Back",'back'))
        self.spell_menu=MenuList(items,180,SCREEN_HEIGHT-185,200,28)

    def _build_item_menu(self):
        usable=self.battle.get_usable_items()
        items=[MenuItem(f"{it['name']} x{it['count']}",it) for it in usable]
        items.append(MenuItem("Back",'back'))
        self.item_menu=MenuList(items,180,SCREEN_HEIGHT-185,200,28)

    def update(self, dt):
        if not self.battle: return
        self.idle_timer += dt
        for e in self.effects[:]:
            e.update(dt)
            if e.is_done: self.effects.remove(e)
        for d in self.damage_numbers[:]:
            d.update(dt)
            if d.is_done(): self.damage_numbers.remove(d)
        for f in self.floating_texts[:]:
            f.update(dt)
            if f.is_done: self.floating_texts.remove(f)
        if self.flash_alpha > 0: self.flash_alpha = max(0, self.flash_alpha - 500*dt)

        inp = self.game.input; st = self.battle.state
        if st == BattleState.CHOOSE_ACTION:
            if inp.is_up(): self.action_menu.move_up(); self.game.audio.play_sound('menu_move')
            elif inp.is_down(): self.action_menu.move_down(); self.game.audio.play_sound('menu_move')
            elif inp.is_confirm(): self._handle_action()
        elif st == BattleState.CHOOSE_SPELL:
            if inp.is_up(): self.spell_menu.move_up()
            elif inp.is_down(): self.spell_menu.move_down()
            elif inp.is_confirm(): self._handle_spell()
            elif inp.is_cancel(): self.battle.state = BattleState.CHOOSE_ACTION
        elif st == BattleState.CHOOSE_ITEM:
            if inp.is_up(): self.item_menu.move_up()
            elif inp.is_down(): self.item_menu.move_down()
            elif inp.is_confirm(): self._handle_item()
            elif inp.is_cancel(): self.battle.state = BattleState.CHOOSE_ACTION
        elif st == BattleState.CHOOSE_TARGET:
            tgts = self._get_targets()
            if inp.is_up(): self.battle.target_index = (self.battle.target_index-1)%len(tgts)
            elif inp.is_down(): self.battle.target_index = (self.battle.target_index+1)%len(tgts)
            elif inp.is_confirm(): self._execute_target(tgts)
            elif inp.is_cancel(): self.battle.state = BattleState.CHOOSE_ACTION
        elif st == BattleState.ANIMATION:
            self.anim_timer -= dt
            if self.anim_timer <= 0: self.battle.next_turn()
        elif st == BattleState.ENEMY_TURN: self._enemy_turn()
        elif st == BattleState.VICTORY:
            if not self.show_victory:
                self.show_victory = True
                try:
                    import os
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    bgm_path = os.path.join(base_dir, 'bgm', 'victory.ogg')
                    self.game.audio.play_bgm(bgm_path, loops=0)
                except Exception:
                    pass
            self.victory_timer += dt
            if inp.is_confirm() and self.victory_timer > 1.5:
                if self.is_boss_fight:
                    self.game.change_state(GameState.CREDITS, data={'party': self.party})
                else:
                    self.game.change_state(GameState.EXPLORATION, data={'party': self.party})
        elif st == BattleState.DEFEAT:
            self.victory_timer += dt
            if inp.is_confirm() and self.victory_timer > 1: self.game.change_state(GameState.GAME_OVER)

    def _get_targets(self):
        if self._target_allies:
            if self._pending_action == 'item' and self._pending_item and self._pending_item.get('type') == 'revive':
                return self.party.members
            if self._pending_action == 'magic' and self._pending_spell and self._pending_spell.get('type') == 'revive':
                return self.party.members
            return self.party.get_alive_members()
        return self.battle.get_alive_monsters()

    def _handle_action(self):
        sel=self.action_menu.get_selected()
        if not sel: return
        self.game.audio.play_sound('menu_select')
        _,actor=self.battle.get_current_actor()
        if sel.value=='attack':
            self.battle.target_index=0; self._target_allies=False
            self.battle.state=BattleState.CHOOSE_TARGET; self._pending_action='attack'
        elif sel.value=='magic':
            if actor.spells: self._build_spell_menu(actor); self.battle.state=BattleState.CHOOSE_SPELL
        elif sel.value=='item':
            self._build_item_menu(); self.battle.state=BattleState.CHOOSE_ITEM
        elif sel.value=='defend':
            actor.defending=True; i=self.party.members.index(actor)
            p=self.hero_positions[i] if i<len(self.hero_positions) else (600,400)
            self.floating_texts.append(FloatingText("Defend!",p[0],p[1],(150,200,255)))
            self.battle.state=BattleState.ANIMATION; self.anim_timer=0.5
        elif sel.value=='flee':
            if self.battle.try_flee(): self.game.change_state(GameState.EXPLORATION,data={'party':self.party})
            else:
                self.floating_texts.append(FloatingText("Can't flee!",SCREEN_WIDTH//2,SCREEN_HEIGHT//2,(255,100,100)))
                self.battle.state=BattleState.ANIMATION; self.anim_timer=0.8

    def _handle_spell(self):
        sel=self.spell_menu.get_selected()
        if not sel or sel.value=='back': self.battle.state=BattleState.CHOOSE_ACTION; return
        self._pending_spell=sel.value; self._pending_action='magic'
        self._target_allies=sel.value['type'] in ('heal','revive','buff')
        self.battle.target_index=0
        if sel.value.get('target')=='all':
            self._execute_target(self._get_targets(), True)
        else: self.battle.state=BattleState.CHOOSE_TARGET

    def _handle_item(self):
        sel=self.item_menu.get_selected()
        if not sel or sel.value=='back': self.battle.state=BattleState.CHOOSE_ACTION; return
        self._pending_item=sel.value; self._pending_action='item'
        self._target_allies=True; self.battle.target_index=0
        self.battle.state=BattleState.CHOOSE_TARGET

    def _execute_target(self, targets, all_t=False):
        _,actor=self.battle.get_current_actor()
        st=targets if all_t else [targets[self.battle.target_index % len(targets)]]
        if self._pending_action=='attack':
            for t in st:
                r=self.battle.execute_attack(actor,t); self._show_dmg(r)
            self.flash_alpha=150; self.game.audio.play_sound('hit')
        elif self._pending_action=='magic':
            results=self.battle.execute_spell(actor,self._pending_spell,st)
            for r in results: self._show_spell_r(r,self._pending_spell)
            self.flash_alpha=100
        elif self._pending_action=='item':
            r=self.battle.execute_item(actor,self._pending_item,st[0])
            self._show_item_r(r)
        self.battle.state=BattleState.ANIMATION; self.anim_timer=0.8

    def _show_dmg(self,r):
        pos=self._get_pos(r['target'])
        txt=("CRIT! " if r.get('critical') else "")+str(r['damage'])
        c=(255,255,100) if r.get('critical') else (255,80,80)
        self.damage_numbers.append(DamageNumber(txt,pos[0],pos[1]-20,c))
        self.effects.append(ParticleEffect(pos[0],pos[1],(255,200,100),8,80))

    def _show_spell_r(self,r,spell):
        tgt=r.get('target')
        if not tgt: return
        pos=self._get_pos(tgt)
        cmap={'fire':(255,100,50),'ice':(100,200,255),'thunder':(255,255,100),'heal':(100,255,150)}
        c=cmap.get(spell.get('element','none'),(255,255,255))
        if 'damage' in r:
            txt=str(r['damage'])+(" WEAK!" if r.get('weak') else "")
            self.damage_numbers.append(DamageNumber(txt,pos[0],pos[1]-20,c))
            self.effects.append(ParticleEffect(pos[0],pos[1],c,15,100)); self.game.audio.play_sound('hit')
        elif 'heal' in r:
            self.damage_numbers.append(DamageNumber(f"+{r['heal']}",pos[0],pos[1]-20,(100,255,150)))
            self.effects.append(ParticleEffect(pos[0],pos[1],(100,255,180),12,60)); self.game.audio.play_sound('heal')
        elif 'revive' in r:
            self.floating_texts.append(FloatingText("Revived!",pos[0],pos[1],(255,255,100))); self.game.audio.play_sound('heal')

    def _show_item_r(self,r):
        tgt=r.get('target')
        if not tgt: return
        pos=self._get_pos(tgt)
        if 'heal' in r:
            self.damage_numbers.append(DamageNumber(f"+{r['heal']}",pos[0],pos[1]-20,(100,255,150))); self.game.audio.play_sound('heal')
        elif 'revive' in r:
            self.floating_texts.append(FloatingText("Revived!",pos[0],pos[1],(255,255,100)))

    def _get_pos(self,target):
        if target in self.party.members:
            i=self.party.members.index(target)
            return self.hero_positions[i] if i<len(self.hero_positions) else (600,300)
        for i,m in enumerate(self.battle.monsters):
            if m is target: return self.monster_positions[i] if i<len(self.monster_positions) else (200,300)
        return (SCREEN_WIDTH//2,SCREEN_HEIGHT//2)

    def _enemy_turn(self):
        at,actor=self.battle.get_current_actor()
        if at!='monster' or not actor.alive: self.battle.next_turn(); return
        action=actor.choose_action(self.party.members)
        if not action: self.battle.next_turn(); return
        if action['type']=='attack':
            for t in action['targets']:
                r=self.battle.execute_attack(actor,t); self._show_dmg(r)
        elif action['type']=='skill':
            sk=action['skill']
            results=self.battle.execute_spell(actor,sk,action['targets'])
            for r in results: self._show_spell_r(r,sk)
            pos=self._get_pos(actor)
            self.floating_texts.append(FloatingText(sk['name'],pos[0],pos[1]-40,(255,150,150)))
        self.flash_alpha=120; self.game.audio.play_sound('hit')
        self.battle.state=BattleState.ANIMATION; self.anim_timer=0.8

    def render(self, renderer):
        if not self.battle: return
        screen=renderer.screen
        GraphicsEngine.draw_gradient_rect_fast(screen,0,0,SCREEN_WIDTH,SCREEN_HEIGHT//2,(15,10,40),(40,25,60),vertical=True)
        GraphicsEngine.draw_gradient_rect_fast(screen,0,SCREEN_HEIGHT//2,SCREEN_WIDTH,SCREEN_HEIGHT//2,(40,25,60),(30,50,30),vertical=True)
        gy=SCREEN_HEIGHT-200
        GraphicsEngine.draw_gradient_rect_fast(screen,0,gy,SCREEN_WIDTH,200,(50,60,40),(30,40,25),vertical=True)
        for i in range(5):
            ly=gy+i*40; GraphicsEngine.draw_line_dda(screen,0,ly,SCREEN_WIDTH,ly,(40+i*5,50+i*5,35+i*5),1)
        # Monsters
        for i,mon in enumerate(self.battle.monsters):
            if not mon.alive: continue
            if i>=len(self.monster_positions): continue
            mx,my=self.monster_positions[i]; bob=math.sin(self.idle_timer*2+i)*4
            if self.sprites:
                spr=self.sprites.get_monster_sprite(mon.sprite_type); sw,sh=spr.get_size()
                screen.blit(spr,(int(mx-sw//2),int(my-sh//2+bob)))
            else:
                r2={'small':25,'medium':35,'large':45,'boss':60}.get(mon.size,35)
                GraphicsEngine.draw_circle(screen,mx,int(my+bob),r2,mon.color,fill=True)
            ns=renderer.font_small.render(mon.name,True,COLORS['white'])
            screen.blit(ns,(mx-ns.get_width()//2,my-50))
            HPBar.draw(screen,mx-30,my-38,60,8,mon.hp_ratio,'hp')
        # Heroes
        for i,hero in enumerate(self.party.members):
            if i>=len(self.hero_positions): continue
            hx,hy=self.hero_positions[i]
            ca=self.battle.get_current_actor()
            is_act=ca and ca[1] is hero and self.battle.state in (BattleState.CHOOSE_ACTION,BattleState.CHOOSE_SPELL,BattleState.CHOOSE_ITEM,BattleState.CHOOSE_TARGET)
            bob=math.sin(self.idle_timer*3)*3 if is_act else 0
            if not hero.alive:
                if self.sprites:
                    spr=self.sprites.get_battle_char_sprite(hero.char_class)
                    spr=pygame.transform.rotate(spr,90); spr.set_alpha(100)
                    screen.blit(spr,(hx-10,hy+10))
                continue
            if self.sprites:
                spr=self.sprites.get_battle_char_sprite(hero.char_class); sw,sh=spr.get_size()
                screen.blit(spr,(int(hx-sw//2),int(hy-sh//2+bob)))
            if is_act:
                GraphicsEngine.draw_line_bresenham(screen,hx-10,hy-50,hx,hy-42,COLORS['ui_text_gold'],2)
                GraphicsEngine.draw_line_bresenham(screen,hx+10,hy-50,hx,hy-42,COLORS['ui_text_gold'],2)
        # Target cursor
        if self.battle.state==BattleState.CHOOSE_TARGET:
            tgts=self._get_targets()
            if tgts and self.battle.target_index<len(tgts):
                pos=self._get_pos(tgts[self.battle.target_index])
                bob2=math.sin(self.idle_timer*5)*5
                ax,ay=pos[0],pos[1]-65+bob2
                GraphicsEngine.draw_line_bresenham(screen,ax-10,ay-12,ax,ay,(255,255,100),3)
                GraphicsEngine.draw_line_bresenham(screen,ax+10,ay-12,ax,ay,(255,255,100),3)
        # Status panel
        pw,ph=320,len(self.party.members)*32+15
        px2,py2=SCREEN_WIDTH-pw-10,SCREEN_HEIGHT-ph-10
        UIPanel.draw(screen,px2,py2,pw,ph)
        for i,h in enumerate(self.party.members):
            ry=py2+8+i*32; c=COLORS['ui_text'] if h.alive else COLORS['ui_text_dim']
            renderer.draw_text(h.name,px2+10,ry,c,renderer.font_small,shadow=False)
            HPBar.draw(screen,px2+85,ry+2,90,10,h.hp_ratio,'hp')
            HPBar.draw(screen,px2+85,ry+14,90,6,h.mp_ratio,'mp')
            renderer.draw_text(f"{h.hp}/{h.max_hp}",px2+185,ry,COLORS['ui_text'],renderer.font_small,shadow=False)
        # Menus
        if self.battle.state==BattleState.CHOOSE_ACTION:
            ca=self.battle.get_current_actor()
            if ca: renderer.draw_text(f"{ca[1].name}'s turn",SCREEN_WIDTH//2,25,COLORS['ui_text_gold'],renderer.font_medium,center=True)
            self.action_menu.draw(screen,renderer.font_medium)
        elif self.battle.state==BattleState.CHOOSE_SPELL:
            self.action_menu.draw(screen,renderer.font_medium); self.spell_menu.draw(screen,renderer.font_medium)
        elif self.battle.state==BattleState.CHOOSE_ITEM:
            self.action_menu.draw(screen,renderer.font_medium); self.item_menu.draw(screen,renderer.font_medium)
        # Effects
        for e in self.effects: e.render(screen)
        for d in self.damage_numbers:
            a=d.get_alpha(); s2=d.scale
            surf=renderer.font_damage.render(d.text,True,d.color)
            if a<255: surf.set_alpha(a)
            if s2!=1:
                w2,h2=max(1,int(surf.get_width()*s2)),max(1,int(surf.get_height()*s2))
                surf=pygame.transform.scale(surf,(w2,h2))
            screen.blit(surf,(int(d.x-surf.get_width()//2),int(d.y)))
        for f in self.floating_texts:
            a=f.get_alpha(); surf=renderer.font_medium.render(f.text,True,f.color)
            if a<255: surf.set_alpha(a)
            screen.blit(surf,(int(f.x-surf.get_width()//2),int(f.y)))
        if self.flash_alpha>0:
            fl=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
            fl.fill((255,255,255,int(self.flash_alpha))); screen.blit(fl,(0,0))
        # Victory/Defeat
        if self.battle.state==BattleState.VICTORY and self.show_victory:
            ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,150)); screen.blit(ov,(0,0))
            UIPanel.draw(screen,SCREEN_WIDTH//2-200,150,400,350)
            renderer.draw_text("VICTORY!",SCREEN_WIDTH//2,190,COLORS['ui_text_gold'],renderer.font_title,center=True)
            renderer.draw_text(f"EXP: +{self.battle.total_exp}",SCREEN_WIDTH//2,260,COLORS['ui_text'],renderer.font_large,center=True)
            renderer.draw_text(f"Gold: +{self.battle.total_gold}",SCREEN_WIDTH//2,300,COLORS['exp_gold'],renderer.font_large,center=True)
            for i,h in enumerate(self.battle.leveled_up):
                renderer.draw_text(f"{h.name} → Lv.{h.level}!",SCREEN_WIDTH//2,350+i*30,(255,255,100),renderer.font_medium,center=True)
            if self.victory_timer>1.5:
                renderer.draw_text("Press Enter",SCREEN_WIDTH//2,460,COLORS['ui_text_dim'],renderer.font_small,center=True)
        elif self.battle.state==BattleState.DEFEAT:
            ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); ov.fill((100,0,0,150)); screen.blit(ov,(0,0))
            renderer.draw_text("GAME OVER",SCREEN_WIDTH//2,SCREEN_HEIGHT//2-30,(255,50,50),renderer.font_title,center=True)
            if self.victory_timer>1:
                renderer.draw_text("Press Enter",SCREEN_WIDTH//2,SCREEN_HEIGHT//2+40,COLORS['ui_text_dim'],renderer.font_medium,center=True)
