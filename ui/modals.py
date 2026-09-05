"""
Township - Interactive UI Modals & Popups
Includes Build Catalog, Helicopter Order Board, Barn Inventory,
Factory & Shed Production, Daily Bonus Streak, and Ernie's Quests.
"""

import time
import pygame
from typing import Dict, List, Optional, Any, Tuple
from config import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HEADER,
    COLOR_BTN_GREEN, COLOR_BTN_BLUE, COLOR_BTN_ORANGE, COLOR_BTN_RED,
    COLOR_TEXT_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED,
    COLOR_TCASH, COLOR_GOLD,
    CROPS, SHEDS, FACTORIES, RECIPES, ALL_RECIPES, HOUSES,
    COMMUNITY_BUILDINGS, DECORATIONS, ROADS, SPECIAL_BUILDINGS,
    ALL_ITEMS, DAILY_REWARDS
)
from sound_manager import get_sound_manager

class ModalManager:
    def __init__(self, state, sprite_manager):
        self.state = state
        self.sprites = sprite_manager
        self.active_modal: Optional[str] = None  # 'build', 'orders', 'barn', 'factory', 'daily', 'quests'
        self.selected_building: Optional[Dict[str, Any]] = None  # for factory/shed modal
        self.build_tab: str = 'farming'  # 'farming', 'houses', 'community', 'factories', 'animals', 'decorations', 'roads'
        self.placement_item: Optional[Tuple[str, str]] = None  # (item_id, category) for ghost building placement

    def open_modal(self, modal_name: str, building: Optional[Dict[str, Any]] = None):
        self.active_modal = modal_name
        self.selected_building = building
        get_sound_manager().play('click')

    def close_modal(self):
        self.active_modal = None
        self.selected_building = None
        get_sound_manager().play('click')

    # -------------------------------------------------------------
    # RENDER DISPATCHER
    # -------------------------------------------------------------
    def render(self, surface: pygame.Surface, font_title, font_bold, font_reg, font_small):
        if not self.active_modal:
            return

        w, h = surface.get_size()
        # Dim background
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        surface.blit(dim, (0, 0))

        if self.active_modal == 'build':
            self._render_build_modal(surface, w, h, font_title, font_bold, font_reg, font_small)
        elif self.active_modal == 'orders':
            self._render_orders_modal(surface, w, h, font_title, font_bold, font_reg, font_small)
        elif self.active_modal == 'barn':
            self._render_barn_modal(surface, w, h, font_title, font_bold, font_reg, font_small)
        elif self.active_modal == 'factory':
            self._render_factory_modal(surface, w, h, font_title, font_bold, font_reg, font_small)
        elif self.active_modal == 'daily':
            self._render_daily_modal(surface, w, h, font_title, font_bold, font_reg, font_small)
        elif self.active_modal == 'quests':
            self._render_quests_modal(surface, w, h, font_title, font_bold, font_reg, font_small)

    def _draw_modal_base(self, surface, w, h, mw, mh, title, font_title) -> Tuple[int, int, pygame.Rect]:
        mx = (w - mw) // 2
        my = (h - mh) // 2

        # Panel body
        pygame.draw.rect(surface, COLOR_PANEL_BG, (mx, my, mw, mh), border_radius=14)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, (mx, my, mw, mh), 4, border_radius=14)

        # Header banner
        pygame.draw.rect(surface, COLOR_PANEL_HEADER, (mx, my, mw, 54), border_top_left_radius=14, border_top_right_radius=14)
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (mx, my + 54), (mx + mw, my + 54), 3)

        title_surf = font_title.render(title, True, (255, 255, 255))
        surface.blit(title_surf, (mx + 24, my + 14))

        # Close 'X' Button
        close_rect = pygame.Rect(mx + mw - 46, my + 10, 34, 34)
        pygame.draw.circle(surface, COLOR_BTN_RED, close_rect.center, 16)
        x_surf = font_title.render("X", True, (255, 255, 255))
        surface.blit(x_surf, (close_rect.centerx - x_surf.get_width() // 2, close_rect.centery - x_surf.get_height() // 2))

        return mx, my, close_rect

    # -------------------------------------------------------------
    # 1. BUILD CATALOG MODAL
    # -------------------------------------------------------------
    def _render_build_modal(self, surface, sw, sh, font_title, font_bold, font_reg, font_small):
        mw, mh = 860, 540
        mx, my, _ = self._draw_modal_base(surface, sw, sh, mw, mh, "Build Catalog & Shop", font_title)

        # Tabs
        tabs = [
            ('farming', 'Farming'),
            ('houses', 'Houses'),
            ('community', 'Community'),
            ('factories', 'Factories'),
            ('animals', 'Animals'),
            ('decorations', 'Decor'),
            ('roads', 'Roads')
        ]
        tab_w = (mw - 40) // len(tabs)
        for i, (tid, label) in enumerate(tabs):
            tx = mx + 20 + i * tab_w
            ty = my + 64
            is_active = (self.build_tab == tid)
            col = (255, 225, 140) if is_active else (230, 220, 205)
            pygame.draw.rect(surface, col, (tx, ty, tab_w - 4, 34), border_radius=6)
            if is_active:
                pygame.draw.rect(surface, COLOR_PANEL_BORDER, (tx, ty, tab_w - 4, 34), 2, border_radius=6)
            txt = font_bold.render(label, True, COLOR_TEXT_DARK)
            surface.blit(txt, (tx + (tab_w - 4 - txt.get_width()) // 2, ty + 8))

        # Catalog Items Grid
        items = self._get_items_for_tab(self.build_tab)
        grid_y = my + 112
        card_w, card_h = 190, 190
        cols = 4

        for i, it in enumerate(items[:8]):  # show first 8 items
            col = i % cols
            row = i // cols
            cx = mx + 24 + col * (card_w + 14)
            cy = grid_y + row * (card_h + 16)

            pygame.draw.rect(surface, (255, 255, 255), (cx, cy, card_w, card_h), border_radius=10)
            pygame.draw.rect(surface, (215, 205, 190), (cx, cy, card_w, card_h), 2, border_radius=10)

            # Item title
            name_txt = font_bold.render(it['name'], True, COLOR_TEXT_DARK)
            surface.blit(name_txt, (cx + (card_w - name_txt.get_width()) // 2, cy + 8))

            # Preview Image or Icon
            preview_img = self._get_preview_image(it['id'], self.build_tab)
            if preview_img:
                scaled = pygame.transform.smoothscale(preview_img, (64, 64))
                surface.blit(scaled, (cx + (card_w - 64) // 2, cy + 34))

            # Stats (Pop, PopCap, Size)
            stat_str = ""
            if 'pop' in it:
                stat_str = f"+{it['pop']} Pop"
            elif 'pop_cap' in it:
                stat_str = f"+{it['pop_cap']} Pop Cap"
            elif 'size' in it:
                stat_str = f"Size: {it['size'][0]}x{it['size'][1]}"
            if stat_str:
                st_txt = font_small.render(stat_str, True, (60, 120, 180))
                surface.blit(st_txt, (cx + (card_w - st_txt.get_width()) // 2, cy + 104))

            # Cost & Level
            cost_txt = font_bold.render(f"{it.get('cost', 0)} Coins", True, (215, 140, 20))
            surface.blit(cost_txt, (cx + (card_w - cost_txt.get_width()) // 2, cy + 124))

            # Build Button
            btn_rect = pygame.Rect(cx + 14, cy + 148, card_w - 28, 32)
            is_locked = (self.state.level < it.get('min_level', 1))
            can_afford = (self.state.coins >= it.get('cost', 0))

            if is_locked:
                pygame.draw.rect(surface, (180, 180, 180), btn_rect, border_radius=6)
                b_txt = font_small.render(f"Lvl {it.get('min_level')} Req", True, (255, 255, 255))
            elif not can_afford:
                pygame.draw.rect(surface, (220, 140, 140), btn_rect, border_radius=6)
                b_txt = font_small.render("Need Coins", True, (255, 255, 255))
            else:
                pygame.draw.rect(surface, COLOR_BTN_GREEN, btn_rect, border_radius=6)
                b_txt = font_bold.render("Place", True, (255, 255, 255))

            surface.blit(b_txt, (btn_rect.centerx - b_txt.get_width() // 2, btn_rect.centery - b_txt.get_height() // 2))

    def _get_items_for_tab(self, tab: str) -> List[Dict[str, Any]]:
        if tab == 'farming':
            return [{'id': 'field_plot', **SPECIAL_BUILDINGS['field_plot']}]
        elif tab == 'houses':
            return [{'id': k, **v} for k, v in HOUSES.items()]
        elif tab == 'community':
            return [{'id': k, **v} for k, v in COMMUNITY_BUILDINGS.items()]
        elif tab == 'factories':
            return [{'id': k, **v} for k, v in FACTORIES.items()]
        elif tab == 'animals':
            return [{'id': k, **v} for k, v in SHEDS.items()]
        elif tab == 'decorations':
            return [{'id': k, **v} for k, v in DECORATIONS.items()]
        elif tab == 'roads':
            return [{'id': k, **v} for k, v in ROADS.items()]
        return []

    def _get_preview_image(self, item_id: str, tab: str) -> Optional[pygame.Surface]:
        if tab == 'roads':
            return self.sprites.roads.get(item_id)
        elif tab == 'decorations':
            return self.sprites.decorations.get(item_id)
        elif item_id == 'field_plot':
            return self.sprites.roads.get('field_plot')
        return self.sprites.buildings.get(item_id)

    # -------------------------------------------------------------
    # 2. HELICOPTER ORDER BOARD MODAL
    # -------------------------------------------------------------
    def _render_orders_modal(self, surface, sw, sh, font_title, font_bold, font_reg, font_small):
        mw, mh = 920, 580
        mx, my, _ = self._draw_modal_base(surface, sw, sh, mw, mh, "Town Helicopter Order Board", font_title)

        card_w, card_h = 270, 230
        cols = 3

        for i, ord_data in enumerate(self.state.orders):
            col = i % cols
            row = i // cols
            cx = mx + 25 + col * (card_w + 20)
            cy = my + 72 + row * (card_h + 20)

            pygame.draw.rect(surface, (255, 255, 255), (cx, cy, card_w, card_h), border_radius=12)
            pygame.draw.rect(surface, (215, 205, 190), (cx, cy, card_w, card_h), 2, border_radius=12)

            cooldown = ord_data.get('cooldown', 0.0)
            if cooldown > 0:
                # Cooldown display
                cd_txt = font_bold.render(f"New Order in {int(cooldown)}s", True, COLOR_TEXT_MUTED)
                surface.blit(cd_txt, (cx + (card_w - cd_txt.get_width()) // 2, cy + 100))
                continue

            # Character Portrait & Info
            port = self.sprites.characters.get(ord_data['character'])
            if port:
                surface.blit(port, (cx + 10, cy + 10))

            char_name = font_bold.render(ord_data['name'], True, COLOR_TEXT_DARK)
            role_txt = font_small.render(ord_data['role'], True, (70, 140, 210))
            surface.blit(char_name, (cx + 82, cy + 16))
            surface.blit(role_txt, (cx + 82, cy + 38))

            # Trash button (small X)
            trash_rect = pygame.Rect(cx + card_w - 30, cy + 10, 20, 20)
            pygame.draw.circle(surface, (220, 220, 220), trash_rect.center, 10)
            x_txt = font_small.render("x", True, (120, 120, 120))
            surface.blit(x_txt, (trash_rect.centerx - x_txt.get_width() // 2, trash_rect.centery - x_txt.get_height() // 2 - 2))

            # Demands checklist
            dy = cy + 78
            all_ready = True
            for item_k, qty in ord_data['demands'].items():
                in_stock = self.state.inventory.get(item_k, 0)
                ready = in_stock >= qty
                if not ready:
                    all_ready = False

                icon = self.sprites.icons.get(item_k)
                if icon:
                    sc = pygame.transform.smoothscale(icon, (24, 24))
                    surface.blit(sc, (cx + 14, dy))

                item_label = f"{ALL_ITEMS.get(item_k, {}).get('name', item_k)}: {in_stock}/{qty}"
                col_txt = (60, 150, 60) if ready else (210, 65, 65)
                lbl = font_small.render(item_label, True, col_txt)
                surface.blit(lbl, (cx + 44, dy + 4))
                dy += 26

            # Rewards
            rew_txt = font_small.render(f"+{ord_data['coins']} Coins  +{ord_data['xp']} XP", True, (220, 145, 20))
            surface.blit(rew_txt, (cx + 14, cy + card_h - 48))

            # Send Button
            btn_rect = pygame.Rect(cx + 14, cy + card_h - 42, card_w - 28, 32)
            if all_ready and self.state.helicopter_state == 'idle':
                pygame.draw.rect(surface, COLOR_BTN_ORANGE, btn_rect, border_radius=6)
                send_lbl = font_bold.render("Send Helicopter", True, (255, 255, 255))
            else:
                pygame.draw.rect(surface, (200, 200, 200), btn_rect, border_radius=6)
                send_lbl = font_small.render("Incomplete" if not all_ready else "Helicopter Busy", True, (255, 255, 255))

            surface.blit(send_lbl, (btn_rect.centerx - send_lbl.get_width() // 2, btn_rect.centery - send_lbl.get_height() // 2))

    # -------------------------------------------------------------
    # 3. BARN MODAL
    # -------------------------------------------------------------
    def _render_barn_modal(self, surface, sw, sh, font_title, font_bold, font_reg, font_small):
        mw, mh = 840, 560
        mx, my, _ = self._draw_modal_base(surface, sw, sh, mw, mh, "Town Barn & Storage", font_title)

        # Capacity Banner
        cap_txt = font_bold.render(f"Barn Storage: {self.state.get_barn_count()} / {self.state.barn_capacity} Items", True, (180, 55, 45))
        surface.blit(cap_txt, (mx + 28, my + 68))

        # Upgrade Section (Right of banner)
        reqs = self.state.get_barn_upgrade_requirements()
        can_up = self.state.can_upgrade_barn()
        up_btn_rect = pygame.Rect(mx + mw - 220, my + 64, 190, 36)
        pygame.draw.rect(surface, COLOR_BTN_GREEN if can_up else (190, 190, 190), up_btn_rect, border_radius=8)
        up_txt = font_bold.render("+30 Capacity Upgrade", True, (255, 255, 255))
        surface.blit(up_txt, (up_btn_rect.centerx - up_txt.get_width() // 2, up_btn_rect.centery - up_txt.get_height() // 2))

        # Tools requirement icons under upgrade button
        tx = mx + mw - 220
        for tool in ['nail', 'paint', 'hammer']:
            have = self.state.inventory.get(tool, 0)
            needed = reqs[tool]
            t_icon = self.sprites.icons.get(tool)
            if t_icon:
                sc = pygame.transform.smoothscale(t_icon, (20, 20))
                surface.blit(sc, (tx, my + 106))
            t_txt = font_small.render(f"{have}/{needed}", True, (50, 140, 50) if have >= needed else (200, 60, 60))
            surface.blit(t_txt, (tx + 24, my + 108))
            tx += 64

        # Inventory Grid
        grid_y = my + 140
        card_w, card_h = 145, 120
        cols = 5

        items_list = list(self.state.inventory.items())
        if not items_list:
            empty_txt = font_bold.render("Your Barn is empty! Harvest crops or produce goods.", True, COLOR_TEXT_MUTED)
            surface.blit(empty_txt, (mx + (mw - empty_txt.get_width()) // 2, my + 260))

        for i, (item_k, qty) in enumerate(items_list[:15]):
            col = i % cols
            row = i // cols
            cx = mx + 24 + col * (card_w + 14)
            cy = grid_y + row * (card_h + 14)

            pygame.draw.rect(surface, (255, 255, 255), (cx, cy, card_w, card_h), border_radius=8)
            pygame.draw.rect(surface, (215, 205, 190), (cx, cy, card_w, card_h), 2, border_radius=8)

            # Icon & Count
            icon = self.sprites.icons.get(item_k)
            if icon:
                surface.blit(icon, (cx + 10, cy + 10))

            qty_txt = font_bold.render(f"x{qty}", True, COLOR_TEXT_DARK)
            surface.blit(qty_txt, (cx + 50, cy + 16))

            item_name = font_small.render(ALL_ITEMS.get(item_k, {}).get('name', item_k)[:14], True, COLOR_TEXT_MUTED)
            surface.blit(item_name, (cx + 10, cy + 46))

            # Sell 1x button
            sell_price = ALL_ITEMS.get(item_k, {}).get('sell', 1)
            sell_btn = pygame.Rect(cx + 8, cy + 78, card_w - 16, 30)
            pygame.draw.rect(surface, (245, 195, 45), sell_btn, border_radius=6)
            s_txt = font_small.render(f"Sell 1x (+{sell_price})", True, (65, 45, 25))
            surface.blit(s_txt, (sell_btn.centerx - s_txt.get_width() // 2, sell_btn.centery - s_txt.get_height() // 2))

    # -------------------------------------------------------------
    # 4. FACTORY & SHED MODAL
    # -------------------------------------------------------------
    def _render_factory_modal(self, surface, sw, sh, font_title, font_bold, font_reg, font_small):
        if not self.selected_building:
            return

        b = self.selected_building
        cat = b.get('category')
        mw, mh = 780, 480
        b_name = FACTORIES.get(b['type'], {}).get('name') or SHEDS.get(b['type'], {}).get('name', 'Building')
        mx, my, _ = self._draw_modal_base(surface, sw, sh, mw, mh, f"{b_name} Production", font_title)

        if cat == 'shed':
            self._render_shed_details(surface, mx, my, mw, mh, b, font_bold, font_reg, font_small)
        elif cat == 'factory':
            self._render_factory_details(surface, mx, my, mw, mh, b, font_bold, font_reg, font_small)

    def _render_shed_details(self, surface, mx, my, mw, mh, shed, font_bold, font_reg, font_small):
        shed_info = SHEDS[shed['type']]
        feed_type = shed_info['feed_type']
        have_feed = self.state.inventory.get(feed_type, 0)

        # Status
        status_txt = "Ready to Feed!"
        if shed.get('ready_count', 0) > 0:
            status_txt = f"{shed['ready_count']}x {shed_info['product_name']} Ready to Collect!"
        elif shed.get('fed', False):
            elapsed = time.time() - shed.get('feed_time', 0.0)
            rem = max(0, int(shed.get('duration', 10.0) - elapsed))
            status_txt = f"Eating & Producing... {rem}s remaining"

        st_surf = font_bold.render(f"Status: {status_txt}", True, (60, 140, 220))
        surface.blit(st_surf, (mx + 30, my + 80))

        # Big Shed Preview
        preview = self.sprites.buildings.get(shed['type'])
        if preview:
            surface.blit(preview, (mx + 30, my + 130))

        # Actions Panel (Right side)
        ax = mx + 280
        ay = my + 130

        # Feed Info
        feed_info = font_reg.render(f"Requires: 1x {feed_type.replace('_', ' ').title()} (You have: {have_feed})", True, COLOR_TEXT_DARK)
        surface.blit(feed_info, (ax, ay))

        feed_btn = pygame.Rect(ax, ay + 40, 220, 44)
        can_feed = (have_feed >= 1 and not shed.get('fed', False) and shed.get('ready_count', 0) == 0)
        pygame.draw.rect(surface, COLOR_BTN_GREEN if can_feed else (190, 190, 190), feed_btn, border_radius=8)
        fb_txt = font_bold.render("Feed Animals", True, (255, 255, 255))
        surface.blit(fb_txt, (feed_btn.centerx - fb_txt.get_width() // 2, feed_btn.centery - fb_txt.get_height() // 2))

        # Speedup Button
        if shed.get('fed', False):
            spd_btn = pygame.Rect(ax, ay + 100, 220, 40)
            pygame.draw.rect(surface, COLOR_TCASH, spd_btn, border_radius=8)
            spd_txt = font_bold.render("Speed Up (1 T$)", True, (255, 255, 255))
            surface.blit(spd_txt, (spd_btn.centerx - spd_txt.get_width() // 2, spd_btn.centery - spd_txt.get_height() // 2))

        # Collect Button
        if shed.get('ready_count', 0) > 0:
            col_btn = pygame.Rect(ax, ay + 100, 220, 44)
            pygame.draw.rect(surface, COLOR_BTN_ORANGE, col_btn, border_radius=8)
            col_txt = font_bold.render("Collect Goods", True, (255, 255, 255))
            surface.blit(col_txt, (col_btn.centerx - col_txt.get_width() // 2, col_btn.centery - col_txt.get_height() // 2))

    def _render_factory_details(self, surface, mx, my, mw, mh, factory, font_bold, font_reg, font_small):
        f_info = FACTORIES[factory['type']]
        queue = factory.get('queue', [])
        completed = factory.get('completed', [])

        # Queue Status Banner
        qy = my + 72
        q_lbl = font_bold.render(f"Production Queue: {len(queue)} / {factory.get('max_queue', 3)} Slots", True, COLOR_TEXT_DARK)
        surface.blit(q_lbl, (mx + 30, qy))

        # Draw Queue slots
        for s in range(3):
            sx = mx + 30 + s * 140
            sy = qy + 32
            pygame.draw.rect(surface, (255, 255, 255), (sx, sy, 130, 60), border_radius=8)
            pygame.draw.rect(surface, (215, 205, 190), (sx, sy, 130, 60), 2, border_radius=8)

            if s < len(queue):
                item_q = queue[s]
                icon = self.sprites.icons.get(item_q['recipe'])
                if icon:
                    surface.blit(icon, (sx + 8, sy + 14))
                rem_txt = font_small.render(f"{int(item_q['remaining'])}s", True, (210, 110, 30))
                surface.blit(rem_txt, (sx + 50, sy + 22))

        # Speed Up & Collect Buttons
        if queue:
            spd_btn = pygame.Rect(mx + 480, qy + 40, 130, 44)
            pygame.draw.rect(surface, COLOR_TCASH, spd_btn, border_radius=8)
            s_txt = font_bold.render("Finish (1 T$)", True, (255, 255, 255))
            surface.blit(s_txt, (spd_btn.centerx - s_txt.get_width() // 2, spd_btn.centery - s_txt.get_height() // 2))

        if completed:
            col_btn = pygame.Rect(mx + 620, qy + 40, 130, 44)
            pygame.draw.rect(surface, COLOR_BTN_GREEN, col_btn, border_radius=8)
            c_txt = font_bold.render(f"Collect ({len(completed)})", True, (255, 255, 255))
            surface.blit(c_txt, (col_btn.centerx - c_txt.get_width() // 2, col_btn.centery - c_txt.get_height() // 2))

        # Available Recipes Grid
        ry = my + 195
        r_title = font_bold.render("Available Recipes:", True, COLOR_TEXT_DARK)
        surface.blit(r_title, (mx + 30, ry))

        recipes_list = f_info.get('recipes', [])
        for i, rec_key in enumerate(recipes_list):
            rec = ALL_RECIPES[rec_key]
            rx = mx + 30 + i * 235
            ry_box = ry + 30

            pygame.draw.rect(surface, (255, 255, 255), (rx, ry_box, 220, 200), border_radius=10)
            pygame.draw.rect(surface, (215, 205, 190), (rx, ry_box, 220, 200), 2, border_radius=10)

            # Icon & Name
            icon = self.sprites.icons.get(rec_key)
            if icon:
                surface.blit(icon, (rx + 14, ry_box + 12))
            r_name = font_bold.render(rec['name'], True, COLOR_TEXT_DARK)
            surface.blit(r_name, (rx + 54, ry_box + 16))

            # Ingredients list
            iy = ry_box + 56
            has_all = True
            for ing_k, req_qty in rec['ingredients'].items():
                have_qty = self.state.inventory.get(ing_k, 0)
                if have_qty < req_qty:
                    has_all = False
                ing_icon = self.sprites.icons.get(ing_k)
                if ing_icon:
                    sc = pygame.transform.smoothscale(ing_icon, (20, 20))
                    surface.blit(sc, (rx + 14, iy))
                ing_txt = font_small.render(f"{have_qty}/{req_qty} {ing_k.replace('_', ' ').title()}", True, (50, 150, 50) if have_qty >= req_qty else (210, 60, 60))
                surface.blit(ing_txt, (rx + 40, iy + 2))
                iy += 24

            time_txt = font_small.render(f"Time: {int(rec['prod_time'])}s  |  +{rec['xp']} XP", True, COLOR_TEXT_MUTED)
            surface.blit(time_txt, (rx + 14, ry_box + 124))

            # Produce Button
            btn_rect = pygame.Rect(rx + 14, ry_box + 148, 192, 36)
            is_locked = (self.state.level < rec['min_level'])

            if is_locked:
                pygame.draw.rect(surface, (190, 190, 190), btn_rect, border_radius=6)
                p_txt = font_small.render(f"Lvl {rec['min_level']} Req", True, (255, 255, 255))
            elif not has_all:
                pygame.draw.rect(surface, (220, 160, 160), btn_rect, border_radius=6)
                p_txt = font_small.render("Missing Items", True, (255, 255, 255))
            else:
                pygame.draw.rect(surface, COLOR_BTN_BLUE, btn_rect, border_radius=6)
                p_txt = font_bold.render("Produce", True, (255, 255, 255))

            surface.blit(p_txt, (btn_rect.centerx - p_txt.get_width() // 2, btn_rect.centery - p_txt.get_height() // 2))

    # -------------------------------------------------------------
    # 5. DAILY BONUS MODAL
    # -------------------------------------------------------------
    def _render_daily_modal(self, surface, sw, sh, font_title, font_bold, font_reg, font_small):
        mw, mh = 780, 420
        mx, my, _ = self._draw_modal_base(surface, sw, sh, mw, mh, "Daily Login Streak Bonus", font_title)

        info_txt = font_reg.render("Log in every day to claim progressively higher coins, T-Cash, and tools!", True, COLOR_TEXT_DARK)
        surface.blit(info_txt, (mx + (mw - info_txt.get_width()) // 2, my + 72))

        # 7 Day Cards
        card_w = 94
        start_x = mx + 30
        for i, d in enumerate(DAILY_REWARDS):
            cx = start_x + i * (card_w + 10)
            cy = my + 120
            is_today = (d['day'] == self.state.daily_streak)
            bg_col = (255, 235, 160) if is_today else (255, 255, 255)

            pygame.draw.rect(surface, bg_col, (cx, cy, card_w, 180), border_radius=10)
            pygame.draw.rect(surface, COLOR_PANEL_HEADER if is_today else (215, 205, 190), (cx, cy, card_w, 180), 2, border_radius=10)

            day_lbl = font_bold.render(f"Day {d['day']}", True, COLOR_TEXT_DARK)
            surface.blit(day_lbl, (cx + (card_w - day_lbl.get_width()) // 2, cy + 12))

            # Coins reward
            coin_icon = self.sprites.icons.get('coin')
            if coin_icon:
                sc = pygame.transform.smoothscale(coin_icon, (24, 24))
                surface.blit(sc, (cx + 10, cy + 50))
            c_txt = font_small.render(f"+{d['coins']}", True, (215, 140, 20))
            surface.blit(c_txt, (cx + 38, cy + 54))

            # T-Cash reward
            tcash_icon = self.sprites.icons.get('tcash')
            if tcash_icon:
                sc = pygame.transform.smoothscale(tcash_icon, (24, 18))
                surface.blit(sc, (cx + 10, cy + 86))
            tc_txt = font_small.render(f"+{d['tcash']} T$", True, COLOR_TCASH)
            surface.blit(tc_txt, (cx + 38, cy + 88))

            # Tool reward
            if d['tool']:
                tool_icon = self.sprites.icons.get(d['tool'])
                if tool_icon:
                    sc = pygame.transform.smoothscale(tool_icon, (22, 22))
                    surface.blit(sc, (cx + 10, cy + 120))
                tl_txt = font_small.render(f"+1 Tool", True, (60, 140, 220))
                surface.blit(tl_txt, (cx + 36, cy + 124))

        # Claim Button
        claim_btn = pygame.Rect(mx + (mw - 240) // 2, my + 330, 240, 50)
        can_claim = self.state.can_claim_daily
        pygame.draw.rect(surface, COLOR_BTN_GREEN if can_claim else (190, 190, 190), claim_btn, border_radius=10)
        btn_label = "Claim Today's Bonus!" if can_claim else "Already Claimed Today"
        cb_txt = font_bold.render(btn_label, True, (255, 255, 255))
        surface.blit(cb_txt, (claim_btn.centerx - cb_txt.get_width() // 2, claim_btn.centery - cb_txt.get_height() // 2))

    # -------------------------------------------------------------
    # 6. ERNIE'S QUESTS MODAL
    # -------------------------------------------------------------
    def _render_quests_modal(self, surface, sw, sh, font_title, font_bold, font_reg, font_small):
        mw, mh = 700, 440
        mx, my, _ = self._draw_modal_base(surface, sw, sh, mw, mh, "Ernie's Town Tasks & Quests", font_title)

        # Ernie Portrait & Speech Bubble
        ernie_port = self.sprites.characters.get('ernie')
        if ernie_port:
            scaled = pygame.transform.smoothscale(ernie_port, (84, 84))
            surface.blit(scaled, (mx + 30, my + 80))

        bubble_rect = pygame.Rect(mx + 130, my + 80, mw - 160, 84)
        pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=12)
        pygame.draw.rect(surface, (215, 205, 190), bubble_rect, 2, border_radius=12)

        speech = font_reg.render("Greetings, Mayor! Complete town tasks to grow our community!", True, COLOR_TEXT_DARK)
        surface.blit(speech, (bubble_rect.x + 16, bubble_rect.y + 16))

        # Current Quest Card
        if self.state.current_quest_idx < len(self.state.quests):
            q = self.state.quests[self.state.current_quest_idx]
            qy = my + 190

            pygame.draw.rect(surface, (255, 255, 255), (mx + 30, qy, mw - 60, 200), border_radius=12)
            pygame.draw.rect(surface, (215, 205, 190), (mx + 30, qy, mw - 60, 200), 2, border_radius=12)

            q_title = font_bold.render(f"Task: {q['title']}", True, (215, 130, 30))
            surface.blit(q_title, (mx + 50, qy + 16))

            q_desc = font_reg.render(q['desc'], True, COLOR_TEXT_DARK)
            surface.blit(q_desc, (mx + 50, qy + 46))

            # Progress Bar
            prog = min(1.0, q['progress'] / max(1, q['target']))
            bar_w = mw - 160
            pygame.draw.rect(surface, (225, 220, 210), (mx + 50, qy + 86, bar_w, 20), border_radius=10)
            if prog > 0:
                pygame.draw.rect(surface, (95, 195, 60), (mx + 50, qy + 86, int(bar_w * prog), 20), border_radius=10)
            p_txt = font_small.render(f"{q['progress']} / {q['target']}", True, COLOR_TEXT_DARK)
            surface.blit(p_txt, (mx + 50 + (bar_w - p_txt.get_width()) // 2, qy + 88))

            # Rewards
            r_txt = font_bold.render(f"Rewards: +{q['reward_coins']} Coins  |  +{q['reward_xp']} XP  |  +{q['reward_tcash']} T$", True, (60, 140, 210))
            surface.blit(r_txt, (mx + 50, qy + 135))
        else:
            all_done = font_bold.render("All current tasks completed! Great work, Mayor!", True, (65, 175, 65))
            surface.blit(all_done, (mx + (mw - all_done.get_width()) // 2, my + 260))

    # -------------------------------------------------------------
    # CLICK HANDLING
    # -------------------------------------------------------------
    def handle_click(self, mx: int, my: int, sw: int, sh: int, farming_sys, livestock_sys, mfg_sys, build_sys) -> bool:
        if not self.active_modal:
            return False

        # Generic modal dimensions check
        mw, mh = 860, 540
        if self.active_modal == 'orders':
            mw, mh = 920, 580
        elif self.active_modal == 'barn':
            mw, mh = 840, 560
        elif self.active_modal in ['factory', 'daily']:
            mw, mh = 780, 480
        elif self.active_modal == 'quests':
            mw, mh = 700, 440

        panel_x = (sw - mw) // 2
        panel_y = (sh - mh) // 2

        # Close 'X' Button
        close_rect = pygame.Rect(panel_x + mw - 46, panel_y + 10, 34, 34)
        if close_rect.collidepoint(mx, my):
            self.close_modal()
            return True

        # Click outside closes
        if not pygame.Rect(panel_x, panel_y, mw, mh).collidepoint(mx, my):
            self.close_modal()
            return True

        # 1. Build Modal Clicks
        if self.active_modal == 'build':
            # Tab clicks
            tabs = ['farming', 'houses', 'community', 'factories', 'animals', 'decorations', 'roads']
            tab_w = (mw - 40) // len(tabs)
            for i, tid in enumerate(tabs):
                tx = panel_x + 20 + i * tab_w
                ty = panel_y + 64
                if pygame.Rect(tx, ty, tab_w - 4, 34).collidepoint(mx, my):
                    self.build_tab = tid
                    get_sound_manager().play('click')
                    return True

            # Items grid clicks
            items = self._get_items_for_tab(self.build_tab)
            grid_y = panel_y + 112
            card_w, card_h = 190, 190
            cols = 4

            for i, it in enumerate(items[:8]):
                col = i % cols
                row = i // cols
                cx = panel_x + 24 + col * (card_w + 14)
                cy = grid_y + row * (card_h + 16)
                btn_rect = pygame.Rect(cx + 14, cy + 148, card_w - 28, 32)

                if btn_rect.collidepoint(mx, my):
                    # Enter placement mode!
                    category = self._tab_to_category(self.build_tab)
                    self.placement_item = (it['id'], category)
                    self.close_modal()
                    self.state.add_toast(f"Click on the map to place {it['name']}!", color=(110, 220, 245))
                    return True

        # 2. Orders Modal Clicks
        elif self.active_modal == 'orders':
            card_w, card_h = 270, 230
            cols = 3
            for i, ord_data in enumerate(self.state.orders):
                col = i % cols
                row = i // cols
                cx = panel_x + 25 + col * (card_w + 20)
                cy = panel_y + 72 + row * (card_h + 20)

                # Trash click
                trash_rect = pygame.Rect(cx + card_w - 30, cy + 10, 20, 20)
                if trash_rect.collidepoint(mx, my):
                    self.state.trash_order(ord_data['id'])
                    return True

                # Send button click
                btn_rect = pygame.Rect(cx + 14, cy + card_h - 42, card_w - 28, 32)
                if btn_rect.collidepoint(mx, my):
                    self.state.dispatch_helicopter(ord_data['id'])
                    return True

        # 3. Barn Modal Clicks
        elif self.active_modal == 'barn':
            # Upgrade button
            up_btn_rect = pygame.Rect(panel_x + mw - 220, panel_y + 64, 190, 36)
            if up_btn_rect.collidepoint(mx, my):
                self.state.upgrade_barn()
                return True

            # Sell buttons
            grid_y = panel_y + 140
            card_w, card_h = 145, 120
            cols = 5
            items_list = list(self.state.inventory.items())
            for i, (item_k, qty) in enumerate(items_list[:15]):
                col = i % cols
                row = i // cols
                cx = panel_x + 24 + col * (card_w + 14)
                cy = grid_y + row * (card_h + 14)
                sell_btn = pygame.Rect(cx + 8, cy + 78, card_w - 16, 30)
                if sell_btn.collidepoint(mx, my):
                    self.state.sell_item(item_k, 1)
                    return True

        # 4. Factory / Shed Modal Clicks
        elif self.active_modal == 'factory' and self.selected_building:
            b = self.selected_building
            cat = b.get('category')
            if cat == 'shed':
                ax = panel_x + 280
                ay = panel_y + 130
                feed_btn = pygame.Rect(ax, ay + 40, 220, 44)
                if feed_btn.collidepoint(mx, my):
                    livestock_sys.feed_shed(b)
                    return True

                if b.get('fed', False):
                    spd_btn = pygame.Rect(ax, ay + 100, 220, 40)
                    if spd_btn.collidepoint(mx, my):
                        livestock_sys.speedup_shed(b)
                        return True

                if b.get('ready_count', 0) > 0:
                    col_btn = pygame.Rect(ax, ay + 100, 220, 44)
                    if col_btn.collidepoint(mx, my):
                        livestock_sys.collect_products(b)
                        return True

            elif cat == 'factory':
                qy = panel_y + 72
                if b.get('queue'):
                    spd_btn = pygame.Rect(panel_x + 480, qy + 40, 130, 44)
                    if spd_btn.collidepoint(mx, my):
                        mfg_sys.speedup_production(b)
                        return True

                if b.get('completed'):
                    col_btn = pygame.Rect(panel_x + 620, qy + 40, 130, 44)
                    if col_btn.collidepoint(mx, my):
                        mfg_sys.collect_finished(b)
                        return True

                # Recipe buttons
                ry = panel_y + 195
                f_info = FACTORIES[b['type']]
                for i, rec_key in enumerate(f_info.get('recipes', [])):
                    rx = panel_x + 30 + i * 235
                    ry_box = ry + 30
                    btn_rect = pygame.Rect(rx + 14, ry_box + 148, 192, 36)
                    if btn_rect.collidepoint(mx, my):
                        mfg_sys.start_production(b, rec_key)
                        return True

        # 5. Daily Modal Clicks
        elif self.active_modal == 'daily':
            claim_btn = pygame.Rect(panel_x + (mw - 240) // 2, panel_y + 330, 240, 50)
            if claim_btn.collidepoint(mx, my) and self.state.can_claim_daily:
                reward = DAILY_REWARDS[self.state.daily_streak - 1]
                self.state.add_coins(reward['coins'])
                self.state.add_tcash(reward['tcash'])
                if reward['tool'] and self.state.can_add_to_barn(1):
                    self.state.add_to_barn(reward['tool'], 1)

                self.state.can_claim_daily = False
                self.state.daily_streak = (self.state.daily_streak % 7) + 1
                self.state.add_toast(f"Claimed Daily Bonus! +{reward['coins']} Coins, +{reward['tcash']} T$!", color=(110, 235, 110))
                get_sound_manager().play('level_up')
                return True

        return True

    def _tab_to_category(self, tab: str) -> str:
        if tab == 'farming':
            return 'crop'
        elif tab == 'houses':
            return 'house'
        elif tab == 'community':
            return 'community'
        elif tab == 'factories':
            return 'factory'
        elif tab == 'animals':
            return 'shed'
        elif tab == 'decorations':
            return 'decoration'
        elif tab == 'roads':
            return 'road'
        return 'house'
