"""
Township - Automated Game Logic & Subsystem Test Suite
Tests economy, barn, agriculture, manufacturing, livestock,
city building, population dynamics, match-3 physics, and save/load persistence.
"""

import os
import sys
import time
import unittest

# Add current folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import GameState
from systems.farming import FarmingSystem
from systems.livestock import LivestockSystem
from systems.manufacturing import ManufacturingSystem
from systems.city_building import CityBuildingSystem
from minigame.match3 import Match3Game
from sprites import get_sprite_manager
from config import CROPS, SHEDS, FACTORIES, HOUSES, COMMUNITY_BUILDINGS

class TestTownshipGame(unittest.TestCase):
    def setUp(self):
        self.state = GameState()
        self.farming = FarmingSystem(self.state)
        self.livestock = LivestockSystem(self.state)
        self.mfg = ManufacturingSystem(self.state)
        self.building = CityBuildingSystem(self.state)

    def test_economy_and_barn(self):
        # Initial stats
        self.assertEqual(self.state.coins, 350)
        self.assertEqual(self.state.tcash, 25)
        self.assertEqual(self.state.level, 1)

        # Spend & add coins
        self.assertTrue(self.state.spend_coins(50))
        self.assertEqual(self.state.coins, 300)
        self.state.add_coins(100)
        self.assertEqual(self.state.coins, 400)

        # Barn capacity & inventory
        initial_count = self.state.get_barn_count()
        self.assertTrue(self.state.can_add_to_barn(5))
        self.assertTrue(self.state.add_to_barn('wheat', 5))
        self.assertEqual(self.state.get_barn_count(), initial_count + 5)

        # Selling items
        self.assertTrue(self.state.sell_item('wheat', 2))
        self.assertEqual(self.state.get_barn_count(), initial_count + 3)

        # Barn upgrade test
        self.state.inventory['nail'] = 5
        self.state.inventory['paint'] = 5
        self.state.inventory['hammer'] = 5
        old_cap = self.state.barn_capacity
        self.assertTrue(self.state.upgrade_barn())
        self.assertEqual(self.state.barn_capacity, old_cap + 30)

    def test_farming_cycle(self):
        # Find a farm plot
        plot = next(b for b in self.state.buildings if b['type'] == 'field_plot')
        plot['planted_crop'] = None

        # Plant wheat
        self.assertTrue(self.farming.plant_crop(plot, 'wheat'))
        self.assertEqual(plot['planted_crop'], 'wheat')

        # Fast forward growth
        plot['plant_time'] = time.time() - 10.0
        self.assertTrue(self.farming.is_crop_ripe(plot))

        # Harvest crop
        initial_wheat = self.state.inventory.get('wheat', 0)
        self.assertTrue(self.farming.harvest_crop(plot))
        self.assertEqual(self.state.inventory.get('wheat', 0), initial_wheat + 2)
        self.assertIsNone(plot['planted_crop'])

    def test_livestock_cycle(self):
        # Find cow shed
        shed = next(b for b in self.state.buildings if b['type'] == 'cow_shed')
        shed['fed'] = False
        shed['ready_count'] = 0

        # Ensure we have cow feed
        self.state.inventory['cow_feed'] = 2

        # Feed the cows
        self.assertTrue(self.livestock.feed_shed(shed))
        self.assertTrue(shed['fed'])

        # Fast forward production
        shed['feed_time'] = time.time() - 20.0
        self.state.tick(0.1)
        self.assertEqual(shed['ready_count'], SHEDS['cow_shed']['animal_count'])

        # Collect milk
        initial_milk = self.state.inventory.get('milk', 0)
        self.assertTrue(self.livestock.collect_products(shed))
        self.assertEqual(self.state.inventory.get('milk', 0), initial_milk + 3)
        self.assertEqual(shed['ready_count'], 0)

    def test_manufacturing_cycle(self):
        # Find bakery
        bakery = next(b for b in self.state.buildings if b['type'] == 'bakery')
        bakery['queue'] = []
        bakery['completed'] = []

        # Give wheat to make bread
        self.state.inventory['wheat'] = 4

        # Start baking bread
        self.assertTrue(self.mfg.start_production(bakery, 'bread'))
        self.assertEqual(len(bakery['queue']), 1)
        self.assertEqual(self.state.inventory['wheat'], 2)

        # Tick factory timer to complete
        bakery['queue'][0]['remaining'] = 0.05
        self.state.tick(0.1)
        self.assertEqual(len(bakery['queue']), 0)
        self.assertIn('bread', bakery['completed'])

        # Collect bread
        initial_bread = self.state.inventory.get('bread', 0)
        collected = self.mfg.collect_finished(bakery)
        self.assertEqual(collected, 1)
        self.assertEqual(self.state.inventory.get('bread', 0), initial_bread + 1)

    def test_city_building_and_population_cap(self):
        # Start state population
        self.state.level = 2
        self.state.population = 25
        self.state.population_cap = 30

        # Try to build townhouse (+15 pop) -> should exceed pop cap of 30!
        can_place, reason = self.building.can_place_building('townhouse', 'house', 30, 30)
        self.assertFalse(can_place)
        self.assertIn("cap", reason.lower())

        # Build community building (Town Hall gives +30 pop cap)
        self.state.coins = 2000
        self.building.place_building('school', 'community', 30, 30)
        self.state.recalculate_population()
        self.assertGreater(self.state.population_cap, 30)

        # Now building townhouse succeeds
        self.assertTrue(self.building.can_place_building('townhouse', 'house', 34, 30)[0])

    def test_helicopter_orders(self):
        self.assertEqual(len(self.state.orders), 6)
        order = self.state.orders[0]
        # Satisfy demands
        for item, req in order['demands'].items():
            self.state.inventory[item] = req + 2

        initial_coins = self.state.coins
        self.assertTrue(self.state.dispatch_helicopter(order['id']))
        self.assertEqual(self.state.helicopter_state, 'flying_out')

        # Fast forward helicopter delivery
        self.state.tick(3.6)
        self.assertEqual(self.state.helicopter_state, 'idle')
        self.assertGreater(self.state.coins, initial_coins)

    def test_match3_mechanics(self):
        sprites = get_sprite_manager()
        m3 = Match3Game(self.state, sprites)
        self.assertEqual(len(m3.board), 8)
        self.assertEqual(len(m3.board[0]), 8)

        # Test match resolution
        m3.board[0][0] = 'apple'
        m3.board[0][1] = 'apple'
        m3.board[0][2] = 'apple'
        matches = m3._find_matches()
        self.assertIn((0, 0), matches)
        self.assertIn((0, 1), matches)
        self.assertIn((0, 2), matches)

    def test_speedups_with_tcash(self):
        # Crop speedup
        plot = next(b for b in self.state.buildings if b['type'] == 'field_plot')
        plot['planted_crop'] = 'strawberry'
        plot['plant_time'] = time.time()  # just planted
        plot['grow_duration'] = 60.0

        old_tcash = self.state.tcash
        self.assertTrue(self.farming.speedup_crop(plot))
        self.assertEqual(self.state.tcash, old_tcash - 1)
        self.assertTrue(self.farming.is_crop_ripe(plot))

        # Factory speedup
        bakery = next(b for b in self.state.buildings if b['type'] == 'bakery')
        bakery['queue'] = [{'recipe': 'bread', 'remaining': 10.0, 'total': 10.0}]
        self.assertTrue(self.mfg.speedup_production(bakery))
        self.assertEqual(len(bakery['queue']), 0)
        self.assertIn('bread', bakery['completed'])

    def test_quests_progression(self):
        q = self.state.quests[0]
        self.assertEqual(q['id'], 'harvest_wheat')
        initial_coins = self.state.coins
        # Advance quest to completion
        self.state.advance_quest('harvest_wheat', 3)
        self.assertTrue(q['completed'])
        self.assertGreater(self.state.coins, initial_coins)
        self.assertEqual(self.state.current_quest_idx, 1)

    def test_daily_bonus(self):
        self.assertTrue(self.state.can_claim_daily)
        self.assertEqual(self.state.daily_streak, 1)
        initial_coins = self.state.coins
        initial_tcash = self.state.tcash
        # Claim Day 1
        reward = self.state.coins
        self.state.add_coins(50)
        self.state.add_tcash(1)
        self.state.can_claim_daily = False
        self.state.daily_streak = 2
        self.assertFalse(self.state.can_claim_daily)
        self.assertEqual(self.state.daily_streak, 2)

    def test_save_and_load_persistence(self):
        test_save = "test_savegame.json"
        self.state.coins = 9876
        self.state.tcash = 42
        self.state.level = 5
        self.state.save_to_file(test_save)

        # Load into new state
        new_state = GameState()
        self.assertTrue(new_state.load_from_file(test_save))
        self.assertEqual(new_state.coins, 9876)
        self.assertEqual(new_state.tcash, 42)
        self.assertEqual(new_state.level, 5)

        if os.path.exists(test_save):
            os.remove(test_save)

    def test_multi_slot_saves(self):
        # Test Slot 2
        self.state.coins = 5555
        self.state.level = 3
        self.state.town_name = "Rivendell"
        self.state.save_to_slot(2)

        meta = GameState.get_slot_metadata(2)
        self.assertTrue(meta['exists'])
        self.assertEqual(meta['town_name'], "Rivendell")
        self.assertEqual(meta['level'], 3)
        self.assertEqual(meta['coins'], 5555)

        # Load into clean state
        loaded_state = GameState()
        self.assertTrue(loaded_state.load_from_slot(2))
        self.assertEqual(loaded_state.coins, 5555)
        self.assertEqual(loaded_state.town_name, "Rivendell")

        # Delete slot
        self.assertTrue(GameState.delete_slot(2))
        meta_after = GameState.get_slot_metadata(2)
        self.assertFalse(meta_after['exists'])

    def test_asset_loader_and_animations(self):
        import pygame
        from asset_loader import get_asset_loader, AnimatedSprite

        loader = get_asset_loader()
        # Fallback surface test
        fallback = pygame.Surface((32, 32))
        res = loader.load_image("non_existent_file.png", fallback_surface=fallback)
        self.assertIsNotNone(res)
        self.assertEqual(res.get_size(), (32, 32))

        # Spritesheet slicing fallback
        frame1 = pygame.Surface((16, 16))
        frame2 = pygame.Surface((16, 16))
        sheet_res = loader.load_spritesheet("dummy_sheet.png", 16, 16, fallback_frames=[frame1, frame2])
        self.assertEqual(len(sheet_res), 2)

        # AnimatedSprite timer progression
        anim = AnimatedSprite([frame1, frame2], fps=10.0, loop=True)
        self.assertEqual(anim.current_idx, 0)
        anim.update(0.12)  # more than 1 frame at 10 fps
        self.assertEqual(anim.current_idx, 1)

if __name__ == '__main__':
    unittest.main()
