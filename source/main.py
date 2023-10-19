"""Entry point, handles main input/output loop for game"""
import math

import pygame as p
import anim
import engine

SCALE = 4
MAP_X = 8
MAP_Y = 11
SQ_SIZE = 16*SCALE
WALLSIZE = 8*SCALE
MAP_WIDTH = MAP_X * SQ_SIZE
MAP_HEIGHT = MAP_Y * SQ_SIZE + WALLSIZE * 2
MENU_WIDTH = MAP_WIDTH / 2.2
WIDTH = 128 * SCALE
HEIGHT = 192 * SCALE
MAX_FPS = 30
IMAGES = {}
BOARDART = p.image.load("Sprites/field.png")
BOARDART = p.transform.scale(BOARDART, (MAP_WIDTH, MAP_HEIGHT))

def load_images():
    """Loads the image sprites for each unit type"""
    teams = ["b", "r"]
    unit_types = ["footsoldier"]
    for team in teams:
        for unit_type in unit_types:
            IMAGES[team, unit_type] = p.image.load(
                "Sprites/" + team + "_" + unit_type + ".png")
            IMAGES[team, unit_type] = p.transform.scale(
                IMAGES[team, unit_type], (SQ_SIZE, SQ_SIZE))


def main():
    """Governs main input/rendering loop"""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    load_images()
    running = True
    gs.setup_still_anims()
    # this_unit = EngineScript.ArmyUnit(kwargs)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                target = p.mouse.get_pos()
                if mouse_in_menu(target, gs.menu):
                    menu_event_handler(target, gs)

                else:
                    map_event_handler(target, gs)

            elif e.type == p.KEYDOWN:  # later move this to menu
                if e.key == p.K_z:
                    gs.undoMove()

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def map_event_handler(mouse_pos, gs):
    """Gets mouse clicks on the map"""
    phase = gs.phase
    if phase in {
            engine.Phase.ANIMATING_MOVE,
            engine.Phase.AWAITING_MENU_INSTRUCTION,
            engine.Phase.ANIMATING_INSTRUCTION,
            engine.Phase.TURN_TRANSITION}:
        return

    selected_square = get_the_row_and_col(mouse_pos)
    if phase == engine.Phase.AWAITING_UNIT_SELECTION:
        select_space(selected_square, gs)  # also need to support buying

    elif phase == engine.Phase.UNIT_SELECTED:
        if selected_square in gs.valid_moves:
            prep_unit_move(selected_square, gs)

    elif phase == engine.Phase.SELECTING_TARGET:
        if selected_square in gs.found_hostiles:
            (sel_x, sel_y) = gs.selected_square
            (ref_x, ref_y) = gs.dest_square
            gs.map[ref_y][ref_x] = gs.selected_unit_index
            gs.map[sel_y][sel_x] = -1
            
            prep_unit_attack(selected_square, gs)


def menu_event_handler(mouse_pos, gs):
    """Handles clicks on the menu"""
    for button in gs.menu.buttons:
        if mouse_in_button(mouse_pos, button):
            if isinstance(button, engine.game_menu.CancelButton):
                if gs.selected_unit:
                    gs.selected_unit.anim = anim.StillAnim()

                gs.phase = engine.Phase.AWAITING_UNIT_SELECTION
                gs.menu = engine.game_menu.GameMenu()

            elif isinstance(button, engine.game_menu.WaitButton):
                (sel_x, sel_y) = gs.selected_square
                (ref_x, ref_y) = gs.dest_square
                gs.map[ref_y][ref_x] = gs.selected_unit_index
                gs.map[sel_y][sel_x] = -1
                gs.selected_unit.is_active = False
                gs.phase = engine.Phase.AWAITING_UNIT_SELECTION
                gs.menu = engine.game_menu.GameMenu()
                gs.reset_select()

            elif isinstance(button, engine.game_menu.EndTurnButton):
                gs.transition_to_turn_transition()
                gs.menu = engine.game_menu.GameMenu()

            elif isinstance(button, engine.game_menu.AttackButton):
                # first, confirm the move
                gs.transition_to_selecting_target()

            # regardless of what button was pushed it's good to check
            check_end_turn(gs)


