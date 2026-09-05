"""
Township - Menu Screens (Title / Main Menu, Save Slot Selection, Options)
Renders modern, polished pre-game screens with interactive buttons,
save game metadata inspection, and sound/display settings.
"""

import math
import time
import pygame
from typing import Dict, List, Optional, Tuple, Callable
from config import (
    COLOR_BG, COLOR_GRASS_LIGHT, COLOR_GRASS_DARK, COLOR_WATER,
    COLOR_GOLD, COLOR_TCASH, COLOR_BTN_GREEN, COLOR_BTN_BLUE,
    COLOR_BTN_ORANGE, COLOR_BTN_RED, COLOR_TEXT_DARK, COLOR_TEXT_LIGHT
)
from sound_manager import get_sound_manager
from game_state import GameState
from ui.components import ModernButton, ModernCard

class MainMenuScreen:
    def __init__(self, asset_loader, sprite_manager):
        self.assets = asset_loader
        self.sprites = sprite_manager
        self.buttons = []
        self._init_buttons()

    def _init_buttons(self):
        cx = 1280 // 2
        btn_w, btn_h = 280, 56
        self.btn_play = ModernButton(
            pygame.Rect(cx - btn_w // 2, 380, btn_w, btn_h),
            "PLAY",
            color=(80, 185, 55),
            hover_color=(100, 210, 75),
            border_radius=14
        )
        self.btn_options = ModernButton(
            pygame.Rect(cx - btn_w // 2, 455, btn_w, btn_h),
            "OPTIONS",
            color=(52, 152, 219),
            hover_color=(70, 175, 240),
            border_radius=14
        )
        self.btn_quit = ModernButton(
            pygame.Rect(cx - btn_w // 2, 530, btn_w, btn_h),
            "QUIT",
            color=(225, 75, 60),
            hover_color=(245, 95, 80),
            border_radius=14
        )
        self.buttons = [self.btn_play, self.btn_options, self.btn_quit]

    def update(self, mouse_pos: Tuple[int, int]):
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface: pygame.Surface, font_title, font_bold, font_reg):
        w, h = surface.get_size()

        # Check for custom background from assets/backgrounds/ (menu_background.png or menu_bg.png)
        custom_bg = self.assets.load_first_available("backgrounds", ["menu_background", "menu_bg", "background", "title_bg"], scale=(w, h))
        if custom_bg:
            surface.blit(custom_bg, (0, 0))
        else:
            self._render_procedural_background(surface, w, h)

        # Draw Animated Township Logo
        t = time.time()
        bob = int(math.sin(t * 3) * 6)
        logo_y = 120 + bob

        # Logo shadow & plate
        logo_w, logo_h = 560, 140
        lx = (w - logo_w) // 2
        pygame.draw.rect(surface, (0, 0, 0, 40), (lx, logo_y + 8, logo_w, logo_h), border_radius=22)
        pygame.draw.rect(surface, (252, 248, 235), (lx, logo_y, logo_w, logo_h), border_radius=22)
        pygame.draw.rect(surface, (242, 165, 65), (lx, logo_y, logo_w, logo_h), 5, border_radius=22)

        # Big "TOWNSHIP" 3D title text
        title_font = pygame.font.SysFont("Trebuchet MS, Arial", 54, bold=True)
        sub_font = pygame.font.SysFont("Trebuchet MS, Arial", 18, bold=True)

        # 3D text shadow
        shadow_txt = title_font.render("TOWNSHIP", True, (160, 105, 45))
        surface.blit(shadow_txt, (w // 2 - shadow_txt.get_width() // 2, logo_y + 24))

        main_txt = title_font.render("TOWNSHIP", True, (75, 175, 45))
        surface.blit(main_txt, (w // 2 - main_txt.get_width() // 2, logo_y + 20))

        sub_txt = sub_font.render("FARMING & CITY BUILDING SIMULATION", True, (215, 135, 30))
        surface.blit(sub_txt, (w // 2 - sub_txt.get_width() // 2, logo_y + 88))

        # Render Action Buttons
        self.btn_play.rect.x = w // 2 - self.btn_play.rect.width // 2
        self.btn_options.rect.x = w // 2 - self.btn_options.rect.width // 2
        self.btn_quit.rect.x = w // 2 - self.btn_quit.rect.width // 2

        for btn in self.buttons:
            btn.draw(surface, font_bold)

        # Footer version label
        ver_txt = font_reg.render("Township Python Edition v1.2  |  Google DeepMind Agentic Pair", True, (255, 255, 255, 180))
        surface.blit(ver_txt, (w // 2 - ver_txt.get_width() // 2, h - 36))

    def _render_procedural_background(self, surface: pygame.Surface, w: int, h: int):
        # Sky gradient (Soft cyan to warm pastel sun)
        sky = pygame.Surface((w, h))
        for y in range(h):
            ratio = y / h
            r = int(125 + ratio * 40)
            g = int(200 + ratio * 30)
            b = int(245 - ratio * 35)
            pygame.draw.line(sky, (r, g, b), (0, y), (w, y))
        surface.blit(sky, (0, 0))

        # Radiant Sun
        pygame.draw.circle(surface, (255, 245, 180, 160), (w - 180, 120), 80)
        pygame.draw.circle(surface, (255, 225, 100), (w - 180, 120), 45)

        # Rolling green hills at bottom
        pygame.draw.ellipse(surface, (125, 195, 80), (-150, h - 260, w + 300, 360))
        pygame.draw.ellipse(surface, (145, 215, 95), (-80, h - 210, w + 160, 320))

        # Clouds
        for cx, cy, sz in [(180, 100, 45), (460, 80, 35), (880, 140, 50)]:
            pygame.draw.circle(surface, (255, 255, 255, 200), (cx, cy), sz)
            pygame.draw.circle(surface, (255, 255, 255, 200), (cx + int(sz * 0.7), cy - 6), int(sz * 0.8))
            pygame.draw.circle(surface, (255, 255, 255, 200), (cx - int(sz * 0.7), cy + 2), int(sz * 0.7))

    def handle_click(self, mouse_pos: Tuple[int, int]) -> str:
        if self.btn_play.handle_click(mouse_pos):
            return "play"
        elif self.btn_options.handle_click(mouse_pos):
            return "options"
        elif self.btn_quit.handle_click(mouse_pos):
            return "quit"
        return "none"


class PlaySelectScreen:
    def __init__(self, asset_loader, sprite_manager):
        self.assets = asset_loader
        self.sprites = sprite_manager
        self.slots_metadata = []
        self.refresh_slots()

        # Navigation
        self.btn_back = ModernButton(
            pygame.Rect(40, 36, 140, 44),
            "< BACK",
            color=(120, 130, 145),
            hover_color=(140, 150, 165),
            border_radius=10
        )

        self.slot_buttons = {}  # slot_id -> {'play': btn, 'delete': btn}
        self._init_slot_buttons()

    def refresh_slots(self):
        self.slots_metadata = [
            GameState.get_slot_metadata(1),
            GameState.get_slot_metadata(2),
            GameState.get_slot_metadata(3)
        ]

    def _init_slot_buttons(self):
        self.slot_buttons = {}
        for s_id in [1, 2, 3]:
            meta = self.slots_metadata[s_id - 1]
            btn_play_label = "CONTINUE" if meta['exists'] else "NEW TOWN"
            btn_play_col = (85, 185, 60) if meta['exists'] else (52, 152, 219)

            self.slot_buttons[s_id] = {
                'play': ModernButton(pygame.Rect(0, 0, 200, 46), btn_play_label, color=btn_play_col, border_radius=10),
                'delete': ModernButton(pygame.Rect(0, 0, 60, 46), "DEL", color=(225, 75, 60), border_radius=10)
            }

    def update(self, mouse_pos: Tuple[int, int]):
        self.btn_back.update(mouse_pos)
        for s_btns in self.slot_buttons.values():
            s_btns['play'].update(mouse_pos)
            s_btns['delete'].update(mouse_pos)

    def render(self, surface: pygame.Surface, font_title, font_bold, font_reg, font_small):
        w, h = surface.get_size()

        # Background
        surface.fill((242, 246, 238))
        pygame.draw.rect(surface, (140, 205, 95), (0, 0, w, 110))
        pygame.draw.line(surface, (115, 175, 75), (0, 110), (w, 110), 3)

        # Back button
        self.btn_back.draw(surface, font_bold)

        # Header title
        title_txt = font_title.render("SELECT TOWN / SAVE SLOT", True, (255, 255, 255))
        surface.blit(title_txt, (w // 2 - title_txt.get_width() // 2, 38))

        # 3 Save Slot Cards
        card_w, card_h = 340, 460
        spacing = 40
        total_w = 3 * card_w + 2 * spacing
        start_x = (w - total_w) // 2
        card_y = 170

        for i, meta in enumerate(self.slots_metadata):
            s_id = meta['slot_id']
            cx = start_x + i * (card_w + spacing)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)

            header_col = (245, 175, 65) if meta['exists'] else (160, 170, 185)
            ModernCard.draw(surface, card_rect, bg_color=(255, 255, 255), border_color=(205, 195, 180), header_color=header_col, header_height=50)

            # Slot Header
            slot_title = font_bold.render(f"SLOT {s_id}", True, (255, 255, 255))
            surface.blit(slot_title, (cx + (card_w - slot_title.get_width()) // 2, card_y + 14))

            if meta['exists']:
                # Town Name
                name_txt = font_title.render(meta['town_name'][:18], True, COLOR_TEXT_DARK)
                surface.blit(name_txt, (cx + (card_w - name_txt.get_width()) // 2, card_y + 75))

                # Level Badge
                lvl_cx, lvl_cy = cx + card_w // 2, card_y + 160
                pygame.draw.circle(surface, (65, 150, 230), (lvl_cx, lvl_cy), 36)
                pygame.draw.circle(surface, (35, 105, 180), (lvl_cx, lvl_cy), 36, 3)
                l_txt = font_bold.render(f"LVL {meta['level']}", True, (255, 255, 255))
                surface.blit(l_txt, (lvl_cx - l_txt.get_width() // 2, lvl_cy - l_txt.get_height() // 2))

                # Stats Pills (Coins, T-Cash, Pop)
                sy = card_y + 220
                for icon_k, val_str, col in [
                    ('coin', f"{meta['coins']:,} Coins", (215, 140, 20)),
                    ('tcash', f"{meta['tcash']} T-Cash", COLOR_TCASH),
                    ('pop', f"{meta['population']} Citizens", (50, 120, 190))
                ]:
                    icon = self.sprites.icons.get(icon_k)
                    if icon:
                        sc = pygame.transform.smoothscale(icon, (24, 24))
                        surface.blit(sc, (cx + 50, sy))
                    stat_txt = font_bold.render(val_str, True, col)
                    surface.blit(stat_txt, (cx + 86, sy + 2))
                    sy += 36

                # Last saved timestamp
                time_lbl = font_small.render(f"Saved: {meta['last_saved']}", True, (140, 130, 120))
                surface.blit(time_lbl, (cx + (card_w - time_lbl.get_width()) // 2, card_y + 342))

                # Play & Delete Buttons
                p_btn = self.slot_buttons[s_id]['play']
                p_btn.label = "CONTINUE"
                p_btn.color = (85, 185, 60)
                p_btn.rect = pygame.Rect(cx + 30, card_y + 380, card_w - 110, 48)
                p_btn.draw(surface, font_bold)

                d_btn = self.slot_buttons[s_id]['delete']
                d_btn.rect = pygame.Rect(cx + card_w - 70, card_y + 380, 44, 48)
                d_btn.draw(surface, font_bold)

            else:
                # Empty Slot layout
                emp_title = font_bold.render("EMPTY SLOT", True, (160, 150, 140))
                surface.blit(emp_title, (cx + (card_w - emp_title.get_width()) // 2, card_y + 110))

                sub_desc = font_reg.render("Start a brand new town here!", True, (170, 160, 150))
                surface.blit(sub_desc, (cx + (card_w - sub_desc.get_width()) // 2, card_y + 140))

                # New Town Button
                p_btn = self.slot_buttons[s_id]['play']
                p_btn.label = "START NEW TOWN"
                p_btn.color = (52, 152, 219)
                p_btn.rect = pygame.Rect(cx + 30, card_y + 380, card_w - 60, 48)
                p_btn.draw(surface, font_bold)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> Tuple[str, Optional[int]]:
        if self.btn_back.handle_click(mouse_pos):
            return "back", None

        for s_id, s_btns in self.slot_buttons.items():
            if s_btns['play'].handle_click(mouse_pos):
                return "play_slot", s_id
            if s_btns['delete'].handle_click(mouse_pos):
                GameState.delete_slot(s_id)
                self.refresh_slots()
                self._init_slot_buttons()
                get_sound_manager().play('click')
                return "deleted_slot", s_id

        return "none", None


class OptionsScreen:
    def __init__(self):
        self.btn_back = ModernButton(
            pygame.Rect(40, 36, 140, 44),
            "< BACK",
            color=(120, 130, 145),
            hover_color=(140, 150, 165),
            border_radius=10
        )
        self.sound = get_sound_manager()
        self.btn_sound_toggle = ModernButton(
            pygame.Rect(0, 0, 220, 48),
            "SOUND: ON",
            color=(80, 180, 60),
            border_radius=10
        )

    def update(self, mouse_pos: Tuple[int, int]):
        self.btn_back.update(mouse_pos)
        self.btn_sound_toggle.update(mouse_pos)

    def render(self, surface: pygame.Surface, font_title, font_bold, font_reg):
        w, h = surface.get_size()

        surface.fill((242, 246, 238))
        pygame.draw.rect(surface, (52, 152, 219), (0, 0, w, 110))
        pygame.draw.line(surface, (35, 120, 180), (0, 110), (w, 110), 3)

        self.btn_back.draw(surface, font_bold)

        title_txt = font_title.render("OPTIONS & SETTINGS", True, (255, 255, 255))
        surface.blit(title_txt, (w // 2 - title_txt.get_width() // 2, 38))

        # Main Settings Card
        card_w, card_h = 600, 440
        cx = (w - card_w) // 2
        cy = 170
        card_rect = pygame.Rect(cx, cy, card_w, card_h)

        ModernCard.draw(surface, card_rect, bg_color=(255, 255, 255), border_color=(205, 195, 180), header_color=(235, 240, 245), header_height=50)

        c_title = font_bold.render("AUDIO & CONTROLS", True, COLOR_TEXT_DARK)
        surface.blit(c_title, (cx + 24, cy + 15))

        # Sound Toggle Row
        sound_lbl = font_bold.render("Sound Effects & Music:", True, COLOR_TEXT_DARK)
        surface.blit(sound_lbl, (cx + 40, cy + 85))

        self.btn_sound_toggle.rect = pygame.Rect(cx + 340, cy + 74, 220, 44)
        self.btn_sound_toggle.label = "SOUND: ON" if self.sound.enabled else "SOUND: MUTED"
        self.btn_sound_toggle.color = (80, 180, 60) if self.sound.enabled else (180, 80, 70)
        self.btn_sound_toggle.draw(surface, font_bold)

        # Controls reference guide
        pygame.draw.line(surface, (220, 215, 205), (cx + 40, cy + 145), (cx + card_w - 40, cy + 145), 2)

        ctrl_title = font_bold.render("KEYBOARD & MOUSE CONTROLS:", True, (50, 120, 190))
        surface.blit(ctrl_title, (cx + 40, cy + 165))

        controls_list = [
            ("Pan Camera", "W, A, S, D  or  Arrow Keys  or  Right-Click Drag"),
            ("Harvest Crops", "Left-Click ripe wheat, corn, carrots, etc."),
            ("Plant Crops", "Left-Click empty plowed field plot"),
            ("Quick Save", "Ctrl + S  or  Click Save button in dock"),
            ("Cancel / Close", "ESC key  or  Click red X button")
        ]

        ky = cy + 205
        for action, binding in controls_list:
            act_txt = font_bold.render(f"- {action}:", True, COLOR_TEXT_DARK)
            bind_txt = font_reg.render(binding, True, (80, 80, 80))
            surface.blit(act_txt, (cx + 40, ky))
            surface.blit(bind_txt, (cx + 200, ky))
            ky += 34

    def handle_click(self, mouse_pos: Tuple[int, int]) -> str:
        if self.btn_back.handle_click(mouse_pos):
            return "back"
        if self.btn_sound_toggle.handle_click(mouse_pos):
            self.sound.toggle_sound()
            return "toggled_sound"
        return "none"
