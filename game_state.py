"""
Township - Game State & Core Data Model
Manages economy, barn inventory, buildings, field plots, factories,
livestock, helicopter orders, quests, daily rewards, and persistence.
"""

import os
import json
import time
import random
from typing import Dict, List, Optional, Any

from config import (
    STARTING_COINS, STARTING_TCASH, STARTING_XP, STARTING_LEVEL,
    STARTING_BARN_CAPACITY, STARTING_POPULATION, STARTING_POPULATION_CAP,
    CROPS, SHEDS, FACTORIES, RECIPES, ALL_RECIPES, HOUSES,
    COMMUNITY_BUILDINGS, DECORATIONS, ROADS, SPECIAL_BUILDINGS,
    ALL_ITEMS, TOWNSPEOPLE, DAILY_REWARDS, get_xp_for_level
)
from sound_manager import get_sound_manager

class GameState:
    def __init__(self):
        self.reset_to_starter_town()

    def reset_to_starter_town(self):
        self.coins: int = STARTING_COINS
        self.tcash: int = STARTING_TCASH
        self.xp: int = STARTING_XP
        self.level: int = STARTING_LEVEL
        self.population: int = 0
        self.population_cap: int = STARTING_POPULATION_CAP

        # Barn
        self.barn_capacity: int = STARTING_BARN_CAPACITY
        self.barn_upgrade_level: int = 1
        self.inventory: Dict[str, int] = {
            'wheat': 6,
            'corn': 4,
            'bread': 2,
            'cow_feed': 3,
            'nail': 1,
            'paint': 1,
            'hammer': 1,
        }

        # World Grid
        self.grid_width: int = 40
        self.grid_height: int = 40
        self.roads: Dict[str, str] = {}  # "x,y" -> road_type
        self.buildings: List[Dict[str, Any]] = []

        # Helicopter Order Board
        self.orders: List[Dict[str, Any]] = []
        self.helicopter_state: str = 'idle'  # 'idle', 'flying_out', 'flying_back'
        self.helicopter_timer: float = 0.0
        self.active_order_reward: Optional[Dict[str, Any]] = None

        # Daily Streak
        self.daily_streak: int = 1
        self.last_daily_claim_time: float = 0.0
        self.can_claim_daily: bool = True

        # Quests / Ernie Tutorial
        self.current_quest_idx: int = 0
        self.quests = [
            {
                'id': 'harvest_wheat',
                'title': 'Harvest Wheat',
                'desc': 'Harvest 3 ripe Wheat crops from your farm plots.',
                'target': 3,
                'progress': 0,
                'reward_coins': 50,
                'reward_xp': 15,
                'reward_tcash': 1,
                'completed': False
            },
            {
                'id': 'feed_cows',
                'title': 'Feed the Cows',
                'desc': 'Feed your cows in the Cow Shed with Cow Feed.',
                'target': 1,
                'progress': 0,
                'reward_coins': 80,
                'reward_xp': 25,
                'reward_tcash': 1,
                'completed': False
            },
            {
                'id': 'bake_bread',
                'title': 'Bake Fresh Bread',
                'desc': 'Produce 2 loaves of Bread in the Bakery.',
                'target': 2,
                'progress': 0,
                'reward_coins': 120,
                'reward_xp': 35,
                'reward_tcash': 2,
                'completed': False
            },
            {
                'id': 'send_helicopter',
                'title': 'Ernie\'s Helicopter Order',
                'desc': 'Fulfill and dispatch an order from the Order Board!',
                'target': 1,
                'progress': 0,
                'reward_coins': 150,
                'reward_xp': 50,
                'reward_tcash': 3,
                'completed': False
            },
            {
                'id': 'build_cottage',
                'title': 'Town Growth',
                'desc': 'Build a new Cottage to increase your town population.',
                'target': 1,
                'progress': 0,
                'reward_coins': 200,
                'reward_xp': 60,
                'reward_tcash': 2,
                'completed': False
            },
            {
                'id': 'play_match3',
                'title': 'Adventure Event',
                'desc': 'Play and win a Match-3 Adventure puzzle level!',
                'target': 1,
                'progress': 0,
                'reward_coins': 300,
                'reward_xp': 100,
                'reward_tcash': 5,
                'completed': False
            }
        ]

        # Toast notifications queue
        self.toasts: List[Dict[str, Any]] = []

        # Setup initial starter town layout
        self._setup_starter_layout()
        self._generate_initial_orders()

    def _setup_starter_layout(self):
        # Helipad at (18, 14)
        self.add_building('helipad', 'special', 18, 14, 3, 3)

        # Starter Town Hall at (18, 9)
        self.add_building('town_hall', 'community', 18, 9, 3, 3)

        # Starter Cottage at (14, 10)
        self.add_building('cottage', 'house', 14, 10, 2, 2)

        # Bakery at (23, 10)
        self.add_building('bakery', 'factory', 23, 10, 3, 2)

        # Feed Mill at (14, 14)
        self.add_building('feed_mill', 'factory', 14, 14, 2, 2)

        # Cow Shed at (23, 14)
        self.add_building('cow_shed', 'shed', 23, 14, 3, 2)

        # 6 Starter Farm plots at (18..20, 19..20)
        for gx in range(17, 23):
            for gy in [19, 20]:
                plot = self.add_building('field_plot', 'crop', gx, gy, 1, 1)
                # Plant initial wheat on some plots
                if gx < 20:
                    plot['planted_crop'] = 'wheat'
                    plot['plant_time'] = time.time() - 5.0  # already ripe!
                    plot['grow_duration'] = CROPS['wheat']['grow_time']

        # Roads linking the starter town
        for x in range(13, 27):
            self.roads[f"{x},13"] = 'road_paved'
        for y in range(8, 22):
            self.roads[f"17,{y}"] = 'road_paved'
            self.roads[f"22,{y}"] = 'road_paved'

        # Decorative trees & flowers
        self.add_building('park_tree', 'decoration', 13, 9, 1, 1)
        self.add_building('flower_bed', 'decoration', 16, 10, 1, 1)
        self.add_building('street_lamp', 'decoration', 17, 12, 1, 1)

        self.recalculate_population()

    # -------------------------------------------------------------
    # BUILDING & GRID MANAGEMENT
    # -------------------------------------------------------------
    def add_building(self, b_type: str, category: str, gx: int, gy: int, w: int, h: int) -> Dict[str, Any]:
        b_id = f"{b_type}_{int(time.time() * 1000)}_{random.randint(100, 999)}"
        b = {
            'id': b_id,
            'type': b_type,
            'category': category,
            'gx': gx,
            'gy': gy,
            'w': w,
            'h': h,
        }

        if category == 'crop':
            b['planted_crop'] = None
            b['plant_time'] = 0.0
            b['grow_duration'] = 0.0

        elif category == 'shed':
            b['fed'] = False
            b['feed_time'] = 0.0
            b['duration'] = SHEDS[b_type]['prod_time']
            b['ready_count'] = 0

        elif category == 'factory':
            b['queue'] = []       # list of {'recipe': str, 'remaining': float, 'total': float}
            b['completed'] = []   # list of finished recipe strings
            b['max_queue'] = 3

        self.buildings.append(b)
        return b

    def get_building_at(self, gx: int, gy: int) -> Optional[Dict[str, Any]]:
        for b in self.buildings:
            if b['gx'] <= gx < b['gx'] + b['w'] and b['gy'] <= gy < b['gy'] + b['h']:
                return b
        return None

    def is_area_clear(self, gx: int, gy: int, w: int, h: int, ignore_id: Optional[str] = None) -> bool:
        if gx < 0 or gy < 0 or gx + w > self.grid_width or gy + h > self.grid_height:
            return False

        for b in self.buildings:
            if ignore_id and b['id'] == ignore_id:
                continue
            # Check AABB overlap
            if not (gx + w <= b['gx'] or gx >= b['gx'] + b['w'] or
                    gy + h <= b['gy'] or gy >= b['gy'] + b['h']):
                return False
        return True

    def recalculate_population(self):
        pop = 0
        cap = STARTING_POPULATION_CAP
        for b in self.buildings:
            if b['type'] in HOUSES:
                pop += HOUSES[b['type']]['pop']
            elif b['type'] in COMMUNITY_BUILDINGS:
                cap += COMMUNITY_BUILDINGS[b['type']]['pop_cap']
        self.population = min(pop, cap)
        self.population_cap = cap

    # -------------------------------------------------------------
    # BARN INVENTORY
    # -------------------------------------------------------------
    def get_barn_count(self) -> int:
        return sum(self.inventory.values())

    def can_add_to_barn(self, qty: int = 1) -> bool:
        return (self.get_barn_count() + qty) <= self.barn_capacity

    def add_to_barn(self, item: str, qty: int = 1) -> bool:
        if not self.can_add_to_barn(qty):
            self.add_toast("Barn is FULL! Upgrade or sell items.", color=(240, 70, 70))
            get_sound_manager().play('error')
            return False
        self.inventory[item] = self.inventory.get(item, 0) + qty
        return True

    def remove_from_barn(self, item: str, qty: int = 1) -> bool:
        if self.inventory.get(item, 0) < qty:
            return False
        self.inventory[item] -= qty
        if self.inventory[item] <= 0:
            del self.inventory[item]
        return True

    def has_items(self, items_dict: Dict[str, int]) -> bool:
        for item, req_qty in items_dict.items():
            if self.inventory.get(item, 0) < req_qty:
                return False
        return True

    def remove_items(self, items_dict: Dict[str, int]) -> bool:
        if not self.has_items(items_dict):
            return False
        for item, qty in items_dict.items():
            self.remove_from_barn(item, qty)
        return True

    def sell_item(self, item: str, qty: int = 1) -> bool:
        if self.inventory.get(item, 0) < qty:
            return False
        price_per = ALL_ITEMS.get(item, {}).get('sell', 1)
        earned = price_per * qty
        self.remove_from_barn(item, qty)
        self.add_coins(earned)
        self.add_toast(f"Sold {qty}x for +{earned} Coins!", color=(255, 215, 50))
        get_sound_manager().play('coin')
        return True

    def get_barn_upgrade_requirements(self) -> Dict[str, int]:
        req_count = self.barn_upgrade_level + 1
        return {'nail': req_count, 'paint': req_count, 'hammer': req_count}

    def can_upgrade_barn(self) -> bool:
        reqs = self.get_barn_upgrade_requirements()
        return self.has_items(reqs)

    def upgrade_barn(self) -> bool:
        reqs = self.get_barn_upgrade_requirements()
        if not self.remove_items(reqs):
            return False
        self.barn_capacity += 30
        self.barn_upgrade_level += 1
        self.add_toast(f"Barn Upgraded! Capacity: {self.barn_capacity}", color=(90, 220, 90))
        get_sound_manager().play('level_up')
        return True

    # -------------------------------------------------------------
    # PROGRESSION & ECONOMY
    # -------------------------------------------------------------
    def add_coins(self, amount: int):
        self.coins += amount

    def add_tcash(self, amount: int):
        self.tcash += amount

    def spend_coins(self, amount: int) -> bool:
        if self.coins >= amount:
            self.coins -= amount
            return True
        self.add_toast("Not enough Coins!", color=(240, 70, 70))
        get_sound_manager().play('error')
        return False

    def spend_tcash(self, amount: int) -> bool:
        if self.tcash >= amount:
            self.tcash -= amount
            return True
        self.add_toast("Not enough T-Cash!", color=(240, 70, 70))
        get_sound_manager().play('error')
        return False

    def add_xp(self, amount: int):
        self.xp += amount
        next_threshold = get_xp_for_level(self.level + 1)
        if self.xp >= next_threshold:
            self.level_up()

    def level_up(self):
        self.level += 1
        tcash_reward = 5 if self.level < 5 else 10
        coin_reward = self.level * 100
        self.coins += coin_reward
        self.tcash += tcash_reward
        self.add_toast(f"LEVEL UP! Reached Level {self.level}! +{coin_reward} Coins, +{tcash_reward} T$", color=(255, 230, 80))
        get_sound_manager().play('level_up')

    # -------------------------------------------------------------
    # HELICOPTER ORDERS
    # -------------------------------------------------------------
    def _generate_initial_orders(self):
        self.orders = []
        for i in range(6):
            self.orders.append(self._create_random_order(i + 1))

    def _create_random_order(self, order_id: int) -> Dict[str, Any]:
        char = random.choice(TOWNSPEOPLE)
        # Select items based on player level
        available_items = ['wheat', 'corn']
        if self.level >= 2:
            available_items.extend(['bread', 'milk', 'chicken_feed'])
        if self.level >= 3:
            available_items.extend(['carrot', 'egg', 'cheese'])
        if self.level >= 4:
            available_items.extend(['sugarcane', 'sugar', 'cookie'])
        if self.level >= 5:
            available_items.extend(['cotton', 'wool', 'butter'])

        demands = {}
        num_items = random.randint(1, 3)
        chosen = random.sample(available_items, min(num_items, len(available_items)))

        total_value = 0
        for item in chosen:
            qty = random.randint(1, 3)
            demands[item] = qty
            sell_val = ALL_ITEMS.get(item, {}).get('sell', 2)
            total_value += sell_val * qty

        coins_reward = int(total_value * random.uniform(1.8, 2.5)) + 10
        xp_reward = int(coins_reward * 0.4) + 5

        # Chance for building tool
        tool_reward = None
        if random.random() < 0.25:
            tool_reward = random.choice(['nail', 'paint', 'hammer'])

        return {
            'id': order_id,
            'character': char['id'],
            'name': char['name'],
            'role': char['role'],
            'phrase': char['phrase'],
            'demands': demands,
            'coins': coins_reward,
            'xp': xp_reward,
            'tool': tool_reward,
            'cooldown': 0.0
        }

    def dispatch_helicopter(self, order_id: int) -> bool:
        if self.helicopter_state != 'idle':
            return False

        order = next((o for o in self.orders if o['id'] == order_id), None)
        if not order:
            return False

        if not self.remove_items(order['demands']):
            self.add_toast("Missing items for order!", color=(240, 70, 70))
            get_sound_manager().play('error')
            return False

        # Launch helicopter!
        self.helicopter_state = 'flying_out'
        self.helicopter_timer = 3.5  # 3.5s delivery flight
        self.active_order_reward = {
            'coins': order['coins'],
            'xp': order['xp'],
            'tool': order['tool']
        }

        # Replace order with cooldown
        order['cooldown'] = 15.0  # 15s until next order
        get_sound_manager().play('helicopter')

        # Quest progress
        self.advance_quest('send_helicopter')
        return True

    def trash_order(self, order_id: int):
        order = next((o for o in self.orders if o['id'] == order_id), None)
        if order:
            order['cooldown'] = 12.0
            get_sound_manager().play('click')
            self.add_toast("Order discarded. New order arriving shortly.", color=(200, 200, 200))

    # -------------------------------------------------------------
    # TICKING TIMERS & UPDATES
    # -------------------------------------------------------------
    def tick(self, dt: float):
        now = time.time()

        # Update Helicopter
        if self.helicopter_state in ('flying_out', 'flying_back'):
            self.helicopter_timer -= dt
            if self.helicopter_state == 'flying_out' and self.helicopter_timer <= 1.75:
                self.helicopter_state = 'flying_back'
            if self.helicopter_timer <= 0:
                self.helicopter_state = 'idle'
                if self.active_order_reward:
                    rew = self.active_order_reward
                    self.add_coins(rew['coins'])
                    self.add_xp(rew['xp'])
                    tool_text = ""
                    if rew['tool'] and self.can_add_to_barn():
                        self.add_to_barn(rew['tool'], 1)
                        tool_text = f", +1 {rew['tool'].capitalize()}"
                    self.add_toast(f"Helicopter returned! +{rew['coins']} Coins, +{rew['xp']} XP{tool_text}!", color=(255, 220, 50))
                    get_sound_manager().play('coin')
                    self.active_order_reward = None

        # Update Order Cooldowns
        for order in self.orders:
            if order.get('cooldown', 0.0) > 0:
                order['cooldown'] -= dt
                if order['cooldown'] <= 0:
                    new_order = self._create_random_order(order['id'])
                    order.update(new_order)

        # Update Buildings (Factories & Sheds)
        for b in self.buildings:
            cat = b['category']
            if cat == 'factory':
                queue = b.get('queue', [])
                if queue:
                    curr = queue[0]
                    curr['remaining'] -= dt
                    if curr['remaining'] <= 0:
                        finished = queue.pop(0)
                        b.setdefault('completed', []).append(finished['recipe'])
                        recipe_data = ALL_RECIPES.get(finished['recipe'], {})
                        self.add_xp(recipe_data.get('xp', 2))

            elif cat == 'shed':
                if b.get('fed', False):
                    feed_time = b.get('feed_time', 0.0)
                    duration = b.get('duration', 10.0)
                    if now - feed_time >= duration:
                        b['fed'] = False
                        b['ready_count'] = SHEDS[b['type']]['animal_count']

        # Update Toasts
        for t in self.toasts:
            t['timer'] -= dt
        self.toasts = [t for t in self.toasts if t['timer'] > 0]

    # -------------------------------------------------------------
    # QUESTS
    # -------------------------------------------------------------
    def advance_quest(self, quest_id: str, amount: int = 1):
        if self.current_quest_idx < len(self.quests):
            q = self.quests[self.current_quest_idx]
            if q['id'] == quest_id and not q['completed']:
                q['progress'] += amount
                if q['progress'] >= q['target']:
                    q['completed'] = True
                    self.add_coins(q['reward_coins'])
                    self.add_xp(q['reward_xp'])
                    self.add_tcash(q['reward_tcash'])
                    self.add_toast(f"Quest Complete: {q['title']}! +{q['reward_coins']} Coins, +{q['reward_tcash']} T$!", color=(110, 235, 110))
                    get_sound_manager().play('level_up')
                    self.current_quest_idx += 1

    # -------------------------------------------------------------
    # TOASTS
    # -------------------------------------------------------------
    def add_toast(self, message: str, color=(255, 255, 255)):
        self.toasts.append({
            'message': message,
            'color': color,
            'timer': 2.8,
            'initial_timer': 2.8
        })

    # -------------------------------------------------------------
    # PERSISTENCE (SAVE / LOAD)
    # -------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            'coins': self.coins,
            'tcash': self.tcash,
            'xp': self.xp,
            'level': self.level,
            'town_name': getattr(self, 'town_name', 'Sunny Township'),
            'population': self.population,
            'population_cap': self.population_cap,
            'barn_capacity': self.barn_capacity,
            'barn_upgrade_level': self.barn_upgrade_level,
            'inventory': self.inventory,
            'roads': self.roads,
            'buildings': self.buildings,
            'orders': self.orders,
            'daily_streak': self.daily_streak,
            'last_daily_claim_time': self.last_daily_claim_time,
            'current_quest_idx': self.current_quest_idx,
            'last_saved': time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def from_dict(self, data: Dict[str, Any]):
        self.coins = data.get('coins', STARTING_COINS)
        self.tcash = data.get('tcash', STARTING_TCASH)
        self.xp = data.get('xp', STARTING_XP)
        self.level = data.get('level', STARTING_LEVEL)
        self.town_name = data.get('town_name', 'Sunny Township')
        self.population = data.get('population', 0)
        self.population_cap = data.get('population_cap', STARTING_POPULATION_CAP)
        self.barn_capacity = data.get('barn_capacity', STARTING_BARN_CAPACITY)
        self.barn_upgrade_level = data.get('barn_upgrade_level', 1)
        self.inventory = data.get('inventory', {})
        self.roads = data.get('roads', {})
        self.buildings = data.get('buildings', [])
        self.orders = data.get('orders', [])
        self.daily_streak = data.get('daily_streak', 1)
        self.last_daily_claim_time = data.get('last_daily_claim_time', 0.0)
        self.current_quest_idx = data.get('current_quest_idx', 0)
        self.recalculate_population()

    # -------------------------------------------------------------
    # MULTI-SLOT SAVE / LOAD SYSTEM
    # -------------------------------------------------------------
    @staticmethod
    def get_slot_path(slot_id: int) -> str:
        saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        os.makedirs(saves_dir, exist_ok=True)
        return os.path.join(saves_dir, f"slot_{slot_id}.json")

    @classmethod
    def get_slot_metadata(cls, slot_id: int) -> Dict[str, Any]:
        path = cls.get_slot_path(slot_id)
        if not os.path.exists(path):
            # Check legacy savegame.json for slot 1
            if slot_id == 1 and os.path.exists("savegame.json"):
                path = "savegame.json"
            else:
                return {
                    'slot_id': slot_id,
                    'exists': False,
                    'town_name': f"Slot {slot_id}",
                    'level': 1,
                    'coins': 0,
                    'tcash': 0,
                    'population': 0,
                    'last_saved': "Empty"
                }

        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            return {
                'slot_id': slot_id,
                'exists': True,
                'town_name': d.get('town_name', f"Town {slot_id}"),
                'level': d.get('level', 1),
                'coins': d.get('coins', 0),
                'tcash': d.get('tcash', 0),
                'population': d.get('population', 0),
                'last_saved': d.get('last_saved', 'Recent')
            }
        except Exception:
            return {
                'slot_id': slot_id,
                'exists': False,
                'town_name': f"Corrupted Slot {slot_id}",
                'level': 1,
                'coins': 0,
                'tcash': 0,
                'population': 0,
                'last_saved': "Error"
            }

    def save_to_slot(self, slot_id: int):
        self.active_slot = slot_id
        path = self.get_slot_path(slot_id)
        self.save_to_file(path)

    def load_from_slot(self, slot_id: int) -> bool:
        self.active_slot = slot_id
        path = self.get_slot_path(slot_id)
        if not os.path.exists(path) and slot_id == 1 and os.path.exists("savegame.json"):
            path = "savegame.json"
        return self.load_from_file(path)

    @classmethod
    def delete_slot(cls, slot_id: int) -> bool:
        path = cls.get_slot_path(slot_id)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception:
                return False
        return False

    def save_to_file(self, filepath: str = "savegame.json"):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
            self.add_toast("Game Saved successfully!", color=(120, 225, 120))
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_from_file(self, filepath: str = "savegame.json") -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.from_dict(data)
            self.add_toast("Game Loaded!", color=(120, 225, 120))
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
