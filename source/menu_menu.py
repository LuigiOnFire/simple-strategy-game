import pygame as p

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width = 0
        self.height = 0
        


    def gen_surface(self):
        self.width = 0
        self.height = 0
        for button in self.buttons:
            # find the dims of the buttons
            width, height = button.find_dims()
            if width >= self.width:
                self.width = width

            self.height += height

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
        
