import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width = 0
        self.height = 0
        self.border_width = 0
        self.border_color = None
        self.bg_color = None


    def gen_surface(self):
        inner_width = 0
        inner_height = 0
        for button in self.buttons:
            # find the dims of the buttons
            width, height = button.find_dims()
            if width >= inner_width:
                inner_width = width

            inner_height += height

        self.width += 2 * inner_width
        self.height += 2 * inner_width

        # generate border rect
        menu_surface = p.Surface(self.width, self.height)

        border_surface = p.Surface(self.width, self.height)
        border_surface.fill(self.border_color)
        menu_surface.blit(border_surface)

        inner_surface = p.Surface(inner_width, inner_height)
        inner_surface.fill(self.bg_color)
        menu_surface.blit(inner_surface, (self.border_width, self.border_width))

        # generate button bg

        # generate each button surface with the correct menu-wide dimensions

    def add_button(self, button):
        self.buttons.append(button)


class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, font):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.outline_width = 0
        self.font = font # font size in encapsulated in this
        self.margin = 2
        # we should have getters and setters but I'm rushing


    def find_dims(self):
        width, height = self.font.size(self.text)

        extra = self.outline_width + self.margin        

        return (width + extra, height + extra)
        
