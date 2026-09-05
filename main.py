"""
Township - Main Game Loop & State Machine
Features Title Screen, Save Slot / Level Selector, Options Menu,
Active Town Simulation, Asset Loader with Spritesheet support, and Match-3 Event.
"""

import os
import sys
import math
import time
import pygame
from typing import Tuple, Optional, Dict, Any

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE,
    COLOR_BG, CROPS, SHEDS, FACTORIES, HOUSES,
    COMMUNITY_BUILDINGS, DECORATIONS, SPECIAL_BUILDINGS, ROADS
)
from sound_manager import get_sound_manager
from sprites import get_sprite_manager
from asset_loader import get_asset_loader, get_animation_manager
from game_state import GameState
from systems.farming import FarmingSystem
from systems.livestock import LivestockSystem
from systems.manufacturing import ManufacturingSystem
from systems.city_building import CityBuildingSystem
from ui.hud import HUD
from ui.modals import ModalManager
from ui.menu_screens import MainMenuScreen, PlaySelectScreen, OptionsScreen
from ui.components import ModernButton, ModernCard
from minigame.match3 import Match3Game

# Game States
STATE_MAIN_MENU = 'main_menu'
STATE_PLAY_SELECT = 'play_select'
STATE_OPTIONS = 'options'
STATE_GAME = 'game'
STATE_MATCH3 = 'match3'

class TownshipGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Township - Python Edition")

        # Fonts
        self.font_title = pygame.font.SysFont("Trebuchet MS, Arial", 26, bold=True)
        self.font_bold = pygame.font.SysFont("Trebuchet MS, Arial", 16, bold=True)
        self.font_reg = pygame.font.SysFont("Trebuchet MS, Arial", 14)
        self.font_small = pygame.font.SysFont("Trebuchet MS, Arial", 12, bold=True)

        self.clock = pygame.time.Clock()
        self.running = True

        # State Machine
        self.state_name = STATE_MAIN_MENU
        self.previous_state = STATE_MAIN_MENU

        # Managers & Loaders
        self.sound = get_sound_manager()
        self.sprites = get_sprite_manager()
        self.assets = get_asset_loader()
        self.anim_manager = get_animation_manager()
        self.state = GameState()

        # Gameplay Systems
        self.farming_sys = FarmingSystem(self.state)
        self.livestock_sys = LivestockSystem(self.state)
        self.mfg_sys = ManufacturingSystem(self.state)
        self.build_sys = CityBuildingSystem(self.state)

        # UI & Screens
        self.hud = HUD(self.state, self.sprites)
        self.modals = ModalManager(self.state, self.sprites)
        self.match3 = Match3Game(self.state, self.sprites)

        self.screen_main_menu = MainMenuScreen(self.assets, self.sprites)
        self.screen_play_select = PlaySelectScreen(self.assets, self.sprites)
        self.screen_options = OptionsScreen()

        # In-Game Pause Dialog
        self.is_paused = False
        self._init_pause_menu()

        # Camera & World Coordinates
        self.cam_x = 18 * TILE_SIZE - SCREEN_WIDTH // 2
        self.cam_y = 14 * TILE_SIZE - SCREEN_HEIGHT // 2
        self.drag_start = None
        self.cam_start = None

        # Seed Selector
        self.seed_picker_plot = None
        self.seed_picker_pos = (0, 0)

        # Autosave
        self.autosave_timer = 60.0

    def _init_pause_menu(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        btn_w, btn_h = 240, 48

        self.btn_resume = ModernButton(pygame.Rect(cx - btn_w // 2, cy - 80, btn_w, btn_h), "RESUME", color=(85, 185, 60), border_radius=10)
        self.btn_save_town = ModernButton(pygame.Rect(cx - btn_w // 2, cy - 20, btn_w, btn_h), "SAVE TOWN", color=(52, 152, 219), border_radius=10)
        self.btn_quit_to_menu = ModernButton(pygame.Rect(cx - btn_w // 2, cy + 40, btn_w, btn_h), "MAIN MENU", color=(225, 75, 60), border_radius=10)
        self.pause_buttons = [self.btn_resume, self.btn_save_town, self.btn_quit_to_menu]

    # -------------------------------------------------------------
    # COORDINATE CONVERSIONS
    # -------------------------------------------------------------
    def screen_to_world(self, sx: int, sy: int) -> Tuple[int, int]:
        return sx + self.cam_x, sy + self.cam_y

    def world_to_screen(self, wx: int, wy: int) -> Tuple[int, int]:
        return wx - self.cam_x, wy - self.cam_y

    def screen_to_grid(self, sx: int, sy: int) -> Tuple[int, int]:
        wx, wy = self.screen_to_world(sx, sy)
        return wx // TILE_SIZE, wy // TILE_SIZE

    def grid_to_screen(self, gx: int, gy: int) -> Tuple[int, int]:
        return self.world_to_screen(gx * TILE_SIZE, gy * TILE_SIZE)

    # -------------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.1)

            mouse_pos = pygame.mouse.get_pos()
            self._handle_events()
            self._update(dt, mouse_pos)
            self._render()

        if self.state_name == STATE_GAME:
            self.state.save_to_slot(getattr(self.state, 'active_slot', 1))

        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------
    # EVENTS
    # -------------------------------------------------------------
    def _handle_events(self):
        sw, sh = self.screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self._init_pause_menu()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.is_paused:
                        self.is_paused = False
                    elif self.state_name == STATE_GAME:
                        if self.modals.active_modal:
                            self.modals.close_modal()
                        elif self.modals.placement_item:
                            self.modals.placement_item = None
                            self.state.add_toast("Placement cancelled.", color=(200, 200, 200))
                        elif self.seed_picker_plot:
                            self.seed_picker_plot = None
                        else:
                            self.is_paused = True
                    elif self.state_name == STATE_MATCH3:
                        self.state_name = STATE_GAME
                    elif self.state_name in (STATE_PLAY_SELECT, STATE_OPTIONS):
                        self.state_name = STATE_MAIN_MENU

                elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    if self.state_name == STATE_GAME:
                        self.state.save_to_slot(getattr(self.state, 'active_slot', 1))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                self._handle_mouse_down(event.button, mx, my, sw, sh)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (2, 3):
                    self.drag_start = None
                    self.cam_start = None

            elif event.type == pygame.MOUSEMOTION:
                if self.drag_start and self.cam_start:
                    dx = event.pos[0] - self.drag_start[0]
                    dy = event.pos[1] - self.drag_start[1]
                    self.cam_x = self.cam_start[0] - dx
                    self.cam_y = self.cam_start[1] - dy

        # Keyboard camera pan in town
        if self.state_name == STATE_GAME and not self.is_paused and not self.modals.active_modal:
            keys = pygame.key.get_pressed()
            pan_speed = 10
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.cam_x -= pan_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.cam_x += pan_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.cam_y -= pan_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.cam_y += pan_speed

            max_cam_x = self.state.grid_width * TILE_SIZE - sw + 200
            max_cam_y = self.state.grid_height * TILE_SIZE - sh + 200
            self.cam_x = max(-200, min(self.cam_x, max_cam_x))
            self.cam_y = max(-200, min(self.cam_y, max_cam_y))

    def _handle_mouse_down(self, button: int, mx: int, my: int, sw: int, sh: int):
        # 1. Main Menu Clicks
        if self.state_name == STATE_MAIN_MENU:
            action = self.screen_main_menu.handle_click((mx, my))
            if action == 'play':
                self.screen_play_select.refresh_slots()
                self.screen_play_select._init_slot_buttons()
                self.state_name = STATE_PLAY_SELECT
            elif action == 'options':
                self.previous_state = STATE_MAIN_MENU
                self.state_name = STATE_OPTIONS
            elif action == 'quit':
                self.running = False
            return

        # 2. Play Select Clicks
        elif self.state_name == STATE_PLAY_SELECT:
            action, slot_id = self.screen_play_select.handle_click((mx, my))
            if action == 'back':
                self.state_name = STATE_MAIN_MENU
            elif action == 'play_slot':
                meta = GameState.get_slot_metadata(slot_id)
                if meta['exists']:
                    self.state.load_from_slot(slot_id)
                else:
                    self.state.reset_to_starter_town()
                    self.state.town_name = f"Town {slot_id}"
                    self.state.save_to_slot(slot_id)
                self.state_name = STATE_GAME
            return

        # 3. Options Clicks
        elif self.state_name == STATE_OPTIONS:
            action = self.screen_options.handle_click((mx, my))
            if action == 'back':
                self.state_name = self.previous_state
            return

        # 4. In-Game Pause Dialog Clicks
        if self.is_paused:
            if self.btn_resume.handle_click((mx, my)):
                self.is_paused = False
            elif self.btn_save_town.handle_click((mx, my)):
                self.state.save_to_slot(getattr(self.state, 'active_slot', 1))
            elif self.btn_quit_to_menu.handle_click((mx, my)):
                self.state.save_to_slot(getattr(self.state, 'active_slot', 1))
                self.is_paused = False
                self.state_name = STATE_MAIN_MENU
            return

        # 5. Match-3 Mode Clicks
        if self.state_name == STATE_MATCH3:
            res = self.match3.handle_click(mx, my, sw, sh)
            if res == "exit":
                self.state_name = STATE_GAME
            return

        # 6. Active Modal Clicks
        if self.modals.active_modal:
            self.modals.handle_click(mx, my, sw, sh, self.farming_sys, self.livestock_sys, self.mfg_sys, self.build_sys)
            return

        # 7. Seed Picker Clicks
        if self.seed_picker_plot:
            if self._handle_seed_picker_click(mx, my):
                return

        # 8. HUD & Dock Clicks
        dock_action = self.hud.handle_click(mx, my, sw, sh)
        if dock_action != "none":
            if dock_action == 'menu':
                self.is_paused = True
            else:
                self._handle_dock_action(dock_action)
            return

        # Ignore world clicks if in top status bar
        if my < 58:
            return

        # 9. Placement Mode Clicks
        if self.modals.placement_item:
            if button == 1:
                gx, gy = self.screen_to_grid(mx, my)
                item_id, category = self.modals.placement_item
                if category == 'road':
                    self.build_sys.place_road(item_id, gx, gy)
                else:
                    res = self.build_sys.place_building(item_id, category, gx, gy)
                    if res:
                        self.modals.placement_item = None
            elif button == 3:
                self.modals.placement_item = None
                self.state.add_toast("Placement cancelled.", color=(200, 200, 200))
            return

        # 10. World Interactions & Drag Pan
        if button == 1:
            gx, gy = self.screen_to_grid(mx, my)
            self._handle_world_click(gx, gy, mx, my)

        elif button in (2, 3):
            self.drag_start = (mx, my)
            self.cam_start = (self.cam_x, self.cam_y)

    def _handle_world_click(self, gx: int, gy: int, mx: int, my: int):
        b = self.state.get_building_at(gx, gy)
        if not b:
            self.seed_picker_plot = None
            return

        cat = b.get('category')

        if cat == 'crop':
            if b.get('planted_crop') is None:
                self.seed_picker_plot = b
                self.seed_picker_pos = (mx, my)
                self.sound.play('click')
            else:
                if self.farming_sys.is_crop_ripe(b):
                    self.farming_sys.harvest_crop(b)
                else:
                    self.farming_sys.speedup_crop(b)
            return

        if b['type'] == 'helipad':
            self.modals.open_modal('orders')
            return

        if cat in ('factory', 'shed'):
            self.modals.open_modal('factory', building=b)
            return

        if b['type'] == 'town_hall':
            self.modals.open_modal('quests')
            return

        if cat in ('house', 'decoration'):
            name = HOUSES.get(b['type'], {}).get('name') or DECORATIONS.get(b['type'], {}).get('name', 'Building')
            self.state.add_toast(f"{name} (Status: Happy Residents)", color=(140, 220, 255))
            self.sound.play('click')

    def _handle_dock_action(self, action: str):
        if action == 'build':
            self.modals.open_modal('build')
        elif action == 'orders':
            self.modals.open_modal('orders')
        elif action == 'barn':
            self.modals.open_modal('barn')
        elif action == 'match3':
            self.state_name = STATE_MATCH3
            self.match3.restart_level()
        elif action == 'daily':
            self.modals.open_modal('daily')
        elif action == 'quests':
            self.modals.open_modal('quests')
        elif action == 'save':
            self.state.save_to_slot(getattr(self.state, 'active_slot', 1))

    def _handle_seed_picker_click(self, mx: int, my: int) -> bool:
        px, py = self.seed_picker_pos
        crop_list = list(CROPS.keys())
        card_w, card_h = 64, 76
        start_x = px - (len(crop_list) * card_w) // 2
        start_y = py - 95

        for i, crop_k in enumerate(crop_list):
            cx = start_x + i * (card_w + 6)
            cy = start_y
            rect = pygame.Rect(cx, cy, card_w, card_h)
            if rect.collidepoint(mx, my):
                self.farming_sys.plant_crop(self.seed_picker_plot, crop_k)
                self.seed_picker_plot = None
                return True

        self.seed_picker_plot = None
        return True

    # -------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------
    def _update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.anim_manager.update(dt)
        if self.state_name == STATE_MAIN_MENU:
            self.screen_main_menu.update(mouse_pos)
        elif self.state_name == STATE_PLAY_SELECT:
            self.screen_play_select.update(mouse_pos)
        elif self.state_name == STATE_OPTIONS:
            self.screen_options.update(mouse_pos)
        elif self.state_name == STATE_GAME:
            if self.is_paused:
                for btn in self.pause_buttons:
                    btn.update(mouse_pos)
            else:
                self.hud.update(mouse_pos)
                self.state.tick(dt)
                self.autosave_timer -= dt
                if self.autosave_timer <= 0:
                    self.state.save_to_slot(getattr(self.state, 'active_slot', 1))
                    self.autosave_timer = 60.0

    # -------------------------------------------------------------
    # RENDERING
    # -------------------------------------------------------------
    def _render(self):
        sw, sh = self.screen.get_size()

        if self.state_name == STATE_MAIN_MENU:
            self.screen_main_menu.render(self.screen, self.font_title, self.font_bold, self.font_reg)
            pygame.display.flip()
            return

        elif self.state_name == STATE_PLAY_SELECT:
            self.screen_play_select.render(self.screen, self.font_title, self.font_bold, self.font_reg, self.font_small)
            pygame.display.flip()
            return

        elif self.state_name == STATE_OPTIONS:
            self.screen_options.render(self.screen, self.font_title, self.font_bold, self.font_reg)
            pygame.display.flip()
            return

        elif self.state_name == STATE_MATCH3:
            self.match3.render(self.screen, self.font_title, self.font_bold)
            pygame.display.flip()
            return

        # Town Simulation Screen
        self.screen.fill(COLOR_BG)

        # 1. Terrain & Roads
        self._render_terrain(sw, sh)

        # 2. Buildings & Crops
        self._render_buildings(sw, sh)

        # 3. Helicopter
        self._render_helicopter(sw, sh)

        # 4. Ghost Placement
        if self.modals.placement_item:
            self._render_placement_ghost()

        # 5. Seed Picker
        if self.seed_picker_plot:
            self._render_seed_picker()

        # 6. HUD & Modals
        self.hud.render(self.screen, self.font_bold, self.font_reg, self.font_small)
        self.modals.render(self.screen, self.font_title, self.font_bold, self.font_reg, self.font_small)

        # 7. Pause Dialog Overlay
        if self.is_paused:
            self._render_pause_dialog(sw, sh)

        pygame.display.flip()

    def _render_terrain(self, sw: int, sh: int):
        min_gx = max(0, self.cam_x // TILE_SIZE)
        max_gx = min(self.state.grid_width, (self.cam_x + sw) // TILE_SIZE + 1)
        min_gy = max(0, self.cam_y // TILE_SIZE)
        max_gy = min(self.state.grid_height, (self.cam_y + sh) // TILE_SIZE + 1)

        # Flexible grass loading (grass.png, town_terrain.png, terrain.png)
        custom_grass = self.assets.load_first_available("backgrounds", ["grass", "town_terrain", "terrain"], scale=(TILE_SIZE, TILE_SIZE))
        grass_surf = custom_grass if custom_grass else self.sprites.roads.get('grass')

        for gy in range(min_gy, max_gy):
            for gx in range(min_gx, max_gx):
                sx, sy = self.grid_to_screen(gx, gy)
                if grass_surf:
                    self.screen.blit(grass_surf, (sx, sy))

                r_type = self.state.roads.get(f"{gx},{gy}")
                if r_type:
                    if r_type == 'water_canal':
                        # Render animated shimmering water
                        water_frame = self.anim_manager.get_frame('water')
                        if water_frame:
                            self.screen.blit(water_frame, (sx, sy))
                        else:
                            self.screen.blit(self.sprites.roads.get('water_canal'), (sx, sy))
                    else:
                        custom_road = self.assets.load_first_available("backgrounds", [r_type, r_type.replace('road_', '')], scale=(TILE_SIZE, TILE_SIZE))
                        r_surf = custom_road if custom_road else self.sprites.roads.get(r_type)
                        if r_surf:
                            self.screen.blit(r_surf, (sx, sy))

    def _render_buildings(self, sw: int, sh: int):
        sorted_b = sorted(self.state.buildings, key=lambda b: (b['gy'] + b['h'], b['gx']))

        for b in sorted_b:
            sx, sy = self.grid_to_screen(b['gx'], b['gy'])
            w_px = b['w'] * TILE_SIZE
            h_px = b['h'] * TILE_SIZE

            if sx + w_px < 0 or sx > sw or sy + h_px < 0 or sy > sh:
                continue

            cat = b['category']
            b_type = b['type']

            if cat == 'crop':
                plot_surf = self.sprites.roads.get('field_plot')
                if plot_surf:
                    self.screen.blit(plot_surf, (sx, sy))

                planted = b.get('planted_crop')
                if planted:
                    stage = self.farming_sys.get_crop_stage(b)
                    custom_crop = self.assets.load_first_available("crops", [f"{planted}_{stage}", f"{planted}_{stage}.png"], scale=(TILE_SIZE, TILE_SIZE))
                    if custom_crop:
                        self.screen.blit(custom_crop, (sx, sy))
                    else:
                        crop_stages = self.sprites.crops.get(planted, [])
                        if stage < len(crop_stages):
                            self.screen.blit(crop_stages[stage], (sx, sy))

                    if self.farming_sys.is_crop_ripe(b):
                        pulse = int(math.sin(time.time() * 6) * 3)
                        xp_star = self.sprites.icons.get('xp')
                        if xp_star:
                            self.screen.blit(xp_star, (sx + (TILE_SIZE - 32) // 2, sy - 14 + pulse))

            elif cat == 'decoration':
                custom_dec = self.assets.load_first_available("buildings", [b_type, b_type.replace('_', '')], scale=(w_px, h_px))
                dec_surf = custom_dec if custom_dec else self.sprites.decorations.get(b_type)
                if dec_surf:
                    self.screen.blit(dec_surf, (sx, sy))

                # Animated Fountain splash
                if b_type == 'fountain':
                    fnt_frame = self.anim_manager.get_frame('fountain')
                    if fnt_frame:
                        self.screen.blit(fnt_frame, (sx + (w_px - 64) // 2, sy + (h_px - 64) // 2 - 8))

            else:
                # Flexible building lookup: e.g. cottage.png, cottage, house, etc.
                custom_b = self.assets.load_first_available("buildings", [b_type, b_type.replace('_', ''), b_type.split('_')[0]], scale=(w_px, h_px))
                b_surf = custom_b if custom_b else self.sprites.buildings.get(b_type)
                if b_surf:
                    self.screen.blit(b_surf, (sx, sy))

                # Windmill Animation for Feed Mill
                if b_type == 'feed_mill':
                    wm_frame = self.anim_manager.get_frame('windmill')
                    if wm_frame:
                        self.screen.blit(wm_frame, (sx + w_px - 44, sy + 18))

                # Animal Animations for Sheds
                if b_type == 'cow_shed':
                    cow_frame = self.anim_manager.get_frame('cow')
                    if cow_frame:
                        for cx in [32, 74, 116]:
                            self.screen.blit(cow_frame, (sx + cx - 16, sy + 44))
                elif b_type == 'chicken_coop':
                    chk_frame = self.anim_manager.get_frame('chicken')
                    if chk_frame:
                        for cx in [30, 60, 90, 120]:
                            self.screen.blit(chk_frame, (sx + cx - 10, sy + 40))
                elif b_type == 'pig_pen':
                    pig_frame = self.anim_manager.get_frame('pig')
                    if pig_frame:
                        for px in [38, 78, 118]:
                            self.screen.blit(pig_frame, (sx + px - 16, sy + 44))
                elif b_type == 'sheep_pen':
                    shp_frame = self.anim_manager.get_frame('sheep')
                    if shp_frame:
                        for sx_pos in [36, 76, 116]:
                            self.screen.blit(shp_frame, (sx + sx_pos - 16, sy + 42))

                # Factory Smoke Animation for active queues
                if cat == 'factory' and b.get('queue'):
                    smoke_frame = self.anim_manager.get_frame('smoke')
                    if smoke_frame:
                        self.screen.blit(smoke_frame, (sx + w_px - 40, sy - 6))

            # Factory & Shed Progress / Ready Indicators
            if cat == 'factory':
                queue = b.get('queue', [])
                completed = b.get('completed', [])
                if completed:
                    pulse = int(math.sin(time.time() * 6) * 4)
                    icon = self.sprites.icons.get(completed[0])
                    if icon:
                        self.screen.blit(icon, (sx + (w_px - 32) // 2, sy - 16 + pulse))
                elif queue:
                    curr = queue[0]
                    ratio = 1.0 - max(0.0, curr['remaining'] / max(0.1, curr['total']))
                    pb_w = w_px - 20
                    pygame.draw.rect(self.screen, (40, 40, 45), (sx + 10, sy + h_px - 14, pb_w, 8), border_radius=4)
                    pygame.draw.rect(self.screen, (75, 185, 240), (sx + 10, sy + h_px - 14, int(pb_w * ratio), 8), border_radius=4)

            elif cat == 'shed':
                ready_count = b.get('ready_count', 0)
                if ready_count > 0:
                    pulse = int(math.sin(time.time() * 6) * 4)
                    prod_name = SHEDS[b_type]['product']
                    icon = self.sprites.icons.get(prod_name)
                    if icon:
                        self.screen.blit(icon, (sx + (w_px - 32) // 2, sy - 16 + pulse))
                elif b.get('fed', False):
                    elapsed = time.time() - b.get('feed_time', 0.0)
                    ratio = min(1.0, elapsed / max(0.1, b.get('duration', 10.0)))
                    pb_w = w_px - 20
                    pygame.draw.rect(self.screen, (40, 40, 45), (sx + 10, sy + h_px - 14, pb_w, 8), border_radius=4)
                    pygame.draw.rect(self.screen, (95, 195, 60), (sx + 10, sy + h_px - 14, int(pb_w * ratio), 8), border_radius=4)

    def _render_helicopter(self, sw: int, sh: int):
        helipad = next((b for b in self.state.buildings if b['type'] == 'helipad'), None)
        if not helipad:
            return

        hx, hy = self.grid_to_screen(helipad['gx'] + 1, helipad['gy'] + 1)
        custom_heli = self.assets.load_image("buildings/helicopter.png", scale=(84, 60))
        heli_surf = custom_heli if custom_heli else self.sprites.buildings.get('helicopter')
        if not heli_surf:
            return

        if self.state.helicopter_state == 'idle':
            self.screen.blit(heli_surf, (hx - heli_surf.get_width() // 2, hy - heli_surf.get_height() // 2))

        elif self.state.helicopter_state in ('flying_out', 'flying_back'):
            t = self.state.helicopter_timer
            if self.state.helicopter_state == 'flying_out':
                flight_prog = (3.5 - t) / 1.75
            else:
                flight_prog = t / 1.75

            fx = hx + int(flight_prog * (sw - hx + 100))
            fy = hy - int(flight_prog * (hy + 100))
            bob = int(math.sin(time.time() * 15) * 4)

            self.screen.blit(heli_surf, (fx - heli_surf.get_width() // 2, fy - heli_surf.get_height() // 2 + bob))

    def _render_placement_ghost(self):
        mx, my = pygame.mouse.get_pos()
        gx, gy = self.screen_to_grid(mx, my)
        item_id, category = self.modals.placement_item

        info = self.build_sys._get_building_info(item_id, category)
        w, h = info.get('size', (1, 1)) if info else (1, 1)

        sx, sy = self.grid_to_screen(gx, gy)
        can_place, _ = self.build_sys.can_place_building(item_id, category, gx, gy)

        ghost_col = (90, 220, 90, 120) if can_place else (240, 70, 70, 120)
        ghost = pygame.Surface((w * TILE_SIZE, h * TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(ghost, ghost_col, (0, 0, w * TILE_SIZE, h * TILE_SIZE), border_radius=6)
        pygame.draw.rect(ghost, (255, 255, 255, 180), (0, 0, w * TILE_SIZE, h * TILE_SIZE), 2, border_radius=6)
        self.screen.blit(ghost, (sx, sy))

    def _render_seed_picker(self):
        px, py = self.seed_picker_pos
        crop_list = list(CROPS.keys())
        card_w, card_h = 64, 76
        total_w = len(crop_list) * (card_w + 6)
        start_x = px - total_w // 2
        start_y = py - 95

        pygame.draw.rect(self.screen, (252, 248, 235), (start_x - 10, start_y - 8, total_w + 14, card_h + 16), border_radius=12)
        pygame.draw.rect(self.screen, (165, 120, 75), (start_x - 10, start_y - 8, total_w + 14, card_h + 16), 3, border_radius=12)

        for i, crop_k in enumerate(crop_list):
            c_info = CROPS[crop_k]
            cx = start_x + i * (card_w + 6)
            cy = start_y

            is_locked = self.state.level < c_info['min_level']
            pygame.draw.rect(self.screen, (240, 240, 240) if is_locked else (255, 255, 255), (cx, cy, card_w, card_h), border_radius=8)
            pygame.draw.rect(self.screen, (200, 190, 175), (cx, cy, card_w, card_h), 1, border_radius=8)

            icon = self.sprites.icons.get(crop_k)
            if icon:
                self.screen.blit(icon, (cx + (card_w - 32) // 2, cy + 6))

            name_txt = self.font_small.render(c_info['name'][:7], True, (50, 40, 30))
            self.screen.blit(name_txt, (cx + (card_w - name_txt.get_width()) // 2, cy + 38))

            if is_locked:
                req_txt = self.font_small.render(f"L{c_info['min_level']}", True, (215, 60, 60))
                self.screen.blit(req_txt, (cx + (card_w - req_txt.get_width()) // 2, cy + 54))
            else:
                cost_txt = self.font_small.render(f"{c_info['cost']}c", True, (215, 140, 20))
                self.screen.blit(cost_txt, (cx + (card_w - cost_txt.get_width()) // 2, cy + 54))

    def _render_pause_dialog(self, sw: int, sh: int):
        dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self.screen.blit(dim, (0, 0))

        dw, dh = 360, 280
        dx = (sw - dw) // 2
        dy = (sh - dh) // 2

        ModernCard.draw(
            self.screen,
            pygame.Rect(dx, dy, dw, dh),
            bg_color=(252, 248, 238),
            border_color=(205, 195, 180),
            header_color=(245, 175, 65),
            header_height=46
        )

        p_title = self.font_bold.render("GAME PAUSED", True, (255, 255, 255))
        self.screen.blit(p_title, (dx + (dw - p_title.get_width()) // 2, dy + 13))

        for btn in self.pause_buttons:
            btn.draw(self.screen, self.font_bold)

if __name__ == '__main__':
    game = TownshipGame()
    game.run()
