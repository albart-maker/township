"""
Township - Game Configuration & Data Catalogs
"""

# Screen & Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 54
GRID_WIDTH = 40
GRID_HEIGHT = 40

# Colors (Vibrant Township Palette)
COLOR_BG = (145, 205, 95)            # Lush grass green
COLOR_GRASS_LIGHT = (160, 218, 105)
COLOR_GRASS_DARK = (135, 192, 85)
COLOR_WATER = (72, 172, 224)
COLOR_WATER_DEEP = (45, 142, 198)
COLOR_DIRT = (180, 136, 85)
COLOR_ROAD = (195, 185, 168)
COLOR_ROAD_MARK = (245, 240, 220)

COLOR_PANEL_BG = (252, 248, 235)
COLOR_PANEL_BORDER = (165, 120, 75)
COLOR_PANEL_HEADER = (242, 165, 65)
COLOR_BTN_GREEN = (95, 186, 60)
COLOR_BTN_GREEN_HOVER = (115, 206, 75)
COLOR_BTN_BLUE = (52, 152, 219)
COLOR_BTN_BLUE_HOVER = (70, 170, 235)
COLOR_BTN_ORANGE = (235, 130, 40)
COLOR_BTN_ORANGE_HOVER = (250, 150, 60)
COLOR_BTN_RED = (225, 75, 60)
COLOR_TEXT_DARK = (55, 40, 30)
COLOR_TEXT_MUTED = (120, 105, 95)
COLOR_TEXT_LIGHT = (255, 255, 255)
COLOR_GOLD = (245, 195, 35)
COLOR_TCASH = (75, 180, 95)

# Starter Profile
STARTING_COINS = 350
STARTING_TCASH = 25
STARTING_XP = 0
STARTING_LEVEL = 1
STARTING_BARN_CAPACITY = 60
STARTING_POPULATION = 0
STARTING_POPULATION_CAP = 30

# Level XP thresholds
LEVEL_THRESHOLDS = [
    0,      # Lvl 1
    50,     # Lvl 2
    140,    # Lvl 3
    300,    # Lvl 4
    580,    # Lvl 5
    1000,   # Lvl 6
    1600,   # Lvl 7
    2400,   # Lvl 8
    3500,   # Lvl 9
    5000,   # Lvl 10
]

def get_xp_for_level(lvl: int) -> int:
    if lvl - 1 < len(LEVEL_THRESHOLDS):
        return LEVEL_THRESHOLDS[lvl - 1]
    return LEVEL_THRESHOLDS[-1] + (lvl - len(LEVEL_THRESHOLDS)) * 2000

# CROPS DEFINITION
CROPS = {
    'wheat': {
        'name': 'Wheat',
        'cost': 0,
        'grow_time': 3.0,     # 3 seconds (snappy & casual)
        'xp': 1,
        'sell_price': 1,
        'min_level': 1,
        'color': (235, 205, 80)
    },
    'corn': {
        'name': 'Corn',
        'cost': 1,
        'grow_time': 8.0,
        'xp': 2,
        'sell_price': 3,
        'min_level': 2,
        'color': (245, 185, 40)
    },
    'carrot': {
        'name': 'Carrot',
        'cost': 2,
        'grow_time': 15.0,
        'xp': 3,
        'sell_price': 5,
        'min_level': 3,
        'color': (245, 120, 35)
    },
    'sugarcane': {
        'name': 'Sugarcane',
        'cost': 3,
        'grow_time': 25.0,
        'xp': 4,
        'sell_price': 7,
        'min_level': 4,
        'color': (140, 200, 90)
    },
    'cotton': {
        'name': 'Cotton',
        'cost': 4,
        'grow_time': 40.0,
        'xp': 5,
        'sell_price': 10,
        'min_level': 5,
        'color': (240, 240, 245)
    },
    'strawberry': {
        'name': 'Strawberry',
        'cost': 6,
        'grow_time': 60.0,
        'xp': 7,
        'sell_price': 15,
        'min_level': 6,
        'color': (235, 60, 75)
    }
}

