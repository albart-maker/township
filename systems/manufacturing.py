"""
Township - Factory & Manufacturing System
Handles factory queues, ingredient consumption from the barn,
producing finished goods, collecting products, and T-Cash speedups.
"""

from typing import Dict, Any
from config import FACTORIES, ALL_RECIPES
from sound_manager import get_sound_manager

class ManufacturingSystem:
    def __init__(self, state):
        self.state = state

    def start_production(self, factory: Dict[str, Any], recipe_name: str) -> bool:
        if factory.get('category') != 'factory':
            return False

        recipe = ALL_RECIPES.get(recipe_name)
        if not recipe:
            return False

        if self.state.level < recipe['min_level']:
            self.state.add_toast(f"Unlocks at Level {recipe['min_level']}!", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        queue = factory.setdefault('queue', [])
        max_q = factory.get('max_queue', 3)
        if len(queue) >= max_q:
            self.state.add_toast("Production queue is full!", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        ingredients = recipe['ingredients']
        if not self.state.has_items(ingredients):
            missing_names = []
            for item, req in ingredients.items():
                have = self.state.inventory.get(item, 0)
                if have < req:
                    missing_names.append(f"{req - have}x {item.replace('_', ' ').title()}")
            self.state.add_toast(f"Missing: {', '.join(missing_names)}", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        # Consume ingredients from barn
        self.state.remove_items(ingredients)

        # Add to queue
        queue.append({
            'recipe': recipe_name,
            'remaining': recipe['prod_time'],
            'total': recipe['prod_time']
        })

        get_sound_manager().play('click')
        self.state.add_toast(f"Started producing {recipe['name']}!", color=(100, 210, 240))
        return True

    def collect_finished(self, factory: Dict[str, Any]) -> int:
        completed = factory.get('completed', [])
        if not completed:
            return 0

        collected_count = 0
        for item in list(completed):
            recipe = ALL_RECIPES.get(item, {})
            yield_qty = recipe.get('yield_qty', 1)

            if not self.state.can_add_to_barn(yield_qty):
                self.state.add_toast("Barn is full! Cannot collect all items.", color=(240, 70, 70))
                get_sound_manager().play('error')
                break

            self.state.add_to_barn(item, yield_qty)
            completed.remove(item)
            collected_count += yield_qty

            if item == 'bread':
                self.state.advance_quest('bake_bread', 1)

        if collected_count > 0:
            self.state.add_toast(f"Collected {collected_count} goods from {FACTORIES[factory['type']]['name']}!", color=(250, 220, 60))
            get_sound_manager().play('harvest')

        return collected_count

    def speedup_production(self, factory: Dict[str, Any]) -> bool:
        queue = factory.get('queue', [])
        if not queue:
            return False

        cost = 1  # 1 T-Cash
        if not self.state.spend_tcash(cost):
            return False

        item_in_progress = queue.pop(0)
        factory.setdefault('completed', []).append(item_in_progress['recipe'])
        recipe_data = ALL_RECIPES.get(item_in_progress['recipe'], {})
        self.state.add_xp(recipe_data.get('xp', 2))

        self.state.add_toast(f"Instantly finished {recipe_data.get('name', 'Item')}!", color=(100, 240, 100))
        get_sound_manager().play('speedup')
        return True
