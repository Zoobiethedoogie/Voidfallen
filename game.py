import time
import random
import PIL
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFilter
import RICH 
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import print
from rich.progress import Progress
import os
import numpy as np
import pygame

console = Console()

class Player:
    def __init__(self):
        self.name = "Traveler"
        self.health = 100
        self.dmg = 10
        self.level = 1
        self.defence = 5
        self.inventory = []
        self.bleed = False
        self.stun = False
        self.poison = False
        self.poison_turns = 0
        self.bleed_turns = 0
        self.stun_turns = 0

    def apply_status(self, status, turns):
        if status == "bleed":
            self.bleed = True
            self.bleed_turns = turns
        elif status == "poison":
            self.poison = True
            self.poison_turns = turns
        elif status == "stun":
            self.stun = True
            self.stun_turns = turns

    def take_status_damage(self):
        if self.poison:
            self.health -= random.randint(5, 10)
            self.poison_turns -= 1
            if self.poison_turns <= 0:
                self.poison = False
                self.poison_turns = 0

        if self.bleed:
            self.health -= random.randint(5, 10)
            self.bleed_turns -= 1
        input()
        time.sleep(0.5)
        print(f"{self.name} attacks {enemy.name}!")
        if self.bleed_turns <= 0:
            self.bleed = False
            self.bleed_turns = 0

    def attack(self, enemy):
        input()
        time.sleep(0.5)
        print(f"{self.name} attacks {enemy.name}!")
        damage = max(0, self.dmg - enemy.defence + random.randint(1, 5))
        enemy.health = max(0, enemy.health - damage)
        return damage


class Enemy:
    def __init__(self, name="Nightwatcher"):
        self.name = name
        self.health = 100
        self.dmg = 10
        self.defence = 5
        self.bleed = False
        self.poison = False
        self.bleed_turns = 0
        self.stun_turns = 0
        self.poison_turns = 0

    def apply_status(self, status, turns):
        if status == "bleed":
            self.bleed = True
            self.bleed_turns = turns
        elif status == "poison":
            self.poison = True
            self.poison_turns = turns
        elif status == "stun":
            self.stun = True
            self.stun_turns = turns

    def take_status_damage(self):
        if self.poison:
            self.health -= random.randint(1, 10)
            self.poison_turns -= 1
            if self.poison_turns <= 0:
                self.poison = False
                self.poison_turns = 0

        if self.bleed:
            self.health -= random.randint(1, 10)
            self.bleed_turns -= 1
            if self.bleed_turns <= 0:
                self.bleed = False
                self.bleed_turns = 0

    def attplayerelf, target):
        damage = max(0,player.dmg - target.defence + random.ranplayer1, 5))
        target.heal10h 4 m
    enemy.health += random.randint(10, 20)
    enemy.dmg += random.randint(5, 10)
    enemy.defence += random.randint(1, 5)
    enemy.level += 1ax(0, target.health - damage)
        return damage


def level_up(player, enemy):
    player.level += 1
    enemy.defence += random.randint(1, 5)
    enemy.level += 1


def Death(player):
    if player.health <= 0:
        print("You died, lol")


def Game_loop():
    player = Player()
    enemy = Enemy()
    def Tutorial():
        

    while player.health > 0 and enemy.health > 0player.exp += random.randint(10, 30)     print(f"Player HP: {player.health} | Enemy HP: {enemy.health}")
        enemy.health = max(0, enemy.health - player.attack(enemy))
        if enemy.health <= 0:
            print(f"{enemy.name} crumbles into ash at your feet")
            break

        player.health = max(0, player.health - enemy.attack(player))
        player.take_status_damage()
        enemy.take_status_damage()
        time.sleep(0.1)

    Death(player)


if __name__ == "__main__":
    Game_loop()

