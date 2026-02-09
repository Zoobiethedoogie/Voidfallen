/**
 * Item class - Represents an item in the inventory
 */
class Item {
    constructor(name, itemId, iconPath = null) {
        this.name = name;
        this.itemId = itemId;
        this.iconPath = iconPath;
    }
}

/**
 * Inventory class - Manages items in a grid
 */
class Inventory {
    constructor(gridWidth = 5, gridHeight = 3) {
        this.gridWidth = gridWidth;
        this.gridHeight = gridHeight;
        this.items = new Map(); // "(row,col)" -> Item
        this.selectedSlot = null;
    }

    /**
     * Add item to inventory at specified slot
     */
    addItem(item, row, col) {
        if (row >= 0 && row < this.gridHeight && col >= 0 && col < this.gridWidth) {
            const key = `${row},${col}`;
            if (!this.items.has(key)) {
                this.items.set(key, item);
                return true;
            }
        }
        return false;
    }

    /**
     * Remove and return item from slot
     */
    removeItem(row, col) {
        const key = `${row},${col}`;
        const item = this.items.get(key);
        if (item) {
            this.items.delete(key);
            return item;
        }
        return null;
    }

    /**
     * Get item at slot
     */
    getItem(row, col) {
        const key = `${row},${col}`;
        return this.items.get(key) || null;
    }

    /**
     * Select an inventory slot
     */
    selectSlot(row, col) {
        if (row >= 0 && row < this.gridHeight && col >= 0 && col < this.gridWidth) {
            this.selectedSlot = { row, col };
            return true;
        }
        return false;
    }

    /**
     * Get all items
     */
    getAllItems() {
        return Array.from(this.items.entries()).map(([key, item]) => ({
            key,
            item,
            row: parseInt(key.split(',')[0]),
            col: parseInt(key.split(',')[1])
        }));
    }

    /**
     * Get item count
     */
    getItemCount() {
        return this.items.size;
    }

    /**
     * Get max slots
     */
    getMaxSlots() {
        return this.gridWidth * this.gridHeight;
    }
}