def highlight_spaces(screen, gs):
    """Highlightes spaces when a unit is selected"""    
    s = p.Surface((SQ_SIZE - SCALE / 2, SQ_SIZE - SCALE / 2))
    s.set_alpha(100)  # 255 is opaque
    s.fill(p.Color('blue'))
    gs.update_valid_moves(gs.selected_unit)
    for square in gs.valid_moves:
        x = square[0]
        y = square[1]
        screen.blit(s, (x*SQ_SIZE, y*SQ_SIZE + WALLSIZE))

def highlight_enemies(screen, gs):
    """Highlights squares that contain enemies"""
    s = p.Surface((SQ_SIZE - SCALE / 2, SQ_SIZE - SCALE /2))
    s.set_alpha(128) # 255 is opaque
    s.fill(p.Color('red'))
    gs.find_in_range_hostiles()
    for square in gs.found_hostiles:
        x = square[0]
        y = square[1]
        screen.blit(s, (x*SQ_SIZE, y*SQ_SIZE + WALLSIZE))

def select_space(selected_square, gs):
    """Gets a selected space once it's been clicked on"""
    if gs.square_is_occupied(selected_square):
        unit_index = gs.map[selected_square[1]][selected_square[0]]
        unit = gs.unit_list[unit_index]

        if unit.is_active and gs.unit_has_active_team(unit):
            gs.selected_unit = gs.unit_list[unit_index]
            gs.selected_unit_index = unit_index
            gs.selected_square = selected_square
            gs.phase = engine.Phase.UNIT_SELECTED

        else:
            gs.selected_square = selected_square
            gs.dest_square = selected_square
            gs.prep_end_menu()

    elif gs.square_can_produce(selected_square):
        gs.selected_square = selected_square
        gs.phase = engine.Phase.AWAITING_MENU_INSTRUCTION

    else:
        gs.selected_square = selected_square
        gs.dest_square = selected_square
        gs.prep_end_menu()


def draw_game_state(screen, gs):
    if gs.phase == engine.Phase.AWAITING_UNIT_SELECTION:
        display_map(screen)
        display_units(screen, gs)

    elif gs.phase == engine.Phase.UNIT_SELECTED:
        display_map(screen)
        highlight_spaces(screen, gs)
        display_units(screen, gs)

    elif gs.phase == engine.Phase.ANIMATING_MOVE:
        display_map(screen)
        display_units(screen, gs)

    elif gs.phase == engine.Phase.AWAITING_MENU_INSTRUCTION:
        display_map(screen)
        display_units(screen, gs)
        display_menu(screen, gs)

    elif gs.phase == engine.Phase.SELECTING_TARGET:
        display_map(screen)
        highlight_enemies(screen, gs)
        display_units(screen, gs)

    elif gs.phase == engine.Phase.ANIMATING_INSTRUCTION:
        display_map(screen)
        display_units(screen, gs)

    elif gs.phase == engine.Phase.TURN_TRANSITION:
        display_map(screen)
        display_units(screen, gs)
        animate_turn_banner(screen, gs)


def display_map(screen):
    screen.blit(BOARDART, p.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))


