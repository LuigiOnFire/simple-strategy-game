import pygame as p
import font_util

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right
        self.width = 0 # these refer to the TOTAL width and height of the menu
        self.height = 0
        self.border_width = 0
        self.border_color = p.Color(255, 255, 255, 0)
        self.bg_color = p.Color(255, 255, 255, 0)
        self.menu_surface = None


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
            button.height = height

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

        self.menu_surface = menu_surface

        return menu_surface


    def add_button(self, button):
        self.buttons.append(button)

    def grow_button(self, pos):
        x = pos[0]
        y = pos[1]

        h = 0

        if x < self.border_width or x > self.width - self.border_width:
            return

        if y < self.border_width or y > self.height - self.border_width:
            return

        for button in self.buttons:
            if y < h + button.height:
                mouse_in = True
                button_surface = button.gen_surface(mouse_in)
                self.menu_surface.blit(
                    button_surface,
                    (
                        self.border_width,
                        self.border_width + h
                    )
                )



class MenuButton(): # this will be responsible for making its own surface
    def __init__(self, text, font_style, font_size):
        self.text = text
        self.bg_color = None
        self.text_color = p.Color("white")
        self.outline_width = 0
        self.outline_color = p.Color("black")
        self.font_style = font_style
        self.font_size = font_size
        self.margin = 2
        self.height = 0
        self.text_delta = 4 # how much to expand the text when we hover
        # we should have getters and setters but I'm rushing


    def find_dims(self):
        font = p.font.Font(self.font_style, self.font_size + self.text_delta)
        width, height = font.size(self.text)
        extra = self.outline_width + self.margin
        return (width + extra, height + extra)


    def gen_surface(self, mouse_in):
        (width, height) = self.find_dims()
        surface = p.Surface((width, height), p.SRCALPHA)
        if self.bg_color:
            surface.fill(self.bg_color)

        font_size = self.font_size
        if mouse_in == True:
            font_size += 4

        font = p.font.Font(self.font_style, font_size)

        font_util.render_w_outline(
            surface,
            self.text,
            font,
            self.text_color,
            self.outline_color,
            (self.margin, self.margin),
            self.outline_width
        )

        return surface