# ANIMAL FEEDS (Produced in Feed Mill)
FEEDS = {
    'cow_feed': {
        'name': 'Cow Feed',
        'ingredients': {'wheat': 2},
        'prod_time': 6.0,
        'yield_qty': 2,
        'xp': 2,
        'sell_price': 2,
        'min_level': 1
    },
    'chicken_feed': {
        'name': 'Chicken Feed',
        'ingredients': {'wheat': 1, 'corn': 1},
        'prod_time': 10.0,
        'yield_qty': 2,
        'xp': 3,
        'sell_price': 3,
        'min_level': 2
    },
    'sheep_feed': {
        'name': 'Sheep Feed',
        'ingredients': {'corn': 1, 'carrot': 1},
        'prod_time': 16.0,
        'yield_qty': 2,
        'xp': 4,
        'sell_price': 5,
        'min_level': 4
    },
    'pig_feed': {
        'name': 'Pig Feed',
        'ingredients': {'corn': 1, 'carrot': 1},
        'prod_time': 12.0,
        'yield_qty': 2,
        'xp': 3,
        'sell_price': 4,
        'min_level': 3
    }
}

# LIVESTOCK SHEDS
SHEDS = {
    'cow_shed': {
        'name': 'Cow Shed',
        'cost': 60,
        'min_level': 1,
        'size': (3, 2),
        'animal_name': 'Cow',
        'animal_count': 3,
        'feed_type': 'cow_feed',
        'product': 'milk',
        'prod_time': 12.0,
        'xp': 3,
        'product_name': 'Milk',
        'sell_price': 5
    },
    'chicken_coop': {
        'name': 'Chicken Coop',
        'cost': 120,
        'min_level': 2,
        'size': (3, 2),
        'animal_name': 'Chicken',
        'animal_count': 4,
        'feed_type': 'chicken_feed',
        'product': 'egg',
        'prod_time': 15.0,
        'xp': 4,
        'product_name': 'Egg',
        'sell_price': 6
    },
    'pig_pen': {
        'name': 'Pig Pen',
        'cost': 180,
        'min_level': 3,
        'size': (3, 2),
        'animal_name': 'Pig',
        'animal_count': 3,
        'feed_type': 'pig_feed',
        'product': 'bacon',
        'prod_time': 18.0,
        'xp': 5,
        'product_name': 'Bacon',
        'sell_price': 9
    },
    'sheep_pen': {
        'name': 'Sheep Pen',
        'cost': 240,
        'min_level': 4,
        'size': (3, 2),
        'animal_name': 'Sheep',
        'animal_count': 3,
        'feed_type': 'sheep_feed',
        'product': 'wool',
        'prod_time': 24.0,
        'xp': 6,
        'product_name': 'Wool',
        'sell_price': 12
    }
}

# FACTORY RECIPES
FACTORIES = {
    'feed_mill': {
        'name': 'Feed Mill',
        'cost': 30,
        'min_level': 1,
        'size': (2, 2),
        'recipes': ['cow_feed', 'chicken_feed', 'pig_feed', 'sheep_feed']
    },
    'bakery': {
        'name': 'Bakery',
        'cost': 90,
        'min_level': 1,
        'size': (3, 2),
        'recipes': ['bread', 'cookie', 'bagel']
    },
    'dairy_factory': {
        'name': 'Dairy Factory',
        'cost': 160,
        'min_level': 2,
        'size': (3, 2),
        'recipes': ['cheese', 'butter', 'yogurt']
    },
    'sugar_mill': {
        'name': 'Sugar Mill',
        'cost': 200,
        'min_level': 3,
        'size': (3, 2),
        'recipes': ['sugar', 'syrup']
    },
    'textile_factory': {
        'name': 'Textile Factory',
        'cost': 300,
        'min_level': 5,
        'size': (3, 3),
        'recipes': ['fabric', 'yarn']
    }
}

