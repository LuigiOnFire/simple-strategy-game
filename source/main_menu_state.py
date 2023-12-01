import random
import pygame as p
import font_util
import menu_menu

class MainMenuState():
    mm_grid_height = 14 # one higher than the screen since we need a bit extra
    mm_grid_width = 9
    mm_grid_layers = 2

    unsized_terrain_tiles = [p.image.load("Sprites/grass_tile.png"),
        p.image.load("Sprites/wheat_tile.png")]

    unsized_unit_tiles = [
        p.image.load("Sprites/b_footsoldier.png"),
        p.image.load("Sprites/r_footsoldier.png")
        ]

    unsized_title = p.image.load("Sprites/title.png")

    def __init__(self, sq_size):
        self.sq_size = sq_size

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

    def setup_top_menu(self):
        self.top_menu = menu_menu.MenuMenu()        
        self.add_top_menu_button("Start Game", self.top_menu)
        self.add_top_menu_button("Quit", self.top_menu)


    def add_top_menu_button(self, btn_text, menu):
        font_style = "Fonts/PressStart2P-Regular.ttf"
        font_size = self.sq_size // 3
        btn = menu_menu.MenuButton(btn_text, font_style, font_size)
        # can change color, bg whatever we want here
        btn.outline_width = 3
        btn.margin = 8
        menu.add_button(btn)

        return btn


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
        screen.blit(self.title, (x, y))


    def draw_submenu(self, screen):
        (x_screen, y_screen) = screen.get_size()
        mouse_pos = p.mouse.get_pos()

        (w, h) = self.top_menu.get_dims()

        x = x_screen / 2 - w / 2
        y = 3 * y_screen / 4 - h / 2

        def within_x(mouse):
            return (x < mouse and mouse < x + w)
        
        def within_y(mouse):
            return (y < mouse and mouse < y + h)

        if within_x(mouse_pos[0]) and within_y(mouse_pos[1]):
            mouse_pos = (mouse_pos[0] - x, mouse_pos[1] - y)
            self.top_menu.grow_button(mouse_pos)
            surface = self.top_menu.menu_surface

        surface = self.top_menu.gen_surface()

        screen.blit(surface, (x, y))


    def reload_surfaces(self):
        self.surfaces[0] = self.surfaces[1]
        self.generate_bg_grid(1)
        self.x_offset_current = 0


    def swap_active_layer(self):
        self.active_layer = 1 - self.active_layer
