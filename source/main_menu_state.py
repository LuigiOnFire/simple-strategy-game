import random
import pygame as p
from team import Team

import menu_menu
from enum import Enum
from player_types import PlayerType

class MainMenuState():
    mm_grid_height = 14 # one higher than the screen since we need a bit extra
    mm_grid_width = 9
    mm_grid_layers = 2

    unsized_terrain_tiles = [
        p.image.load("Sprites/grass_tile.png"),
        p.image.load("Sprites/wheat_tile.png")
        ]

    unsized_unit_tiles = [
        p.image.load("Sprites/b_footsoldier.png"),
        p.image.load("Sprites/r_footsoldier.png")
        ]

    unsized_title = p.image.load("Sprites/title.png")

    start_text = "Start Game"
    quit_text = "Quit"

    def __init__(self, sq_size, screen_width):
        self.sq_size = sq_size
        self.state = State.START_MENU
        self.slide_offset_l = 0
        self.slide_offset_r = screen_width

        self.player_count = 2
        self.player_types = []

        self.bg_terrain_grid = [[[[0] for _ in range(MainMenuState.mm_grid_width)]
                           for _ in range(MainMenuState.mm_grid_height)]
                           for _ in range(MainMenuState.mm_grid_layers)]
        self.bg_unit_grid = [[[[0] for _ in range(MainMenuState.mm_grid_width)]
                         for _ in range(MainMenuState.mm_grid_height)]
                         for _ in range(MainMenuState.mm_grid_layers)]

        self.bg_terrain_tiles = []
        for tile in MainMenuState.unsized_terrain_tiles:
            self.bg_terrain_tiles.append(p.transform.scale(tile, (self.sq_size, self.sq_size)))

        self.bg_unit_tiles = []
        for tile in MainMenuState.unsized_unit_tiles:
            self.bg_unit_tiles.append(p.transform.scale(tile, (self.sq_size, self.sq_size)))

        unsized_title = MainMenuState.unsized_title
        dim = self.sq_size / 16 * (3 / 4)
        self.title = p.transform.scale_by(unsized_title, dim)

        self.active_layer = 0

        self.generate_bg_grid(0)
        self.generate_bg_grid(1)

        self.surfaces = [
            self.grids_to_surface(0),
            self.grids_to_surface(1)
        ]
        self.x_jump = sq_size / 128
        self.x_offset_current = 0

        self.setup_top_menu()

        self.setup_player_setup_menu()

        self.fade = 0


    def setup_top_menu(self):
        self.top_menu = menu_menu.MenuMenu()        
        self.add_top_menu_button(MainMenuState.start_text, self.top_menu)
        self.add_top_menu_button(MainMenuState.quit_text, self.top_menu)


    def add_top_menu_button(self, btn_text, menu):
        font_style = "Fonts/PressStart2P-Regular.ttf"
        font_size = self.sq_size // 3
        btn = menu_menu.MenuButton(btn_text, font_style, font_size)
        # can change color, bg whatever we want here
        btn.outline_width = 3
        btn.margin = 8
        menu.add_button(btn)

        return btn
    

    def setup_player_setup_menu(self):
        self.setup_menu_elements = SetupMenuElems()

        for i in range(self.player_count):
            self.add_player_setup_module(i)

        # add start game button
        self.add_player_setup_start_button()


    def add_player_setup_module(self, i):
        font_style = "Fonts/PressStart2P-Regular.ttf"
        font_size = self.sq_size // 2
        outline_width = 3
        margin = 8
        starting_y = 2

        team = Team(i)

        label_btn_text = f"Player {i}"

        label_btn = menu_menu.StandaloneButton(label_btn_text, font_style, font_size)
        label_btn.text_color = Team.to_color(team)
        label_btn.outline_width = outline_width
        label_btn.margin = margin
        label_btn.x = 3 * self.sq_size  # do something more intelligent here to center it
        label_btn.y = (starting_y + i * 4) * self.sq_size
        label_btn.text_delta = 0
        self.setup_menu_elements.player_setup_labels.append(label_btn)

        values = [PlayerType.HUMAN, PlayerType.COMPUTER]
        symbols = [
                    p.image.load("Sprites/player_human.png"),
                    p.image.load("Sprites/player_computer.png")
                ]
        texts = ["Human", "Computer"]

        p_type_selector = menu_menu.Selector(
            values,
            texts,
            font_style,
            font_size,
            symbols, # this will probably end up being an optional argument
        ) 

        p_type_selector.set_outline_width(3)

        self.setup_menu_elements.player_setup_selectors.append(p_type_selector)


    def add_player_setup_start_button(self):
        btn_text = "Start!"
        font_style = "Fonts/PressStart2P-Regular.ttf"
        font_size = self.sq_size // 2
        btn = menu_menu.StandaloneButton(btn_text, font_style, font_size)
        # can change color, bg whatever we want here
        btn.outline_width = 3
        btn.margin = 8

        self.setup_menu_elements.player_setup_start_btn = btn


    def generate_bg_grid(self, layer):
        terrain_probs = [0.95, 0.05]
        self.bg_terrain_grid[layer] = MainMenuState.generate_grid_layer(terrain_probs)

        unit_probs = [0.95, 0.025, 0.025]
        self.bg_unit_grid[layer] = MainMenuState.generate_grid_layer(unit_probs)


    @staticmethod
    def generate_grid_layer(probs):
        grid_layer = [[[0] for _ in range(MainMenuState.mm_grid_width)] \
                         for _ in range(MainMenuState.mm_grid_height)]

        for y in range(MainMenuState.mm_grid_height):
            for x in range(MainMenuState.mm_grid_width):
                digit = MainMenuState.generate_digit(probs)
                grid_layer[y][x] = digit

        return grid_layer


    @staticmethod
    def generate_digit(probs):
        """Gets a random digit when given a probability list for each index"""
        prob_sum = sum(probs)
        rand = prob_sum * random.random()

        running_sum = 0
        for i, prob in enumerate(probs):
            running_sum += prob
            if rand < running_sum:
                return i


    def grids_to_surface(self, layer):
        bg_surface = p.Surface((self.sq_size * MainMenuState.mm_grid_width, \
                               self.sq_size * MainMenuState.mm_grid_height))

        for y in range(MainMenuState.mm_grid_height):
            for x in range(MainMenuState.mm_grid_width):
                terrain_grid_index = self.bg_terrain_grid[layer][y][x]
                terrain_tile_image = self.bg_terrain_tiles[terrain_grid_index]
                bg_surface.blit(terrain_tile_image, (self.sq_size * x, self.sq_size * y))
                unit_grid_index = self.bg_unit_grid[layer][y][x]

                # 0 is a placeholder on the unit tile array
                if unit_grid_index != 0:
                    unit_grid_index -= 1
                    unit_tile_image = self.bg_unit_tiles[unit_grid_index]
                    bg_surface.blit(unit_tile_image, (self.sq_size * x, self.sq_size * y))

        return bg_surface


    def draw_all(self, screen):
        screen_width = screen.get_width()
        if self.state == State.MOVING_TO_GAME_SETUP:
            self.increment_slide(screen_width)

        display_start_menu = \
            self.state == State.START_MENU or State.MOVING_TO_GAME_SETUP

        display_setup_menu = \
            self.state == State.START_MENU or State.MOVING_TO_GAME_SETUP

        if display_start_menu:
            self.draw_start_menu(screen)

        if display_setup_menu:
            self.draw_setup_menu(screen)


        if self.state == State.AWAITING_GAME:
            if self.fade > 255:
                self.state = State.TO_GAME
                self.fade = 255

            screen_x = screen.get_width()
            screen_y = screen.get_height()

            dark_surface = p.Surface((screen_x, screen_y), p.SRCALPHA)

            fade_step = 8
            shade_color = (0, 0, 0, self.fade)

            dark_surface.fill(shade_color)
            screen.blit(dark_surface, (0, 0))
            self.fade += fade_step


    def increment_slide(self, screen_width):
        slide_step = 12
        self.slide_offset_l += slide_step
        self.slide_offset_r -= slide_step
        if self.slide_offset_l >= screen_width:
            self.slide_offset_l = screen_width
            self.slide_offset_r = 0
            self.state = State.GAME_SETUP


    def draw_start_menu(self, screen):
         # display background
        self.draw_bg(screen)

        # display title
        self.draw_title(screen)

        # display menu text/content
        self.draw_submenu(screen)


    def draw_setup_menu(self, screen):
        (mouse_pos) = p.mouse.get_pos()

        # divide the screen into players + 1 parts
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        grid_lines_y = []
        height_divisions = self.player_count + 1
        
        for i in range(height_divisions + 1):
            grid_lines_y.append((screen_height / height_divisions) * i)

        for player in range(self.player_count):
            label = self.setup_menu_elements.player_setup_labels[player]
            selector = self.setup_menu_elements.player_setup_selectors[player]

            # get the dims of both elements
            (label_width, label_height) = label.find_dims()

            (selector_width, selector_height) = selector.find_dims()

            # find the right starting point for y
            element_height = label_height + selector_height
            cell_height = grid_lines_y[player + 1] - grid_lines_y[player]

            y_offset = cell_height / 2 - element_height / 2
            y = grid_lines_y[player] + y_offset

            label_surface = label.gen_surface(mouse_pos)

            # do the player elems labels
            x = screen_width / 2 - label_width / 2
            x += self.slide_offset_r
            
            label.set_pos(x, y)
            screen.blit(label_surface, (x, y))

            # do the selectors themselves
            width_diff = selector_width - label_width
            x = x - width_diff # we can basically use the same x and y
            y = y + label_height

            selector_surface = selector.gen_surface(mouse_pos)

            selector.set_pos(x, y)
            screen.blit(selector_surface, (x, y))



        # do the start button
        start_button = self.setup_menu_elements.player_setup_start_btn
        
        (btn_width, btn_height) = start_button.find_dims()
        cell_height = grid_lines_y[-2] - grid_lines_y[-1]

        x = screen_width / 2 - btn_width / 2
        x += self.slide_offset_r

        y_offset = cell_height / 2 - btn_height / 2
        y = grid_lines_y[-1] + y_offset
        
        start_button_surface = start_button.gen_surface(mouse_pos)

        start_button.set_pos(x, y)
        screen.blit(start_button_surface, (x, y))


    def draw_bg(self, screen):
        surface_width = self.surfaces[0].get_width()
        screen.blit(self.surfaces[0], (self.x_offset_current, 0))
        screen.blit(self.surfaces[1], (self.x_offset_current + surface_width, 0))

        self.x_offset_current -= self.x_jump
        if -self.x_offset_current >= surface_width:
            self.reload_surfaces()


    def draw_title(self, screen):
        (x_screen, y_screen) = screen.get_size()
        x_sprite = self.title.get_width()
        y_sprite = self.title.get_height()

        x = x_screen / 2 - x_sprite / 2
        y = y_screen / 4 - y_sprite / 2 # will place it in the middle of the top half of the screen

        x -= self.slide_offset_l

        screen.blit(self.title, (x, y))


    def draw_submenu(self, screen):
        (x_screen, y_screen) = screen.get_size()
        (mouse_pos) = p.mouse.get_pos()

        (w, h) = self.top_menu.find_dims()

        x = x_screen / 2 - w / 2
        y = 3 * y_screen / 4 - h / 2

        x -= self.slide_offset_l

        self.top_menu.x = x # should be a function
        self.top_menu.y = y

        surface = self.top_menu.gen_surface(mouse_pos)

        screen.blit(surface, (x, y))


    def reload_surfaces(self):
        self.surfaces[0] = self.surfaces[1]
        self.generate_bg_grid(1)
        self.x_offset_current = 0


    def swap_active_layer(self):
        self.active_layer = 1 - self.active_layer


    def event_handler(self, mouse_pos, events):
        if self.state == State.START_MENU:
            self.top_menu_event_handler(mouse_pos)
        
        if self.state == State.GAME_SETUP:
            self.setup_menu_event_handler(mouse_pos)


    def top_menu_event_handler(self, mouse_pos):
        btn = self.top_menu.is_clicked(mouse_pos)
        if btn:
            if btn.text == MainMenuState.start_text:
                self.setup_game()

            if btn.text == MainMenuState.quit_text:
                self.quit_client()

    def setup_menu_event_handler(self, mouse_pos):
        # check if the mouse is in the position of any of the setup elements
        mouse_x, mouse_y = mouse_pos
        for elem in self.setup_menu_elements.player_setup_selectors:
            elem.is_clicked(mouse_pos)

        start_button = self.setup_menu_elements.player_setup_start_btn
        if start_button.is_clicked(mouse_pos):
            self.start_match()


    def setup_game(self):
        self.state = State.MOVING_TO_GAME_SETUP

    def quit_client(self):
        self.state = State.TURN_OFF

    def reset_menu(self):
        self.state = State.START_MENU
    
    def start_match(self):
        player_types = []
        for p in range(self.player_count):
            val = self.setup_menu_elements.player_setup_selectors[p].get_val()
            player_types.append(val)
        self.player_types = player_types
        self.state = State.AWAITING_GAME


class State(Enum):
    START_MENU = 0
    MOVING_TO_GAME_SETUP = 1
    GAME_SETUP = 2
    AWAITING_GAME = 3
    TO_GAME = 4
    TURN_OFF = 5

class SetupMenuElems():
    def __init__(self):
        self.player_setup_labels = []
        self.player_setup_selectors = []
        self.player_setup_start_btn = None