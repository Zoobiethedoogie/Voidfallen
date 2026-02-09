/**
 * InventoryScene - Phaser scene for displaying and interacting with inventory
 */
class InventoryScene extends Phaser.Scene {
    constructor() {
        super({ key: 'InventoryScene' });
        this.inventory = null;
        this.slotWidth = 80;
        this.slotHeight = 80;
        this.gridPadding = 20;
        this.gridStartX = 100;
        this.gridStartY = 100;
    }

    init(data) {
        this.inventory = data.inventory || new Inventory(5, 3);
    }

    create() {
        // Draw background
        this.drawBackground();

        // Draw grid slots
        this.drawGrid();

        // Draw items
        this.drawItems();

        // Draw UI text
        this.drawUI();

        // Input handling
        this.input.on('pointerdown', (pointer) => {
            this.handleClick(pointer.x, pointer.y);
        });

        // Keyboard shortcuts
        this.input.keyboard.on('keydown-ESC', () => {
            console.log('Closing game');
        });
    }

    drawBackground() {
        // Create gradient background
        const graphics = this.make.graphics({ x: 0, y: 0, add: false });
        graphics.fillStyle(0x1e1e1e, 1);
        graphics.fillRect(0, 0, this.sys.game.config.width, this.sys.game.config.height);
        graphics.generateTexture('bg', this.sys.game.config.width, this.sys.game.config.height);
        graphics.destroy();

        this.add.image(0, 0, 'bg').setOrigin(0, 0);
    }

    drawGrid() {
        const graphics = this.add.graphics();
        graphics.lineStyle(2, 0x646464, 1);
        graphics.fillStyle(0x323232, 0.7);

        for (let row = 0; row < this.inventory.gridHeight; row++) {
            for (let col = 0; col < this.inventory.gridWidth; col++) {
                const x = this.gridStartX + col * (this.slotWidth + this.gridPadding);
                const y = this.gridStartY + row * (this.slotHeight + this.gridPadding);

                // Check if slot is selected
                const isSelected = this.inventory.selectedSlot &&
                    this.inventory.selectedSlot.row === row &&
                    this.inventory.selectedSlot.col === col;

                if (isSelected) {
                    graphics.lineStyle(3, 0xffc800, 1);
                    graphics.fillStyle(0xffc800, 0.2);
                } else {
                    graphics.lineStyle(2, 0x646464, 1);
                    graphics.fillStyle(0x323232, 0.7);
                }

                graphics.fillRect(x, y, this.slotWidth, this.slotHeight);
                graphics.strokeRect(x, y, this.slotWidth, this.slotHeight);

                // Store slot data for click detection
                if (!this.slotRects) this.slotRects = [];
                this.slotRects.push({
                    x, y,
                    width: this.slotWidth,
                    height: this.slotHeight,
                    row, col
                });
            }
        }
    }

    drawItems() {
        const items = this.inventory.getAllItems();

        items.forEach(({ item, row, col }) => {
            const x = this.gridStartX + col * (this.slotWidth + this.gridPadding) + this.slotWidth / 2;
            const y = this.gridStartY + row * (this.slotHeight + this.gridPadding) + this.slotHeight / 2;

            // Draw item name
            this.add.text(x, y, item.name.substring(0, 3).toUpperCase(), {
                font: '16px Arial',
                fill: '#c8c8c8',
                align: 'center'
            }).setOrigin(0.5, 0.5);
        });
    }

    drawUI() {
        const titleY = 40;
        const infoY = 70;
        const bottomY = this.sys.game.config.height - 50;

        // Title
        this.add.text(this.gridStartX, titleY, 'INVENTORY', {
            font: 'bold 32px Arial',
            fill: '#ffffff'
        });

        // Item count
        const itemCount = this.inventory.getItemCount();
        const maxSlots = this.inventory.getMaxSlots();
        this.add.text(this.gridStartX, infoY, `Items: ${itemCount}/${maxSlots}`, {
            font: '24px Arial',
            fill: '#c8c8c8'
        });

        // Selected item info
        if (this.inventory.selectedSlot) {
            const selected = this.inventory.getItem(
                this.inventory.selectedSlot.row,
                this.inventory.selectedSlot.col
            );

            if (selected) {
                this.add.text(this.gridStartX, bottomY, `Selected: ${selected.name}`, {
                    font: '24px Arial',
                    fill: '#64c8ff'
                });
            }
        }

        // Instructions
        this.add.text(this.gridStartX, bottomY + 30, 'Click to select item • ESC to quit', {
            font: '18px Arial',
            fill: '#888888'
        });
    }

    handleClick(clickX, clickY) {
        if (!this.slotRects) return;

        for (const slot of this.slotRects) {
            if (clickX >= slot.x && clickX < slot.x + slot.width &&
                clickY >= slot.y && clickY < slot.y + slot.height) {
                this.inventory.selectSlot(slot.row, slot.col);
                // Refresh the scene
                this.scene.restart({ inventory: this.inventory });
                return;
            }
        }
    }
}