def display_menu(screen, gs):
    BORDER_PADDING = 1 * SCALE
    BUTTON_PADDING = 2 * SCALE
    ELEMENT_HEIGHT = 6 * SCALE
    ELEMENT_SPACING = 2 * SCALE  # spacing between the icon and the button
    icon_width = ELEMENT_HEIGHT
    BUTTON_HEIGHT = ELEMENT_HEIGHT + 2 * BUTTON_PADDING

    border_color = p.Color('gray25')
    body_color = p.Color('gray50')

    # maybe move MENU_WIDTH here
    menu = gs.menu
    right_side = True
    top_side = True
    (dest_square_x, dest_square_y) = gs.dest_square
    if gs.selected_square != None:  # later TODO this should probably be an exception
        if dest_square_x >= MAP_X // 2:
            right_side = False
        if dest_square_y <= MAP_Y // 2:
            top_side = False

    button_count = (len(gs.menu.buttons))
    menu.width = MENU_WIDTH + 2 * BORDER_PADDING
    menu_height = (button_count * BUTTON_HEIGHT)
    menu.height = menu_height + 2 * BORDER_PADDING
    (dest_coords_x, dest_coords_y) = get_square_coords(gs.dest_square)

    if right_side:
        menu.x = dest_coords_x + SQ_SIZE
    else:
        menu.x = dest_coords_x - menu.width

    if top_side:
        menu.y = dest_coords_y - menu.height
    else:
        menu.y = dest_coords_y + SQ_SIZE

    border_position = (menu.x, menu.y)

    body_top_left_x = menu.x + BORDER_PADDING
    body_top_left_y = menu.y + BORDER_PADDING
    body_position = (body_top_left_x, body_top_left_y)

    # display the border
    border_surface = p.Surface((menu.width, menu.height))
    border_surface.fill(border_color)
    screen.blit(border_surface, border_position)

    # display the body
    body_surface = p.Surface((MENU_WIDTH, menu_height))
    body_surface.fill(body_color)

    mouse_pos = p.mouse.get_pos()
    screen.blit(body_surface, body_position)

    for i in range(0, len(gs.menu.buttons)):
        button = gs.menu.buttons[i]

        button.x = body_top_left_x
        button.width = MENU_WIDTH

        button.y = body_top_left_y + (i * BUTTON_HEIGHT)
        button.height = BUTTON_HEIGHT

        button_color = None
        if mouse_in_button(mouse_pos, button):
            button_color = p.Color("Gray38")
        else:
            button_color = body_color

        button_surface = p.Surface((button.width, button.height))
        button_surface.fill(button_color)
        screen.blit(button_surface, (button.x, button.y))

        icon_image = button.icon
        icon_size = (ELEMENT_HEIGHT, ELEMENT_HEIGHT)
        icon_location = (body_top_left_x + BUTTON_PADDING,
                         button.y + BUTTON_PADDING)
        icon_image = p.transform.scale(icon_image, icon_size)

        screen.blit(icon_image, icon_location)

        font = p.font.Font('Fonts/PressStart2P-Regular.ttf', 24)
        font_color = p.Color(255, 255, 127)
        text_bg_color = None
        text = font.render(button.text, True, font_color, text_bg_color)
        screen.blit(text, (body_top_left_x + BUTTON_PADDING +
                    icon_width + ELEMENT_SPACING, button.y + BUTTON_PADDING))


def display_units(screen, gs):
    for r in range(MAP_Y):
        for c in range(MAP_X):
            # print(f"the vertical value is {r*SQ_SIZE+WALLSIZE}")
            index = gs.map[r][c]
            coords = (r, c)
            if index != -1:
                this_unit = gs.unit_list[index]
                this_anim = this_unit.anim
                if isinstance(this_anim, anim.StillAnim):
                    animate_still(coords, this_unit,  screen)
                if isinstance(this_anim, anim.MovingAnim):
                    animate_moving(this_unit, screen, gs)
                if isinstance(this_anim, anim.AttackAnim):
                    animate_attacking(this_unit, screen, gs)
                if isinstance(this_anim, anim.TakingDamageAnim):
                    animate_taking_damage(this_unit, screen, gs)
                if isinstance(this_anim, anim.DeathAnim):
                    animate_dying(this_unit, screen, gs)


def prep_unit_move(ref_square, gs):
    # if gs.square_is_occupied(ref_square): # make this "occupied by other unit"
    #     return
    frames_per_square = 5  # change this as desired TODO make this static variable in Anim
    start_square = gs.selected_square
    distance = math.sqrt(
        (start_square[0]-ref_square[0])**2 + (start_square[1]-ref_square[1])**2)
    duration = distance*frames_per_square
    gs.dest_square = ref_square
    this_anim = anim.MovingAnim(duration, start_square, ref_square)
    unit = gs.selected_unit
    if not distance == 0:
        unit.anim = this_anim
        gs.phase = engine.Phase.ANIMATING_MOVE

    else:  # if the user selected the same square twice, skip the move animation
        gs.phase = engine.Phase.AWAITING_MENU_INSTRUCTION

    # move to new method
    adj_squares = [(ref_square[0] + 1, ref_square[1]), (ref_square[0] - 1, ref_square[1]),
                   (ref_square[0], ref_square[1] + 1), (ref_square[0], ref_square[1] - 1)]
    for adj_square in adj_squares:
        if gs.is_on_map(adj_square):
        # if it's in range AND if it's occupied
            if gs.square_is_occupied(adj_square):
                gs.menu.buttons.append(engine.game_menu.AttackButton())
                break

    gs.menu.buttons.append(engine.game_menu.WaitButton())
    gs.menu.buttons.append(engine.game_menu.CancelButton())

