"""
Township - City Building System
Handles purchasing and placing houses, community buildings, factories,
decorations, roads, moving structures, and checking population caps.
"""

from typing import Dict, Any, Optional
from config import (
    HOUSES, COMMUNITY_BUILDINGS, FACTORIES, SHEDS,
    DECORATIONS, ROADS, SPECIAL_BUILDINGS
)
from sound_manager import get_sound_manager

class CityBuildingSystem:
    def __init__(self, state):
        self.state = state

    def can_place_building(self, b_type: str, category: str, gx: int, gy: int) -> tuple[bool, str]:
        info = self._get_building_info(b_type, category)
        if not info:
            return False, "Unknown building type."

        min_lvl = info.get('min_level', 1)
        if self.state.level < min_lvl:
            return False, f"Unlocks at Level {min_lvl}!"

        cost = info.get('cost', 0)
        if self.state.coins < cost:
            return False, f"Not enough Coins! Need {cost}."

        w, h = info.get('size', (1, 1))
        if not self.state.is_area_clear(gx, gy, w, h):
            return False, "Area is blocked or out of bounds!"

        # Population Cap check for Houses
        if category == 'house':
            gain_pop = info.get('pop', 0)
            if self.state.population + gain_pop > self.state.population_cap:
                return False, f"Population cap reached! Build Community Buildings to increase cap ({self.state.population}/{self.state.population_cap})."

        return True, "OK"

    def place_building(self, b_type: str, category: str, gx: int, gy: int) -> Optional[Dict[str, Any]]:
        can_place, reason = self.can_place_building(b_type, category, gx, gy)
        if not can_place:
            self.state.add_toast(reason, color=(240, 80, 80))
            get_sound_manager().play('error')
            return None

        info = self._get_building_info(b_type, category)
        cost = info.get('cost', 0)
        w, h = info.get('size', (1, 1))

        self.state.spend_coins(cost)
        b = self.state.add_building(b_type, category, gx, gy, w, h)

        xp_gain = info.get('xp', 5)
        if xp_gain > 0:
            self.state.add_xp(xp_gain)

        self.state.recalculate_population()
        self.state.add_toast(f"Built {info.get('name', b_type)}! (+{xp_gain} XP)", color=(110, 225, 110))
        get_sound_manager().play('coin')

        if b_type == 'cottage':
            self.state.advance_quest('build_cottage', 1)

        return b

    def place_road(self, road_type: str, gx: int, gy: int) -> bool:
        road_info = ROADS.get(road_type)
        if not road_info:
            return False

        if 0 <= gx < self.state.grid_width and 0 <= gy < self.state.grid_height:
            if not self.state.spend_coins(road_info['cost']):
                return False
            self.state.roads[f"{gx},{gy}"] = road_type
            get_sound_manager().play('click')
            return True
        return False

    def remove_road(self, gx: int, gy: int) -> bool:
        key = f"{gx},{gy}"
        if key in self.state.roads:
            del self.state.roads[key]
            get_sound_manager().play('click')
            return True
        return False

    def bulldoze_building(self, building: Dict[str, Any]) -> bool:
        # Cannot bulldoze essential structures like Helipad or Town Hall
        if building['type'] in ['helipad', 'town_hall']:
            self.state.add_toast("Cannot bulldoze core town structures!", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        if building in self.state.buildings:
            self.state.buildings.remove(building)
            self.state.recalculate_population()
            self.state.add_toast("Building removed.", color=(200, 200, 200))
            get_sound_manager().play('click')
            return True
        return False

    def move_building(self, building: Dict[str, Any], new_gx: int, new_gy: int) -> bool:
        w, h = building['w'], building['h']
        if not self.state.is_area_clear(new_gx, new_gy, w, h, ignore_id=building['id']):
            self.state.add_toast("Target area is blocked!", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        building['gx'] = new_gx
        building['gy'] = new_gy
        self.state.add_toast("Building relocated.", color=(120, 220, 120))
        get_sound_manager().play('click')
        return True

    def _get_building_info(self, b_type: str, category: str) -> Optional[Dict[str, Any]]:
        if category == 'house':
            return HOUSES.get(b_type)
        elif category == 'community':
            return COMMUNITY_BUILDINGS.get(b_type)
        elif category == 'factory':
            return FACTORIES.get(b_type)
        elif category == 'shed':
            return SHEDS.get(b_type)
        elif category == 'decoration':
            return DECORATIONS.get(b_type)
        elif category == 'crop':
            return SPECIAL_BUILDINGS.get(b_type)
        return None
