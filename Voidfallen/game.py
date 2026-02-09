import os
import sys

# Set up virtual display for headless environments
if os.environ.get('DISPLAY') is None:
    try:
        import pyvirtualdisplay
        display = pyvirtualdisplay.Display(visible=0, size=(1280, 720))
        display.start()
    except ImportError:
        pass

import pygame
import time
import random
import math
import json
from enum import Enum
from typing import List, Dict, Optional, Tuple


# ============================================================================
# GAME CONSTANTS
# ============================================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Asset paths
ASSET_DIR = os.path.join(os.path.dirname(__file__), '..', 'game_assets')
GUI_DIR = os.path.join(ASSET_DIR, 'GUI')
INVENTORY_BG = os.path.join(GUI_DIR, 'Inventory_background.png')
INVENTORY_GRID = os.path.join(GUI_DIR, 'Inventory_grid.png')
SELECTED_ITEM = os.path.join(GUI_DIR, 'Selected_item.png')


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================
class GameState(Enum):
    INVENTORY = 1
    DIALOGUE = 2
    EXPLORATION = 3


class Item:
    """Represents an item in the inventory."""
    def __init__(self, name: str, item_id: str, icon_path: Optional[str] = None):
        self.name = name
        self.item_id = item_id
        self.icon_path = icon_path
        self.icon = None
        if icon_path and os.path.exists(icon_path):
            try:
                self.icon = pygame.image.load(icon_path)
            except:
                pass


class Inventory:
    """Manages items and inventory state."""
    def __init__(self, grid_width: int = 5, grid_height: int = 3):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.items: Dict[Tuple[int, int], Item] = {}  # (row, col) -> Item
        self.selected_slot: Optional[Tuple[int, int]] = None

    def add_item(self, item: Item, row: int, col: int) -> bool:
        """Add item to inventory at specified slot."""
        if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
            if (row, col) not in self.items:
                self.items[(row, col)] = item
                return True
        return False

    def remove_item(self, row: int, col: int) -> Optional[Item]:
        """Remove and return item from slot."""
        return self.items.pop((row, col), None)

    def select_slot(self, row: int, col: int):
        """Select an inventory slot."""
        if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
            self.selected_slot = (row, col)


