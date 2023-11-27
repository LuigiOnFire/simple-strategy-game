import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width = 0
        self.height = 0
        self.margin = 2


    def gen_surface(self):
        self.width = 0
        self.height = 0
        for button in self.buttons:
            

    def add_button(self, button):
        self.buttons.append(button)


class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, font):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.outline_width = 0
        self.font = font # font size in encapsulated in this
        # we should have getters and setters but I'm rushing


    def find_dims(self):
        temp_surface = self.font.render(self.text, False, self.text_color, self.bg_color)
        return temp_surface.get_width()
