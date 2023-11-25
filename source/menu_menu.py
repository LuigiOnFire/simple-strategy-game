import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width = 0
        self.height = 0
        self.border_width = 1 # just for testing, let's make this 0 later
        self.border_color = p.Color("black")
        self.surface = None
    
    def generate_surface(self):
        if self.width == 0 or self.height == 0:
            self.find_dims()
            self.width += 2 * self.border_width
            self.height += 2 * self.border_width        

    def add_button(self, button):
        self.buttons.append(button)
        self.reset_for_button()

    def find_dims(self):
        self.width = 0
        self.height = 0
        for button in self.buttons:
            surface = button.generate_surface()
            this_width = surface.get_width()
            self.height += surface.get_height()
            if this_width > self.width:
                self.width = this_width    


class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, text_size):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.has_outline = False
        self.text_size = text_size
        self.font = 'PixeloidSans'
        self.surface = None

    def generate_surface(self):
        font = p.font.Font('Fonts/' + self.font + '.ttf', 24)
        self.surface = font.render(self.text, False, self.text_color, self.bg_color)

