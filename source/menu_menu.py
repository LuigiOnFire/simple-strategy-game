import pygame as p
import font_util

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width = 0
        self.height = 0
        self.border_width = 0
        self.border_color = p.Color(255, 255, 255, 0)
        self.bg_color = p.Color(255, 255, 255, 0)


    def gen_surface(self):
        inner_width = 0
        inner_height = 0
        button_heights = []
        for button in self.buttons:
            # find the dims of the buttons
            width, height = button.find_dims()
            if width >= inner_width:
                inner_width = width

            button_heights.append(height)

        self.width = inner_width
        self.height = sum(button_heights)

        # generate border rect
        menu_surface = p.Surface((self.width, self.height), p.SRCALPHA)

        border_surface = p.Surface((self.width, self.height), p.SRCALPHA)
        if self.border_color:
            border_surface.fill(self.border_color)

        menu_surface.blit(border_surface, (0, 0))

        # generate button bg
        inner_surface = p.Surface((inner_width, inner_height))
        if self.bg_color:
            inner_surface.fill(self.bg_color)

        menu_surface.blit(inner_surface, (self.border_width, self.border_width))

        # generate each button surface with the correct menu-wide dimensions
        for i, button in enumerate(self.buttons):
            mouse_in = False
            button_surface = button.gen_surface(mouse_in)
            menu_surface.blit(
                button_surface,
                (self.border_width, self.border_width + sum(button_heights[:i]))
            )

        return menu_surface


    def add_button(self, button):
        self.buttons.append(button)


class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, font):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.outline_width = 0
        self.outline_color = p.Color("black")
        self.font = font # font size in encapsulated in this
        self.margin = 2
        # we should have getters and setters but I'm rushing


    def find_dims(self):
        width, height = self.font.size(self.text)
        extra = self.outline_width + self.margin
        return (width + extra, height + extra)


    def gen_surface(self, mosue_in):
        (width, height) = self.find_dims()
        surface = p.Surface((width, height), p.SRCALPHA)
        if self.bg_color:
            surface.fill(self.bg_color)

        font_util.render_w_outline(
            surface,
            self.text,
            self.font,
            self.text_color,
            self.outline_color,
            (self.margin, self.margin),
            self.outline_width
        )

        return surface
