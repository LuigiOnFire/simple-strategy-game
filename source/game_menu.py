import pygame as p
import units

class GameMenu():
    def __init__(self):
        self.buttons = []
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0

class Button():
    icon = None
    text = None
    priority = None
    x = 0
    y = 0
    height = 0
    width = 0


# attack
class AttackButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/AttackButtonIcon.png")
        self.text = "Attack"
        self.priority = 0

# wait
class WaitButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/WaitButtonIcon.png")
        self.text = "Wait"
        self.priority = 1

# cancel
class CancelButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/CancelButtonIcon.png")
        self.text = "Cancel"
        self.priority = 2

class BuyFootSoldierButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/AttackButtonIcon.png")
        self.text = f"Foot Soldier {units.FootSoldier.cost}"
        self.priority = 3


class BuyLancerButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/BuyLancer.png")
        self.text = f"Lancer {units.Lancer.cost}"
        self.priority = 4


class BuyArmoredSoldierButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/BuyArmored.png")
        self.text = f"Armored Soldier {units.Armored.cost}"
        self.priority = 5

class BuyArcherButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/BuyArcher.png")
        self.text = f"Archer {units.Archer.cost}"
        self.priority = 6


class BuyKnightButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/BuyKnight.png")
        self.text = f"Knight {units.Knight.cost}"
        self.priority = 7

class EndTurnButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/EndTurnButtonIcon.png")
        self.text = "End Turn"
        self.priority = 15