RECIPES = {
    # Bakery
    'bread': {
        'name': 'Bread',
        'ingredients': {'wheat': 2},
        'prod_time': 10.0,
        'yield_qty': 1,
        'xp': 3,
        'sell_price': 6,
        'min_level': 1
    },
    'cookie': {
        'name': 'Cookie',
        'ingredients': {'wheat': 2, 'sugar': 1},
        'prod_time': 18.0,
        'yield_qty': 1,
        'xp': 6,
        'sell_price': 16,
        'min_level': 3
    },
    'bagel': {
        'name': 'Bagel',
        'ingredients': {'wheat': 2, 'egg': 1},
        'prod_time': 24.0,
        'yield_qty': 1,
        'xp': 8,
        'sell_price': 22,
        'min_level': 2
    },
    # Dairy
    'cheese': {
        'name': 'Cheese',
        'ingredients': {'milk': 2},
        'prod_time': 14.0,
        'yield_qty': 1,
        'xp': 5,
        'sell_price': 14,
        'min_level': 2
    },
    'butter': {
        'name': 'Butter',
        'ingredients': {'milk': 1},
        'prod_time': 10.0,
        'yield_qty': 1,
        'xp': 4,
        'sell_price': 9,
        'min_level': 2
    },
    'yogurt': {
        'name': 'Yogurt',
        'ingredients': {'milk': 2, 'strawberry': 1},
        'prod_time': 28.0,
        'yield_qty': 1,
        'xp': 10,
        'sell_price': 32,
        'min_level': 6
    },
    # Sugar
    'sugar': {
        'name': 'Sugar',
        'ingredients': {'sugarcane': 2},
        'prod_time': 12.0,
        'yield_qty': 1,
        'xp': 4,
        'sell_price': 12,
        'min_level': 3
    },
    'syrup': {
        'name': 'Syrup',
        'ingredients': {'sugarcane': 3},
        'prod_time': 20.0,
        'yield_qty': 1,
        'xp': 7,
        'sell_price': 24,
        'min_level': 4
    },
    # Textile
    'fabric': {
        'name': 'Fabric',
        'ingredients': {'cotton': 2},
        'prod_time': 18.0,
        'yield_qty': 1,
        'xp': 7,
        'sell_price': 22,
        'min_level': 5
    },
    'yarn': {
        'name': 'Yarn',
        'ingredients': {'wool': 2},
        'prod_time': 24.0,
        'yield_qty': 1,
        'xp': 9,
        'sell_price': 30,
        'min_level': 5
    }
}

ALL_RECIPES = {**RECIPES, **FEEDS}

# HOUSES (Gives Population, Requires Pop Cap)
HOUSES = {
    'cottage': {
        'name': 'Cottage',
        'cost': 45,
        'pop': 5,
        'min_level': 1,
        'size': (2, 2),
        'xp': 10
    },
    'townhouse': {
        'name': 'Townhouse',
        'cost': 125,
        'pop': 15,
        'min_level': 2,
        'size': (2, 2),
        'xp': 25
    },
    'apartment': {
        'name': 'Apartment Block',
        'cost': 320,
        'pop': 35,
        'min_level': 4,
        'size': (3, 2),
        'xp': 60
    },
    'modern_condo': {
        'name': 'Modern Condo',
        'cost': 750,
        'pop': 80,
        'min_level': 6,
        'size': (3, 3),
        'xp': 140
    }
}

# COMMUNITY BUILDINGS (Increases Population Cap)
COMMUNITY_BUILDINGS = {
    'town_hall': {
        'name': 'Town Hall',
        'cost': 100,
        'pop_cap': 30,
        'min_level': 1,
        'size': (3, 3),
        'xp': 30
    },
    'school': {
        'name': 'School',
        'cost': 220,
        'pop_cap': 45,
        'min_level': 2,
        'size': (3, 2),
        'xp': 50
    },
    'fire_station': {
        'name': 'Fire Station',
        'cost': 450,
        'pop_cap': 65,
        'min_level': 3,
        'size': (3, 2),
        'xp': 90
    },
    'hospital': {
        'name': 'Hospital',
        'cost': 750,
        'pop_cap': 95,
        'min_level': 5,
        'size': (3, 3),
        'xp': 150
    },
    'cinema': {
        'name': 'Cinema',
        'cost': 1150,
        'pop_cap': 130,
        'min_level': 6,
        'size': (3, 2),
        'xp': 220
    }
}

# DECORATIONS
DECORATIONS = {
    'park_tree': {
        'name': 'Oak Tree',
        'cost': 15,
        'min_level': 1,
        'size': (1, 1),
        'xp': 3
    },
    'pine_tree': {
        'name': 'Pine Tree',
        'cost': 20,
        'min_level': 1,
        'size': (1, 1),
        'xp': 4
    },
    'flower_bed': {
        'name': 'Flower Bed',
        'cost': 25,
        'min_level': 1,
        'size': (1, 1),
        'xp': 5
    },
    'fountain': {
        'name': 'Town Fountain',
        'cost': 120,
        'min_level': 2,
        'size': (2, 2),
        'xp': 25
    },
    'street_lamp': {
        'name': 'Victorian Lamp',
        'cost': 30,
        'min_level': 1,
        'size': (1, 1),
        'xp': 6
    },
    'gazebo': {
        'name': 'Park Gazebo',
        'cost': 180,
        'min_level': 3,
        'size': (2, 2),
        'xp': 35
    }
}

# ROADS & PAVING
ROADS = {
    'road_dirt': {'name': 'Dirt Path', 'cost': 2, 'size': (1, 1)},
    'road_paved': {'name': 'Stone Pavement', 'cost': 4, 'size': (1, 1)},
    'water_canal': {'name': 'Water Canal', 'cost': 8, 'size': (1, 1)}
}