def prep_unit_attack(ref_square, gs):
    selected_square = gs.dest_square
    selected_unit = gs.selected_unit
    gs.target_square = ref_square
    col = ref_square[0]
    row = ref_square[1]
    target_unit_index = gs.map[row][col]
    target_unit = gs.unit_list[target_unit_index]
    selected_unit.anim = anim.AttackAnim(selected_square, ref_square, SQ_SIZE)
    target_unit.anim = anim.TakingDamageAnim(ref_square)
    gs.transition_to_animating_instruction()


def animate_still(coords, this_unit, screen):
    if this_unit.anim.square == None:
        (r, c) = coords
    else:
        (r, c) = this_unit.anim.square
    this_type = this_unit.unit_name()
    this_team = engine.Team.to_string(this_unit.team())
    unit_sprite = IMAGES[this_team, this_type]
    if not this_unit.is_active:
        unit_sprite = convert_sprite_to_greyscale(unit_sprite)

    screen.blit(unit_sprite, p.Rect(c*SQ_SIZE, r*SQ_SIZE+WALLSIZE, SQ_SIZE, SQ_SIZE))


def animate_moving(this_unit, screen, gs):
    this_anim = this_unit.anim
    # if isinstance(anim, Anim.StillAnim): # if the user selected the same square
    #     gs.phase = EngineScript.Phase.AWAITING_MENU_INSTRUCTION

    start_square = this_anim.start_square
    end_square = this_anim.end_square

    # in our square variables, first is column (x), then row (y)
    dura = this_unit.anim.duration
    curr = this_unit.anim.timer
    dR = end_square[1] - start_square[1]
    dC = end_square[0] - start_square[0]

    r, c = (start_square[1] + dR*curr/dura, start_square[0] + dC*curr/dura)

    # show moving piece
    this_team = engine.Team.to_string(this_unit.team())

    screen.blit(IMAGES[this_team, this_unit.unit_name()], p.Rect(
        c*SQ_SIZE, r*SQ_SIZE + WALLSIZE, SQ_SIZE, SQ_SIZE))

    this_unit.anim.timer += 1
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.anim = anim.StillAnim((end_square[1], end_square[0]))
        gs.phase = engine.Phase.AWAITING_MENU_INSTRUCTION


def animate_attacking(this_unit, screen, gs):
    this_anim = this_unit.anim
    this_team = engine.Team.to_string(this_unit.team())
    this_sprite = IMAGES[this_team, this_unit.unit_name()]
    (c, r) = gs.selected_square
    (dx, dy) = this_anim.get_current_offset()

    screen.blit(this_sprite, p.Rect(c*SQ_SIZE + dx, r*SQ_SIZE + WALLSIZE + dy, SQ_SIZE, SQ_SIZE))

    this_anim.increment_timer()
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.anim = anim.StillAnim()
        this_unit.is_active = False


def animate_taking_damage(this_unit, screen, gs):
    this_anim = this_unit.anim
    this_team = engine.Team.to_string(this_unit.team())
    this_sprite = IMAGES[this_team, this_unit.unit_name()].copy()
    (c, r) = gs.target_square
    color_offset = this_anim.get_alpha_offset()

    shade_color = (color_offset, color_offset, color_offset)

    sprite_color = shade_color + (color_offset,) 
    # check this later, color offset should not be needed here? TODO

    this_sprite.fill(sprite_color, None, p.BLEND_RGB_ADD)
    screen.blit(this_sprite, p.Rect(c * SQ_SIZE, r * SQ_SIZE + WALLSIZE, SQ_SIZE, SQ_SIZE))

    this_anim.increment_timer()
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.hit_points -= 1
        if this_unit.hit_points <= 0:
            this_unit.anim = anim.DeathAnim()

        else:
            this_unit.anim = anim.StillAnim()
            gs.phase = engine.Phase.AWAITING_UNIT_SELECTION


