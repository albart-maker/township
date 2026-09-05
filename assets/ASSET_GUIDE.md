# Township Custom Asset Replacement Guide

You can drop any custom PNG or JPG images and spritesheets into the folders below.
The game will automatically detect and load them. If any asset is missing, it will
seamlessly fall back to its built-in procedural artwork!

## Folder Structure & Recommended Dimensions

### 1. `assets/backgrounds/`
- `menu_bg.png`: Main menu background (1280x720 or 1920x1080)
- `town_terrain.png` or `grass.png`: Ground tile texture (54x54 px or repeating)
- `water.png`: Water canal tile texture (54x54 px)

### 2. `assets/buildings/`
- Size standards (at 54px per grid tile):
  - `cottage.png`: 108x108 px (2x2 tiles)
  - `townhouse.png`: 108x108 px (2x2 tiles)
  - `apartment.png`: 162x108 px (3x2 tiles)
  - `modern_condo.png`: 162x162 px (3x3 tiles)
  - `town_hall.png`: 162x162 px (3x3 tiles)
  - `school.png`: 162x108 px (3x2 tiles)
  - `fire_station.png`: 162x108 px (3x2 tiles)
  - `hospital.png`: 162x162 px (3x3 tiles)
  - `cinema.png`: 162x108 px (3x2 tiles)
  - `feed_mill.png`: 108x108 px (2x2 tiles)
  - `bakery.png`: 162x108 px (3x2 tiles)
  - `dairy_factory.png`: 162x108 px (3x2 tiles)
  - `sugar_mill.png`: 162x108 px (3x2 tiles)
  - `textile_factory.png`: 162x162 px (3x3 tiles)
  - `cow_shed.png`: 162x108 px (3x2 tiles)
  - `chicken_coop.png`: 162x108 px (3x2 tiles)
  - `sheep_pen.png`: 162x108 px (3x2 tiles)
  - `helipad.png`: 162x162 px (3x3 tiles)
  - `helicopter.png`: 84x60 px

### 3. `assets/spritesheets/`
- For animated objects (e.g. factory smoke, spinning windmill, fountains, animals):
  - Spritesheets are arranged horizontally (frames in a row) or as a grid.
  - Example: `bakery_smoke_sheet.png` (4 frames, 32x32 each = 128x32 px)
  - Example: `cow_anim.png` (4 frames = 108x27 px)

### 4. `assets/crops/`
- 3 growth stages per crop (either single images or 3-frame sheet):
  - `wheat_0.png` (sprout), `wheat_1.png` (growing), `wheat_2.png` (ripe)
  - Or `wheat_sheet.png` (3 frames of 54x54 = 162x54 px)
  - Crops: `wheat`, `corn`, `carrot`, `sugarcane`, `cotton`, `strawberry`

### 5. `assets/animals/`
- `cow.png`, `chicken.png`, `sheep.png` (or spritesheets `cow_sheet.png`)

### 6. `assets/characters/`
- 64x64 or 128x128 character avatar portraits:
  - `ernie.png` (Farmer Guide)
  - `mayor.png` (Mayor Bell)
  - `antonio.png` (Chef Antonio)
  - `jenny.png` (Officer Jenny)
  - `sarah.png` (Dr. Sarah)
  - `emma.png` (Emma Florist)

### 7. `assets/icons/`
- 32x32 or 48x48 PNG icons:
  - `coin.png`, `tcash.png`, `xp.png`, `barn.png`, `pop.png`
  - Products: `bread.png`, `cheese.png`, `milk.png`, `egg.png`, `wool.png`, etc.
  - Tools: `nail.png`, `paint.png`, `hammer.png`

### 8. `assets/ui/`
- Custom UI graphics:
  - `button.png`, `panel.png`, `card_bg.png`, `logo.png`
