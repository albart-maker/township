"""
Township - Match-3 Adventure Event Mini-Game
Township's iconic puzzle event! Players swap colorful crops/gems to match
lines of 3 or more, complete level goals under a move limit, and win Coins,
T-Cash, XP, and Barn upgrade materials for their main town!
"""

import random
import pygame
from typing import Dict, List, Tuple, Optional, Any
from sound_manager import get_sound_manager

BOARD_ROWS = 8
BOARD_COLS = 8
CELL_SIZE = 58
GEM_TYPES = ['apple', 'carrot', 'sun', 'leaf', 'drop', 'berry']

class Match3Game:
    def __init__(self, state, sprite_manager):
        self.state = state
        self.sprites = sprite_manager
        self.board: List[List[str]] = []
        self.selected_gem: Optional[Tuple[int, int]] = None
        self.score: int = 0
        self.moves_left: int = 22
        self.level: int = 1

        # Level Goals: e.g., collect specific gems
        self.goals = {
            'apple': 12,
            'carrot': 10
        }
        self.collected = {
            'apple': 0,
            'carrot': 0
        }

        self.game_over: bool = False
        self.victory: bool = False
        self.claimed_rewards: bool = False

        self._init_board()

    def _init_board(self):
        self.board = [[random.choice(GEM_TYPES) for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        # Ensure no matches at start
        while self._find_matches():
            for r in range(BOARD_ROWS):
                for c in range(BOARD_COLS):
                    self.board[r][c] = random.choice(GEM_TYPES)

    def restart_level(self):
        self.score = 0
        self.moves_left = 22
        self.goals = {
            'apple': 10 + self.level * 2,
            'carrot': 8 + self.level * 2
        }
        self.collected = {'apple': 0, 'carrot': 0}
        self.game_over = False
        self.victory = False
        self.claimed_rewards = False
        self.selected_gem = None
        self._init_board()

    def _find_matches(self) -> set[Tuple[int, int]]:
        matched = set()

        # Horizontal matches
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS - 2):
                g = self.board[r][c]
                if g and g == self.board[r][c + 1] == self.board[r][c + 2]:
                    matched.add((r, c))
                    matched.add((r, c + 1))
                    matched.add((r, c + 2))
                    # check longer chains
                    k = c + 3
                    while k < BOARD_COLS and self.board[r][k] == g:
                        matched.add((r, k))
                        k += 1

        # Vertical matches
        for c in range(BOARD_COLS):
            for r in range(BOARD_ROWS - 2):
                g = self.board[r][c]
                if g and g == self.board[r + 1][c] == self.board[r + 2][c]:
                    matched.add((r, c))
                    matched.add((r + 1, c))
                    matched.add((r + 2, c))
                    k = r + 3
                    while k < BOARD_ROWS and self.board[k][c] == g:
                        matched.add((k, c))
                        k += 1

        return matched

    def handle_cell_click(self, r: int, c: int) -> bool:
        if self.game_over or self.victory:
            return False

        if not (0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS):
            return False

        if self.selected_gem is None:
            self.selected_gem = (r, c)
            get_sound_manager().play('click')
            return True

        sr, sc = self.selected_gem
        # If clicked same cell, deselect
        if sr == r and sc == c:
            self.selected_gem = None
            return True

        # Check adjacency
        if abs(sr - r) + abs(sc - c) == 1:
            # Try swap
            self.board[sr][sc], self.board[r][c] = self.board[r][c], self.board[sr][sc]
            matches = self._find_matches()

            if matches:
                # Valid move!
                self.moves_left -= 1
                self.selected_gem = None
                self._resolve_matches(matches, combo=1)
                self._check_end_condition()
                return True
            else:
                # Invalid swap, swap back
                self.board[sr][sc], self.board[r][c] = self.board[r][c], self.board[sr][sc]
                get_sound_manager().play('error')
                self.selected_gem = (r, c)
                return False
        else:
            # Select new gem
            self.selected_gem = (r, c)
            get_sound_manager().play('click')
            return True

    def _resolve_matches(self, matches: set[Tuple[int, int]], combo: int = 1):
        if not matches:
            return

        # Track collection for goals
        for r, c in matches:
            gem = self.board[r][c]
            if gem in self.collected:
                self.collected[gem] += 1
            self.board[r][c] = None

        self.score += len(matches) * 10 * combo
        if combo > 1:
            get_sound_manager().play('combo')
        else:
            get_sound_manager().play('match')

        # Drop gravity
        for c in range(BOARD_COLS):
            empty_row = BOARD_ROWS - 1
            for r in range(BOARD_ROWS - 1, -1, -1):
                if self.board[r][c] is not None:
                    if r != empty_row:
                        self.board[empty_row][c] = self.board[r][c]
                        self.board[r][c] = None
                    empty_row -= 1

            # Fill top with new gems
            for r in range(empty_row, -1, -1):
                self.board[r][c] = random.choice(GEM_TYPES)

        # Check for cascading matches
        cascading = self._find_matches()
        if cascading:
            self._resolve_matches(cascading, combo + 1)

    def _check_end_condition(self):
        # Check victory
        all_goals_met = True
        for g_type, target in self.goals.items():
            if self.collected.get(g_type, 0) < target:
                all_goals_met = False
                break

        if all_goals_met:
            self.victory = True
            self.game_over = True
            if not self.claimed_rewards:
                self._grant_rewards()
        elif self.moves_left <= 0:
            self.game_over = True
            self.victory = False

    def _grant_rewards(self):
        self.claimed_rewards = True
        coins = 200 + self.level * 50
        xp = 40 + self.level * 10
        tcash = 2
        tool = random.choice(['nail', 'paint', 'hammer'])

        self.state.add_coins(coins)
        self.state.add_xp(xp)
        self.state.add_tcash(tcash)
        if self.state.can_add_to_barn(1):
            self.state.add_to_barn(tool, 1)

        self.state.add_toast(f"Match-3 Victory! +{coins} Coins, +{tcash} T$, +1 {tool.capitalize()}!", color=(255, 225, 60))
        self.state.advance_quest('play_match3', 1)
        get_sound_manager().play('level_up')

    # -------------------------------------------------------------
    # RENDERING
    # -------------------------------------------------------------
    def render(self, surface: pygame.Surface, font_title, font_body):
        w, h = surface.get_size()

        # Darkened overlay background
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((25, 30, 45, 230))
        surface.blit(overlay, (0, 0))

        # Center Board Panel
        board_w = BOARD_COLS * CELL_SIZE + 24
        board_h = BOARD_ROWS * CELL_SIZE + 24
        bx = (w - board_w) // 2
        by = (h - board_h) // 2 + 30

        # Header Title
        title_txt = font_title.render("Adventure Event: Color Harvest", True, (255, 220, 80))
        surface.blit(title_txt, (w // 2 - title_txt.get_width() // 2, 28))

        # Top Info Bar (Goals, Moves, Score)
        bar_y = 75
        moves_txt = font_body.render(f"Moves: {self.moves_left}", True, (255, 255, 255))
        surface.blit(moves_txt, (bx + 10, bar_y))

        score_txt = font_body.render(f"Score: {self.score}", True, (245, 205, 50))
        surface.blit(score_txt, (bx + 180, bar_y))

        # Goals display
        gx_off = bx + 340
        goals_lbl = font_body.render("Goal:", True, (220, 220, 220))
        surface.blit(goals_lbl, (gx_off, bar_y))
        gx_off += 50

        for g_type, target in self.goals.items():
            curr = min(target, self.collected.get(g_type, 0))
            gem_surf = self.sprites.match3_gems.get(g_type)
            if gem_surf:
                scaled_gem = pygame.transform.smoothscale(gem_surf, (26, 26))
                surface.blit(scaled_gem, (gx_off, bar_y - 2))
            gx_off += 30
            txt = font_body.render(f"{curr}/{target}", True, (110, 235, 110) if curr >= target else (255, 255, 255))
            surface.blit(txt, (gx_off, bar_y))
            gx_off += 65

        # Board container
        pygame.draw.rect(surface, (45, 52, 70), (bx, by, board_w, board_h), border_radius=12)
        pygame.draw.rect(surface, (80, 92, 120), (bx, by, board_w, board_h), 3, border_radius=12)

        # Draw Cells & Gems
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                cx = bx + 12 + c * CELL_SIZE
                cy = by + 12 + r * CELL_SIZE

                # Cell tile
                cell_bg = (55, 62, 85) if (r + c) % 2 == 0 else (62, 70, 95)
                pygame.draw.rect(surface, cell_bg, (cx + 2, cy + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=8)

                # Highlight selected
                if self.selected_gem == (r, c):
                    pygame.draw.rect(surface, (255, 230, 80), (cx, cy, CELL_SIZE, CELL_SIZE), 3, border_radius=8)

                gem = self.board[r][c]
                if gem:
                    gem_img = self.sprites.match3_gems.get(gem)
                    if gem_img:
                        surface.blit(gem_img, (cx + (CELL_SIZE - 48) // 2, cy + (CELL_SIZE - 48) // 2))

        # Close / Back button (Top Right)
        close_rect = pygame.Rect(w - 140, 24, 110, 40)
        pygame.draw.rect(surface, (215, 65, 60), close_rect, border_radius=6)
        close_txt = font_body.render("Exit Event", True, (255, 255, 255))
        surface.blit(close_txt, (close_rect.centerx - close_txt.get_width() // 2, close_rect.centery - close_txt.get_height() // 2))

        # Victory or Game Over Modals
        if self.victory:
            self._render_end_dialog(surface, font_title, font_body, w, h, is_win=True)
        elif self.game_over:
            self._render_end_dialog(surface, font_title, font_body, w, h, is_win=False)

    def _render_end_dialog(self, surface, font_title, font_body, w, h, is_win: bool):
        dw, dh = 420, 260
        dx = (w - dw) // 2
        dy = (h - dh) // 2

        pygame.draw.rect(surface, (252, 248, 235), (dx, dy, dw, dh), border_radius=14)
        pygame.draw.rect(surface, (242, 165, 65) if is_win else (215, 75, 60), (dx, dy, dw, dh), 4, border_radius=14)

        title = "EVENT VICTORY!" if is_win else "OUT OF MOVES!"
        title_col = (75, 175, 55) if is_win else (215, 60, 50)
        txt = font_title.render(title, True, title_col)
        surface.blit(txt, (dx + (dw - txt.get_width()) // 2, dy + 24))

        if is_win:
            msg = f"Awesome! Rewards sent directly to your Town Barn!"
            rew_txt = font_body.render(f"+250 Coins  |  +2 T-Cash  |  +1 Tool", True, (215, 140, 30))
            surface.blit(rew_txt, (dx + (dw - rew_txt.get_width()) // 2, dy + 95))
        else:
            msg = "You ran out of moves! Give it another shot."

        msg_txt = font_body.render(msg, True, (65, 50, 40))
        surface.blit(msg_txt, (dx + (dw - msg_txt.get_width()) // 2, dy + 68))

        # Button: Next Level / Retry
        btn_rect = pygame.Rect(dx + 50, dy + 160, dw - 100, 48)
        pygame.draw.rect(surface, (95, 186, 60) if is_win else (52, 152, 219), btn_rect, border_radius=8)
        btn_label = "Play Next Level" if is_win else "Try Again"
        b_txt = font_body.render(btn_label, True, (255, 255, 255))
        surface.blit(b_txt, (btn_rect.centerx - b_txt.get_width() // 2, btn_rect.centery - b_txt.get_height() // 2))

    def handle_click(self, mx: int, my: int, w: int, h: int) -> str:
        # Exit button
        close_rect = pygame.Rect(w - 140, 24, 110, 40)
        if close_rect.collidepoint(mx, my):
            get_sound_manager().play('click')
            return "exit"

        # End dialog button
        if self.game_over:
            dw, dh = 420, 260
            dx = (w - dw) // 2
            dy = (h - dh) // 2
            btn_rect = pygame.Rect(dx + 50, dy + 160, dw - 100, 48)
            if btn_rect.collidepoint(mx, my):
                if self.victory:
                    self.level += 1
                self.restart_level()
                get_sound_manager().play('click')
                return "continue"

        # Board click
        board_w = BOARD_COLS * CELL_SIZE + 24
        board_h = BOARD_ROWS * CELL_SIZE + 24
        bx = (w - board_w) // 2
        by = (h - board_h) // 2 + 30

        if bx + 12 <= mx < bx + 12 + BOARD_COLS * CELL_SIZE and by + 12 <= my < by + 12 + BOARD_ROWS * CELL_SIZE:
            col = (mx - (bx + 12)) // CELL_SIZE
            row = (my - (by + 12)) // CELL_SIZE
            self.handle_cell_click(row, col)
            return "board"

        return "none"
