# Voidfallen

A narrative RPG game built with Phaser.js and deployed on GitHub Pages.

## Quick Start

Open `index.html` in a web browser to play. The game features an inventory management system with item slots and selection.

### Features
- **Inventory Grid**: 5x3 grid for managing items
- **Item Selection**: Click any slot to select items
- **Responsive UI**: Adapts to different screen sizes
- **Static Deployment**: Runs entirely in the browser, no backend needed

## Development

### Project Structure
```
Voidfallen/
├── index.html              # Main entry point
├── js/
│   ├── game.js            # Game initialization & config
│   ├── inventory.js       # Inventory & Item classes
│   └── scenes/
│       └── InventoryScene.js  # Inventory UI scene
├── game_assets/
│   ├── GUI/
│   ├── dialogue_boxes/
│   ├── interactive_sprites/
│   └── Items/
├── dialogue/              # Generated dialogue files
└── scripts/               # Python scripts for asset generation
```

### Adding New Features

**To add more items:**
Edit `js/game.js` and add to the `testItems` array:
```javascript
new Item('Item Name', 'item_id')
```

**To modify the grid size:**
In `js/game.js`, change:
```javascript
const inventory = new Inventory(5, 3); // width, height
```

**To add new scenes** (dialogue, exploration):
Create a new scene file in `js/scenes/` and add it to the Phaser config in `game.js`.

## Deploying to GitHub Pages

1. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Select main branch and /root folder

2. **Access your game:**
   - `https://yourusername.github.io/Voidfallen/`

The game runs entirely from static files—no build step required!

## Technologies
- **Phaser 3**: Game framework
- **HTML5/CSS3**: Layout and styling
- **JavaScript**: Game logic
- **GitHub Pages**: Free hosting

## Assets
Game assets are stored in `game_assets/` and can be easily imported into the web version when needed.

## License
[Add your license here]
