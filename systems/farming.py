"""
Township - Farming System
Handles planting crops on field plots, growth calculation,
harvesting into the barn, and T-Cash instant speedups.
"""

import time
from typing import Dict, Any, Optional
from config import CROPS
from sound_manager import get_sound_manager

class FarmingSystem:
    def __init__(self, state):
        self.state = state

    def plant_crop(self, plot: Dict[str, Any], crop_name: str) -> bool:
        if plot.get('category') != 'crop':
            return False
        if plot.get('planted_crop') is not None:
            return False

        crop_info = CROPS.get(crop_name)
        if not crop_info:
            return False

        if self.state.level < crop_info['min_level']:
            self.state.add_toast(f"Unlocks at Level {crop_info['min_level']}!", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        if crop_info['cost'] > 0:
            if not self.state.spend_coins(crop_info['cost']):
                return False

        plot['planted_crop'] = crop_name
        plot['plant_time'] = time.time()
        plot['grow_duration'] = crop_info['grow_time']
        get_sound_manager().play('click')
        return True

    def is_crop_ripe(self, plot: Dict[str, Any]) -> bool:
        if plot.get('planted_crop') is None:
            return False
        elapsed = time.time() - plot.get('plant_time', 0.0)
        return elapsed >= plot.get('grow_duration', 1.0)

    def get_crop_stage(self, plot: Dict[str, Any]) -> int:
        if plot.get('planted_crop') is None:
            return 0
        elapsed = time.time() - plot.get('plant_time', 0.0)
        duration = plot.get('grow_duration', 1.0)
        ratio = min(1.0, elapsed / max(0.1, duration))
        if ratio >= 1.0:
            return 2  # Fully mature
        elif ratio >= 0.4:
            return 1  # Growing
        else:
            return 0  # Sprout

    def harvest_crop(self, plot: Dict[str, Any]) -> bool:
        if not self.is_crop_ripe(plot):
            return False

        crop_name = plot['planted_crop']
        crop_info = CROPS[crop_name]

        # Each harvest yields 2 crops (classic Township farming loop: 1 seed -> 2 crops!)
        yield_qty = 2
        if not self.state.can_add_to_barn(yield_qty):
            self.state.add_toast("Barn is full! Cannot harvest.", color=(240, 70, 70))
            get_sound_manager().play('error')
            return False

        self.state.add_to_barn(crop_name, yield_qty)
        self.state.add_xp(crop_info['xp'])
        self.state.add_toast(f"Harvested {yield_qty}x {crop_info['name']}! (+{crop_info['xp']} XP)", color=(250, 220, 70))
        get_sound_manager().play('harvest')

        # Advance harvest quest
        if crop_name == 'wheat':
            self.state.advance_quest('harvest_wheat', 1)

        # Clear plot for replanting
        plot['planted_crop'] = None
        plot['plant_time'] = 0.0
        plot['grow_duration'] = 0.0
        return True

    def speedup_crop(self, plot: Dict[str, Any]) -> bool:
        if plot.get('planted_crop') is None or self.is_crop_ripe(plot):
            return False

        speedup_cost = 1  # 1 T-Cash
        if not self.state.spend_tcash(speedup_cost):
            return False

        # Instantly make ripe
        plot['plant_time'] = time.time() - plot.get('grow_duration', 1.0)
        self.state.add_toast("Crop instantly matured!", color=(100, 240, 100))
        get_sound_manager().play('speedup')
        return True
