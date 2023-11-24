import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width

    def reset_for_button(self):
        self.width = 0
        for button in buttons:
            surface = button.gen_surface()
            this_width = surface.get_width()
            if this_width > self.width:
                self.width = this_width

    def add_button(self, button):
        self.buttons.append(button)
        self.reset_for_button()

class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, text_size):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.has_outline = False
        self.text_size = text_size