# SPECIAL BUILDINGS
SPECIAL_BUILDINGS = {
    'field_plot': {
        'name': 'Farm Plot',
        'cost': 10,
        'min_level': 1,
        'size': (1, 1),
        'xp': 2
    },
    'helipad': {
        'name': 'Helipad',
        'cost': 0,
        'min_level': 1,
        'size': (3, 3),
        'xp': 0
    }
}

# BARN UPGRADE TOOLS & BASE DATA
BARN_TOOLS = ['nail', 'paint', 'hammer']
BARN_TOOL_NAMES = {
    'nail': 'Construction Nails',
    'paint': 'Red Barn Paint',
    'hammer': 'Carpentry Hammer'
}

# ITEM NAMES & SELL VALUES LOOKUP
ALL_ITEMS = {
    # Crops
    'wheat': {'name': 'Wheat', 'sell': 1},
    'corn': {'name': 'Corn', 'sell': 3},
    'carrot': {'name': 'Carrot', 'sell': 5},
    'sugarcane': {'name': 'Sugarcane', 'sell': 7},
    'cotton': {'name': 'Cotton', 'sell': 10},
    'strawberry': {'name': 'Strawberry', 'sell': 15},
    # Animal Products
    'milk': {'name': 'Fresh Milk', 'sell': 5},
    'egg': {'name': 'Farm Egg', 'sell': 6},
    'wool': {'name': 'Soft Wool', 'sell': 12},
    'bacon': {'name': 'Crispy Bacon', 'sell': 10},
    # Feeds
    'cow_feed': {'name': 'Cow Feed', 'sell': 2},
    'chicken_feed': {'name': 'Chicken Feed', 'sell': 3},
    'pig_feed': {'name': 'Pig Feed', 'sell': 4},
    'sheep_feed': {'name': 'Sheep Feed', 'sell': 5},
    # Manufactured
    'bread': {'name': 'Bread', 'sell': 6},
    'cookie': {'name': 'Cookie', 'sell': 16},
    'bagel': {'name': 'Bagel', 'sell': 22},
    'cheese': {'name': 'Cheese', 'sell': 14},
    'butter': {'name': 'Butter', 'sell': 9},
    'yogurt': {'name': 'Yogurt', 'sell': 32},
    'sugar': {'name': 'Sugar', 'sell': 12},
    'syrup': {'name': 'Syrup', 'sell': 24},
    'fabric': {'name': 'Fabric', 'sell': 22},
    'yarn': {'name': 'Yarn', 'sell': 30},
    # Tools
    'nail': {'name': 'Nails', 'sell': 15},
    'paint': {'name': 'Red Paint', 'sell': 15},
    'hammer': {'name': 'Hammer', 'sell': 15},
}

# Characters for Helicopter Orders
TOWNSPEOPLE = [
    {'id': 'ernie', 'name': 'Ernie', 'role': 'Farmer Guide', 'phrase': 'Good day, neighbor! My farm needs some fresh goods!'},
    {'id': 'mayor', 'name': 'Mayor Bell', 'role': 'Town Mayor', 'phrase': 'Our townspeople need supplies for the community festival!'},
    {'id': 'antonio', 'name': 'Chef Antonio', 'role': 'Head Chef', 'phrase': 'Mamma mia! My kitchen is missing fresh ingredients!'},
    {'id': 'jenny', 'name': 'Officer Jenny', 'role': 'Police Chief', 'phrase': 'Keeping the town safe builds up quite an appetite!'},
    {'id': 'sarah', 'name': 'Dr. Sarah', 'role': 'Town Physician', 'phrase': 'Fresh organic produce keeps the whole town healthy!'},
    {'id': 'emma', 'name': 'Emma', 'role': 'Local Florist', 'phrase': 'Decorating town parks requires great snacks for our crew!'}
]

# Daily Streak Rewards
DAILY_REWARDS = [
    {'day': 1, 'coins': 50, 'tcash': 1, 'tool': None},
    {'day': 2, 'coins': 100, 'tcash': 2, 'tool': 'nail'},
    {'day': 3, 'coins': 200, 'tcash': 3, 'tool': 'paint'},
    {'day': 4, 'coins': 350, 'tcash': 4, 'tool': 'hammer'},
    {'day': 5, 'coins': 500, 'tcash': 5, 'tool': 'nail'},
    {'day': 6, 'coins': 750, 'tcash': 6, 'tool': 'paint'},
    {'day': 7, 'coins': 1200, 'tcash': 15, 'tool': 'hammer'},
]
