import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []

class MenuButton(): # this will be responsible for making its own surface
    def __init__(self):
        self.text = ""
        self.bg_color = None
        self.text_color = p.Color("white")
        self.has_outline = False
        self.text_size = 24
        pass