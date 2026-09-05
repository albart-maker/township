# Township - Python Edition

A standalone desktop simulation of Playrix's **Township**, built in Python using **Pygame**. 

Experience the complete agricultural and industrial pipeline: cultivate starter farmlands, run factories, feed livestock, fulfill townspeople helicopter orders with Ernie, expand city housing within population limits, upgrade your barn storage, and play the iconic **Match-3 Adventure Event** mini-game!

---

## What's New in This Version

1. **Title / Main Menu Screen**:
   - Clean, festive start screen with **Play**, **Options**, and **Quit**.
2. **Multi-Slot Save & Level Selector**:
   - Choose between **Slot 1**, **Slot 2**, and **Slot 3** with live metadata (current level, town name, coins, T-cash, population, and last saved date).
   - Start new towns or continue existing ones anytime.
3. **Custom Spritesheet & Asset Architecture**:
   - Complete modular folder structure under `assets/` (`backgrounds/`, `buildings/`, `spritesheets/`, `crops/`, `animals/`, `characters/`, `icons/`, `ui/`).
   - Drop in your custom PNG/JPG textures or spritesheet animations—the game automatically detects and loads them!
   - Full procedural fallback ensures everything works out of the box even before custom art is added.
4. **Redesigned Modern UI**:
   - Sleek floating top bar with glassmorphic status pills (Level, Coins, T-Cash, Population, Barn).
   - Floating rounded action dock with hover animations.
   - In-game pause menu with quick save and return-to-title options.

---

## Quick Start

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Dependencies: `pygame>=2.6.0`, `numpy>=1.24.0` (already installed in your environment)

### How to Run
1. **Double-click** `run_game.bat` inside `C:\Users\Rion\.gemini\antigravity\scratch\township`, OR
2. Open PowerShell / Command Prompt and run:
```bash
python main.py
```

### Running Automated Tests
```bash
python test_game_logic.py
```

---

## Menu Navigation & Controls

### Main Menu
- **PLAY**: Opens the Save Slot / Level selection screen.
- **OPTIONS**: Adjust sound effects and view keybindings.
- **QUIT**: Exits the game cleanly.

### Save Slot Screen
- **CONTINUE**: Loads an existing town save in that slot.
- **START NEW TOWN**: Generates a fresh starter town in an empty slot.
- **DEL**: Deletes the selected save slot.
- **< BACK**: Returns to the Main Menu.

### In-Game Controls
| Action | Control |
|---|---|
| **Pan Camera** | `W`, `A`, `S`, `D` or `Arrow Keys`, or **Click & Drag** with Middle/Right Mouse Button |
| **Interact / Select** | **Left Click** on plots, buildings, buttons, and gems |
| **Harvest Crops** | **Left Click** on ripe farm plots (golden wheat / carrots / corn) |
| **Plant Seeds** | **Left Click** on empty soil plot to open the seed wheel |
| **Speed Up Tasks** | **Left Click** on growing crop / active factory to spend 1 T-Cash for instant completion |
| **Pause / In-Game Menu** | `ESC` key or click the **MENU** button in the top right |
| **Quick Save** | `Ctrl + S` or click the **Save** button in the bottom dock |

---

## How to Add Your Custom Spritesheets & Art

See [`assets/ASSET_GUIDE.md`](assets/ASSET_GUIDE.md) for detailed dimensions and naming standards.

Simply drop your files into the appropriate subfolder in `assets/`:
- **`assets/backgrounds/`**: `menu_bg.png` (Title background), `grass.png`, `water.png`.
- **`assets/buildings/`**: `cottage.png`, `townhouse.png`, `bakery.png`, `cow_shed.png`, `town_hall.png`, etc.
- **`assets/spritesheets/`**: Horizontal frame strips for animated buildings, factory smoke, or water fountains.
- **`assets/crops/`**: Growth stage images (`wheat_0.png`, `wheat_1.png`, `wheat_2.png`).
- **`assets/animals/`**: `cow.png`, `chicken.png`, `sheep.png`.
- **`assets/characters/`**: 64x64 or 128x128 avatar portraits (`ernie.png`, `mayor.png`, `antonio.png`, etc.).
- **`assets/icons/`**: `coin.png`, `tcash.png`, `bread.png`, `milk.png`, etc.

The engine uses `AssetLoader` with automatic procedural fallback, meaning you can replace assets one by one at your own pace!

---

## Core Gameplay Features

1. **Agriculture**: Wheat, Corn, Carrots, Sugarcane, Cotton, Strawberries with 3 growth stages.
2. **Livestock**: Feed Mill $\rightarrow$ Cow Shed (Milk), Chicken Coop (Eggs), Sheep Pen (Wool).
3. **Industrial Pipelines**: Bakery (Bread, Cookies, Bagels), Dairy Factory (Cheese, Butter, Yogurt), Sugar Mill, Textile Factory.
4. **City Building & Population**: Houses provide population; Community Buildings (Town Hall, School, Fire Station, Hospital, Cinema) increase your Population Cap.
5. **Helicopter Orders**: Animated helicopter deliveries for Ernie and townspeople.
6. **Barn Storage**: Sell goods and upgrade capacity using Nails, Paint, and Hammers.
7. **Match-3 Adventure Event**: 8x8 gem-matching puzzle event with cascading gravity and barn tool rewards.
8. **Daily Bonus**: 7-day login streak rewards.
