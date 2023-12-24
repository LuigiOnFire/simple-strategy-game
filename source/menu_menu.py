import pygame as p
import font_util

class MenuMenu():
    def __init__(self):
        self.buttons = []
        self.alignment = "l" # l - left, c - center, r - right, NOT IMPLEMENTED
        self.width = 0 # these refer to the TOTAL width and height of the menu
        self.height = 0
        self.border_width = 0
        self.border_color = p.Color(255, 255, 255, 0)
        self.bg_color = p.Color(255, 255, 255, 0)
        self.menu_surface = None
        self.x = 0
        self.y = 0


    def find_dims(self):
        inner_width = 0
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
        return (self.width, self.height)


    def gen_surface(self, mouse_pos):
        (mouse_x, mouse_y) = mouse_pos
        (mouse_x, mouse_y) = (mouse_x - self.x, mouse_y - self.y)
        inner_width = self.width - self.border_width
        inner_height = self.height -self.border_width

        # generate border rect
        menu_surface = p.Surface((self.width, self.height), p.SRCALPHA)

        border_surface = p.Surface((self.width, self.height), p.SRCALPHA)
        if self.border_color:
            border_surface.fill(self.border_color)

        menu_surface.blit(border_surface, (0, 0))

        # generate button bg
        inner_surface = p.Surface((inner_width, inner_height), p.SRCALPHA)
        if self.bg_color:
            inner_surface.fill(self.bg_color)

        menu_surface.blit(inner_surface, (self.border_width, self.border_width))

        current_y = self.border_width

        mouse_in_x = mouse_x > self.border_width and mouse_x < self.width - self.border_width

        # generate each button surface with the correct menu-wide dimensions
        for button in self.buttons:
            mouse_in_y = current_y < mouse_y and mouse_y < current_y + button.height
            mouse_in = mouse_in_y and mouse_in_x

            button_surface = button.gen_surface(mouse_in)
            menu_surface.blit(
                button_surface,
                (self.border_width, self.border_width + current_y)
            )
            current_y += button.height

        self.menu_surface = menu_surface

        return menu_surface


    def add_button(self, button):
        self.buttons.append(button)


    def is_clicked(self, mouse_pos):
        (mouse_x, mouse_y) = mouse_pos
        (mouse_x, mouse_y) = (mouse_x - self.x, mouse_y - self.y)

        mouse_in_x = mouse_x > self.border_width and mouse_x < self.width - self.border_width

        current_y = self.border_width

        for button in self.buttons:
            mouse_in_y = current_y < mouse_y and mouse_y < current_y + button.height
            mouse_in = mouse_in_y and mouse_in_x
            if mouse_in:
                return button
            current_y += button.height

        return None


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
        # add proper getters and setters

        # only used for standalone buttons
        self.x = 0
        self.y = 0


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
        if mouse_in is True:
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


class Selector():
    def __init__(self, values, texts, font_style, font_size, symbols):
        self.values = values
        self.texts = texts
        self.font_style = font_style
        self.font_size = font_size
        self.symbols = symbols

        self._bg_color = None
        self._text_color = p.Color("white")
        self._outline_width = 0
        self._outline_color = p.Color("black")
        self._margin = 2
        self._width = 0
        self._height = 0
        self._bg_color = None

        self._select_index = 0
        self._arrows = None # load default arrow assets once we've made them

        self.x = 0
        self.y = 0

        self.setup_imgs()

    def find_dims(self):
        max_text_width = 0
        my_text_height = 0

        max_text_width, my_text_height = self.get_font_dims()

        width = 2 * self._arrows[0].get_width() + \
            2 * self._margin + \
            max_text_width

        if self.symbols:
            # boldly assuming all symbols will have the same size
            # I will draw them as such
            width += self.symbols[0].get_width() + self._margin

        self._width = width
        self._height = my_text_height

        return (width, my_text_height)

    def gen_surface(self, mouse_in):
        (width, height) = self.find_dims()
        ind = self._select_index
        surface = p.Surface((width, height), p.SRCALPHA)
        if self._bg_color:
            surface.fill(self._bg_color)

        font = p.font.Font(self.font_style, self.font_size)

        x = 0
        # render left arrow
        left_arrow_img = self._arrows[0]
        surface.blit(left_arrow_img, (x, 0))
        x += left_arrow_img.get_width()

        # render symbol (if applicable)
        if self.symbols:
            symb_surf = self.symbols[self._select_index]
            surface.blit(symb_surf, (x, 0))
            x += symb_surf.get_width()

        # render text
        font_util.render_w_outline(
            surface,
            self.texts[ind],
            font,
            self._text_color,
            self._outline_color,
            (x, 0),
            self._outline_width
        )

        # render right arrow
        right_arrow_img = self._arrows[1]
        x = surface.get_width() - right_arrow_img.get_width()
        surface.blit(right_arrow_img, (x, 0))

        return surface


    def set_outline_width(self, width):
        self._outline_width = width


    def setup_imgs(self):
        left_arrow_img = p.image.load("Sprites/selector_left_arrow.png")
        _, target_height = self.get_font_dims() # dependends on our font_size being correct

        left_arrow_img = self.scale_to_height(left_arrow_img, target_height)
        right_arrow_img = p.transform.flip(left_arrow_img, 1, 1)

        self._arrows = [left_arrow_img, right_arrow_img]

        for i, symbol in enumerate(self.symbols):
            self.symbols[i] = self.scale_to_height(symbol, target_height)


    def scale_to_height(self, img, height):
        curr_height = img.get_height()

        scale = height / curr_height
        img = p.transform.scale_by(img, scale)
        return img


    def get_font_dims(self):
        for text in self.texts:
            font = p.font.Font(self.font_style, self.font_size)
            text_width, text_height = font.size(text)
            max_text_width = 0
            if text_width > max_text_width:
                max_text_width = text_width
                my_text_height = text_height

        return max_text_width, my_text_height