# ============================================================================
# INVENTORY GUI RENDERER
# ============================================================================
class InventoryGUI:
    """Handles rendering and interaction with the inventory screen."""
    
    def __init__(self, inventory: Inventory, width: int, height: int):
        self.inventory = inventory
        self.screen_width = width
        self.screen_height = height
        
        # Load assets
        self.background = None
        self.grid_image = None
        self.selected_item_image = None
        
        try:
            if os.path.exists(INVENTORY_BG):
                self.background = pygame.image.load(INVENTORY_BG)
                self.background = pygame.transform.scale(self.background, (width, height))
        except Exception as e:
            print(f"Warning: Could not load inventory background: {e}")
        
        try:
            if os.path.exists(INVENTORY_GRID):
                self.grid_image = pygame.image.load(INVENTORY_GRID)
        except Exception as e:
            print(f"Warning: Could not load inventory grid: {e}")
        
        try:
            if os.path.exists(SELECTED_ITEM):
                self.selected_item_image = pygame.image.load(SELECTED_ITEM)
        except Exception as e:
            print(f"Warning: Could not load selected item image: {e}")
        
        # Calculate grid layout
        self.slot_width = 80
        self.slot_height = 80
        self.grid_padding = 20
        self.grid_start_x = 100
        self.grid_start_y = 100
        
        # Font for item names
        self.font_small = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)

    def draw(self, surface: pygame.Surface):
        """Draw the inventory screen."""
        # Draw background
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 30, 30))
        
        # Draw grid slots
        self._draw_grid(surface)
        
        # Draw items in slots
        self._draw_items(surface)
        
        # Draw UI elements
        self._draw_title(surface)

    def _draw_grid(self, surface: pygame.Surface):
        """Draw the inventory grid."""
        for row in range(self.inventory.grid_height):
            for col in range(self.inventory.grid_width):
                x = self.grid_start_x + col * (self.slot_width + self.grid_padding)
                y = self.grid_start_y + row * (self.slot_height + self.grid_padding)
                
                # Draw slot background
                slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)
                
                # Highlight selected slot
                if self.inventory.selected_slot == (row, col):
                    if self.selected_item_image:
                        # Scale selection indicator to fit slot
                        scaled_selection = pygame.transform.scale(
                            self.selected_item_image,
                            (self.slot_width, self.slot_height)
                        )
                        surface.blit(scaled_selection, slot_rect)
                    else:
                        pygame.draw.rect(surface, (255, 200, 0), slot_rect, 3)
                else:
                    pygame.draw.rect(surface, (100, 100, 100), slot_rect, 2)
                    pygame.draw.rect(surface, (50, 50, 50), slot_rect)

    def _draw_items(self, surface: pygame.Surface):
        """Draw items in their inventory slots."""
        for (row, col), item in self.inventory.items.items():
            x = self.grid_start_x + col * (self.slot_width + self.grid_padding)
            y = self.grid_start_y + row * (self.slot_height + self.grid_padding)
            
            # Draw item icon if available
            if item.icon:
                # Scale icon to fit slot with padding
                icon_scaled = pygame.transform.scale(item.icon, (60, 60))
                icon_rect = icon_scaled.get_rect(center=(
                    x + self.slot_width // 2,
                    y + self.slot_height // 2
                ))
                surface.blit(icon_scaled, icon_rect)
            else:
                # Draw placeholder
                label = self.font_small.render(item.name[:3], True, (200, 200, 200))
                label_rect = label.get_rect(center=(
                    x + self.slot_width // 2,
                    y + self.slot_height // 2
                ))
                surface.blit(label, label_rect)

    def _draw_title(self, surface: pygame.Surface):
        """Draw the title and info."""
        title = self.font_large.render("INVENTORY", True, (255, 255, 255))
        surface.blit(title, (self.grid_start_x, 40))
        
        # Item count
        item_count = len(self.inventory.items)
        max_slots = self.inventory.grid_width * self.inventory.grid_height
        count_text = self.font_small.render(
            f"Items: {item_count}/{max_slots}",
            True,
            (200, 200, 200)
        )
        surface.blit(count_text, (self.grid_start_x, 70))
        
        # Selected item info
        if self.inventory.selected_slot and self.inventory.selected_slot in self.inventory.items:
            item = self.inventory.items[self.inventory.selected_slot]
            info_text = self.font_small.render(f"Selected: {item.name}", True, (100, 200, 255))
            surface.blit(info_text, (self.grid_start_x, self.screen_height - 50))

    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on inventory."""
        x, y = pos
        
        # Check which slot was clicked
        for row in range(self.inventory.grid_height):
            for col in range(self.inventory.grid_width):
                slot_x = self.grid_start_x + col * (self.slot_width + self.grid_padding)
                slot_y = self.grid_start_y + row * (self.slot_height + self.grid_padding)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_width, self.slot_height)
                
                if slot_rect.collidepoint(x, y):
                    self.inventory.select_slot(row, col)
                    return


# ============================================================================
# MAIN GAME CLASS
# ============================================================================
class Game:
    """Main game controller."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Voidfallen")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.INVENTORY
        
        # Initialize inventory
        self.inventory = Inventory(grid_width=5, grid_height=3)
        
        # Add some test items
        self._populate_test_inventory()
        
        # Create GUI renderers
        self.inventory_gui = InventoryGUI(self.inventory, WINDOW_WIDTH, WINDOW_HEIGHT)

    def _populate_test_inventory(self):
        """Add test items to the inventory."""
        test_items = [
            Item("Sword", "sword_001"),
            Item("Shield", "shield_001"),
            Item("Potion", "potion_001"),
            Item("Key", "key_001"),
            Item("Scroll", "scroll_001"),
        ]
        
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
        
        for item, (row, col) in zip(test_items, positions):
            self.inventory.add_item(item, row, col)
        
        # Select first item by default
        self.inventory.select_slot(0, 0)

    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == GameState.INVENTORY:
                        self.inventory_gui.handle_click(event.pos)

    def update(self):
        """Update game logic."""
        pass

    def draw(self):
        """Render the current state."""
        if self.state == GameState.INVENTORY:
            self.inventory_gui.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    game = Game()
    game.run()
