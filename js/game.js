/**
 * Phaser Game Configuration and Initialization
 */

// Create inventory
const inventory = new Inventory(5, 3);

// Populate with test items
const testItems = [
    new Item('Sword', 'sword_001'),
    new Item('Shield', 'shield_001'),
    new Item('Potion', 'potion_001'),
    new Item('Key', 'key_001'),
    new Item('Scroll', 'scroll_001'),
];

const positions = [
    [0, 0], [0, 1], [0, 2],
    [1, 0], [1, 1]
];

testItems.forEach((item, index) => {
    if (index < positions.length) {
        const [row, col] = positions[index];
        inventory.addItem(item, row, col);
    }
});

// Select first item
inventory.selectSlot(0, 0);

// Phaser configuration
const config = {
    type: Phaser.AUTO,
    width: 1280,
    height: 720,
    parent: 'game-container',
    backgroundColor: '#1a1a1a',
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    scene: InventoryScene,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 },
            debug: false
        }
    }
};

// Create game
const game = new Phaser.Game(config);

// Pass inventory to the scene
game.scene.start('InventoryScene', { inventory });
