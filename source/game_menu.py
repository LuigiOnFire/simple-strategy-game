import pygame as p

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
        self.text = "Foot Soldier 1"
        self.priority = 3

class EndTurnButton(Button):
    def __init__(self):
        self.icon = p.image.load("Sprites/ButtonIcons/EndTurnButtonIcon.png")
        self.text = "End Turn"
        self.priority = 15