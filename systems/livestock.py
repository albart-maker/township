"""
Township - Livestock & Sheds System
Handles feeding animals (cows, chickens, sheep), production timers,
collecting animal products (milk, eggs, wool), and T-Cash speedups.
"""

import time
from typing import Dict, Any
from config import SHEDS
from sound_manager import get_sound_manager

class LivestockSystem:
    def __init__(self, state):
        self.state = state

    def feed_shed(self, shed: Dict[str, Any]) -> bool:
        if shed.get('category') != 'shed':
            return False

        shed_type = shed['type']
        shed_info = SHEDS.get(shed_type)
        if not shed_info:
            return False

        if shed.get('fed', False) or shed.get('ready_count', 0) > 0:
            self.state.add_toast("Animals are already eating or products are ready!", color=(230, 200, 80))
            return False

        feed_req = shed_info['feed_type']
        if not self.state.has_items({feed_req: 1}):
            self.state.add_toast(f"Need 1x {feed_req.replace('_', ' ').title()} from Feed Mill!", color=(240, 80, 80))
            get_sound_manager().play('error')
            return False

        self.state.remove_from_barn(feed_req, 1)
        shed['fed'] = True
        shed['feed_time'] = time.time()
        shed['duration'] = shed_info['prod_time']
        self.state.add_toast(f"Fed the {shed_info['animal_name']}s!", color=(120, 220, 120))
        get_sound_manager().play('click')

        if shed_type == 'cow_shed':
            self.state.advance_quest('feed_cows', 1)
        return True

    def collect_products(self, shed: Dict[str, Any]) -> bool:
        ready_count = shed.get('ready_count', 0)
        if ready_count <= 0:
            return False

        shed_type = shed['type']
        shed_info = SHEDS[shed_type]
        product = shed_info['product']

        if not self.state.can_add_to_barn(ready_count):
            self.state.add_toast("Barn is full! Cannot collect.", color=(240, 70, 70))
            get_sound_manager().play('error')
            return False

        self.state.add_to_barn(product, ready_count)
        xp_gain = shed_info['xp'] * ready_count
        self.state.add_xp(xp_gain)
        self.state.add_toast(f"Collected {ready_count}x {shed_info['product_name']}! (+{xp_gain} XP)", color=(250, 230, 80))
        get_sound_manager().play('harvest')

        shed['ready_count'] = 0
        shed['fed'] = False
        return True

    def speedup_shed(self, shed: Dict[str, Any]) -> bool:
        if not shed.get('fed', False):
            return False

        cost = 1  # 1 T-Cash
        if not self.state.spend_tcash(cost):
            return False

        shed_type = shed['type']
        shed_info = SHEDS[shed_type]
        shed['fed'] = False
        shed['ready_count'] = shed_info['animal_count']
        self.state.add_toast(f"{shed_info['product_name']} is ready to collect!", color=(100, 240, 100))
        get_sound_manager().play('speedup')
        return True
