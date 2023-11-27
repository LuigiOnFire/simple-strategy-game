import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width
        self.margin = 2

    def reset_for_button(self):
        self.width = 0
        for button in self.buttons:

            this_width = button.find_width()
            if this_width > self.width:
                self.width = this_width


    def add_button(self, button):
        button.bg_color = self.bg_color
        self.buttons.append(button)
        self.reset_for_button()

    
class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, text_size, font):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.outline_width = 0
        self.text_size = text_size
        self.font = font

    def find_width(self):
        temp_surface = self.font.render(self.text, False, self.text_color, self.bg_color)
        return temp_surface.get_width()