def animate_dying(this_unit, screen, gs):
    this_anim = this_unit.anim
    this_team = engine.Team.to_string(this_unit.team())
    this_sprite = IMAGES[this_team, this_unit.unit_name()].copy()
    (c, r) = gs.target_square
    alpha_offset = this_anim.get_alpha_offset()

    shade_color = (255, 255, 255)

    sprite_color = shade_color + (alpha_offset,)

    this_sprite.fill(sprite_color, None, p.BLEND_RGBA_MULT)
    screen.blit(this_sprite, p.Rect(c*SQ_SIZE, r* SQ_SIZE + WALLSIZE, SQ_SIZE, SQ_SIZE))

    this_anim.increment_timer()
    if this_unit.anim.timer >= this_unit.anim.duration:
        gs.map[r][c] = -1
        gs.phase = engine.Phase.AWAITING_UNIT_SELECTION





def animate_turn_banner(screen, gs):
    time = gs.banner_anim.timer
    dura = gs.banner_anim.duration
    blue_to_move = gs.blue_to_move

    font = p.font.Font('Fonts/PressStart2P-Regular.ttf', 32)

    if blue_to_move:
        font_color = p.Color(0, 0, 172)
        text_bg_color = None
        text = "Blue Turn"

    else:
        font_color = p.Color(255, 0, 0)
        text_bg_color = None
        text = "Red Turn"
    text = font.render(text, True, font_color, text_bg_color)

    text_width = text.get_width()
    text_height = text.get_height()

    x_mid = (MAP_WIDTH - text_width) / 2
    y = (MAP_HEIGHT - text_height) / 2

    if time < dura / 3:
        x = MAP_WIDTH - (MAP_WIDTH - x_mid) * 3 * time / dura
        screen.blit(text, (x, y))

    elif time < 2 * dura / 3:
        x = x_mid
        screen.blit(text, (x, y))

    elif time < dura:
        x = x_mid - (x_mid + text_width) * (3 * time -
                                            2 * dura) / (dura)  # this will sum to
        screen.blit(text, (x, y))

    gs.banner_anim.timer += 1

    if time >= dura:
        gs.transition_to_awaiting_unit_selection()


def square_can_produce(square, gs):
    if square in gs.production_tiles:
        return True
    return False


def get_the_row_and_col(pos):
    x = pos[0] // SQ_SIZE
    y = (pos[1] - WALLSIZE) // SQ_SIZE
    return (x, y)


def get_square_coords(square):
    (c, r) = square
    return (c*SQ_SIZE, r*SQ_SIZE+WALLSIZE)


def mouse_in_button(mouse_pos, button):
    return button.x <= mouse_pos[0] < button.x + button.width and button.y <= mouse_pos[1] <= button.y + button.height


def mouse_in_menu(mouse_pos, menu):
    return menu.x <= mouse_pos[0] < menu.x + menu.width and menu.y <= mouse_pos[1] <= menu.y + menu.height


def convert_sprite_to_greyscale(image):
    grey_image = p.Surface(image.get_size(), p.SRCALPHA)
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            r, g, b, a = image.get_at((x, y))
            grey = int(0.34 * r + 0.48 * g + 0.18 * b)
            grey_image.set_at((x, y), (grey, grey, grey, a))
            if a != 255:
                pass
    return grey_image


def check_end_turn(gs):
    advance_state = True
    team = engine.Team.BLUE if gs.blue_to_move else engine.Team.RED
    for unit in gs.unit_list:
        if unit.team() == team and unit.is_active == True:
            advance_state = False
    if advance_state == True:
        gs.transition_to_turn_transition()


if __name__ == "__main__":
    main()
