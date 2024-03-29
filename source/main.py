"""Entry point, handles main input/output loop for game"""
import math

import pygame as p
import anim
import engine
import top_state
import main_menu_state
import font_util
import units

SCALE = 4
MAP_X = 8
MAP_Y = 13
SQ_SIZE = 16 * SCALE
MAP_WIDTH = MAP_X * SQ_SIZE
MAP_HEIGHT = MAP_Y * SQ_SIZE
INFO_HEIGHT = 8 * SCALE
WIDTH = 128 * SCALE
HEIGHT = MAP_HEIGHT + INFO_HEIGHT
MAX_FPS = 30
IMAGES = {}
INACTIVE_IMAGES = {}
BOARDART = p.image.load("Sprites/field.png")
BOARDART = p.transform.scale(BOARDART, (MAP_WIDTH, MAP_HEIGHT))
COINSART = p.image.load("Sprites/coins.png")
COINSART = p.transform.scale(COINSART, (INFO_HEIGHT, INFO_HEIGHT))
BORDER_COLOR = p.Color('gray25')

CURRENT_STATE = top_state.MainPhase.MAIN_MENU


def load_images():
    """Loads the image sprites for each unit type"""
    teams = ["b", "r"]
    unit_types = ["footsoldier", "lancer", "armored", "archer", "knight"]
    load_door_images()
    for team in teams:
        for unit_type in unit_types:
            IMAGES[team, unit_type] = p.image.load(
                "Sprites/" + team + "_" + unit_type + ".png")
            IMAGES[team, unit_type] = p.transform.scale(
                IMAGES[team, unit_type], (SQ_SIZE, SQ_SIZE))
            INACTIVE_IMAGES[team, unit_type] = convert_sprite_to_greyscale(IMAGES[team, unit_type])


def load_door_images():    
    IMAGES["r", "door_left"] = p.image.load(  # the doors are special case
        "Sprites/door_l.png")
    IMAGES["r", "door_left"] = p.transform.scale(
        IMAGES["r", "door_left"], (SQ_SIZE, SQ_SIZE))
    IMAGES["r", "door_right"] = p.image.load(
        "Sprites/door_r.png")
    IMAGES["r", "door_right"] = p.transform.scale(
        IMAGES["r", "door_right"], (SQ_SIZE, SQ_SIZE))
    IMAGES["b", "door_left"] = p.transform.flip(IMAGES["r", "door_left"], 0, 1)
    IMAGES["b", "door_right"] = p.transform.flip(IMAGES["r", "door_right"], 0, 1)
    IMAGES["fragment"] = p.image.load(
        "Sprites/door_fragment.png"
    )
    IMAGES["fragment"] = p.transform.scale(IMAGES["fragment"], (2 * SCALE, 2 * SCALE))


def main():
    """Governs main input/rendering loop"""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    mm_s = main_menu_state.MainMenuState(SQ_SIZE, screen.get_width())
    load_images()
    running = True
    gs.setup_still_anims()
    # this_unit = EngineScript.ArmyUnit(kwargs)
    while running:
        events = p.event.get()
        for e in events:
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                target = p.mouse.get_pos()
                running = master_event_handler(target, mm_s, gs, events)
        
        master_draw(screen, mm_s, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def master_event_handler(target, mm_s, gs, events):
    if CURRENT_STATE == top_state.MainPhase.MAIN_MENU:
        main_menu_event_handler(target, mm_s, events)

        if mm_s.state == main_menu_state.State.TURN_OFF:
            return False

    elif CURRENT_STATE == top_state.MainPhase.IN_MATCH:
        in_match_event_handler(target, gs)

    return True


def main_menu_event_handler(target, mm_s, events):
    mm_s.event_handler(target, events)


def in_match_event_handler(target, gs):
    if mouse_in_menu(target, gs.menu):
        menu_event_handler(target, gs)

    else:
        map_event_handler(target, gs)

def map_event_handler(mouse_pos, gs):
    """Gets mouse clicks on the map"""
    phase = gs.phase
    if phase in {
            engine.Phase.ANIMATING_MOVE,
            engine.Phase.AWAITING_MENU_INSTRUCTION,
            engine.Phase.ANIMATING_INSTRUCTION,
            engine.Phase.TURN_TRANSITION,
            engine.Phase.PLAYER_WON
        }:
        return

    selected_square = get_the_row_and_col(mouse_pos)
    if phase == engine.Phase.AWAITING_UNIT_SELECTION:
        select_space(selected_square, gs)

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

        else:
            gs.transition_from_selecting_target_to_awaiting_menu_instruction()

    elif phase == engine.Phase.READY_FOR_MAIN_MENU:
        global CURRENT_STATE
        CURRENT_STATE = top_state.MainPhase.MAIN_MENU


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
                gs.map[sel_y][sel_x] = -1
                gs.map[ref_y][ref_x] = gs.selected_unit_index
                gs.selected_unit.is_active = False
                gs.phase = engine.Phase.AWAITING_UNIT_SELECTION
                gs.menu = engine.game_menu.GameMenu()
                gs.reset_select()

            elif isinstance(button, engine.game_menu.EndTurnButton):
                gs.transition_to_turn_transition()
                gs.menu = engine.game_menu.GameMenu()

            elif isinstance(button, engine.game_menu.AttackButton):
                gs.transition_to_selecting_target()

            elif isinstance(button, engine.game_menu.BuyFootSoldierButton):
                gs.buy_unit(units.FootSoldier)

            elif isinstance(button, engine.game_menu.BuyLancerButton):
                gs.buy_unit(units.Lancer)

            elif isinstance(button, engine.game_menu.BuyArmoredSoldierButton):
                gs.buy_unit(units.Armored)

            elif isinstance(button, engine.game_menu.BuyArcherButton):
                gs.buy_unit(units.Archer)

            elif isinstance(button, engine.game_menu.BuyKnightButton):
                gs.buy_unit(units.Knight)

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
        screen.blit(s, (x*SQ_SIZE, y*SQ_SIZE))


def highlight_enemies(screen, gs):
    """Highlights squares that contain enemies"""
    s = p.Surface((SQ_SIZE - SCALE / 2, SQ_SIZE - SCALE /2))
    s.set_alpha(128) # 255 is opaque
    s.fill(p.Color('red'))
    gs.find_in_range_hostiles()
    for square in gs.found_hostiles:
        x = square[0]
        y = square[1]
        screen.blit(s, (x*SQ_SIZE, y*SQ_SIZE))


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
        gs.transition_from_selecting_target_to_awaiting_unit_purchase()

    else:
        gs.selected_square = selected_square
        gs.dest_square = selected_square
        gs.prep_end_menu()

def master_draw(screen, mm_s, gs):
    global CURRENT_STATE  # pylint: disable=global-statement
    if CURRENT_STATE == top_state.MainPhase.MAIN_MENU:
        draw_menu_state(screen, mm_s)
        if mm_s.state == main_menu_state.State.TO_GAME:
            gs.reset_game()
            gs.player_types = mm_s.player_types
            CURRENT_STATE = top_state.MainPhase.IN_MATCH
            mm_s.reset_menu()

    elif CURRENT_STATE == top_state.MainPhase.IN_MATCH:
        draw_game_state(screen, gs)


def draw_menu_state(screen, mm_s):
    mm_s.draw_all(screen)


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
        display_action_menu(screen, gs)

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

    elif gs.phase == engine.Phase.COUNTING_GOLD:
        display_map(screen)
        display_units(screen, gs)
        animate_coins(screen, gs)

    elif gs.phase == engine.Phase.AWAITNIG_UNIT_PURCHASE:
        display_map(screen)
        display_units(screen, gs)
        display_buy_menu(screen, gs)

    elif gs.phase == engine.Phase.PLAYER_WON:
        display_map(screen)
        display_units(screen, gs)
        animate_win_banner(screen, gs)

    elif gs.phase == engine.Phase.READY_FOR_MAIN_MENU:
        display_map(screen)
        display_units(screen, gs)
        animate_win_banner(screen, gs)

    elif gs.phase == engine.Phase.AWAITING_UNIT_SELECTION_AI:
        gs.get_ai_move()
        display_map(screen)
        display_units(screen, gs)
    
    elif gs.phase == engine.Phase.AWAITING_MENU_INSTRUCTION_AI:
        display_map(screen)
        display_units(screen, gs)

    # always do this
    display_info_bar(screen, gs)


def display_map(screen):
    screen.blit(BOARDART, p.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))


def display_action_menu(screen, gs):
    border_padding = 1 * SCALE
    button_padding = 2 * SCALE
    element_height = 6 * SCALE
    button_height = element_height + 2 * button_padding

    body_color = p.Color('gray50')

    menu = gs.menu
    menu.width = MAP_WIDTH / 2.2
    border_width = menu.width + 2 * border_padding

    right_side = True
    top_side = True
    if gs.dest_square != []:
        (dest_square_x, dest_square_y) = gs.dest_square

    else:
        (dest_square_x, dest_square_y) = gs.selected_square

    if gs.selected_square is not None:  # later TODO this should probably be an exception
        if dest_square_x >= MAP_X // 2:
            right_side = False

        if dest_square_y <= MAP_Y // 2:
            top_side = False

    button_count = len(menu.buttons)
    menu.height = button_count * button_height
    border_height = menu.height + 2 * border_padding
    (dest_coords_x, dest_coords_y) = get_square_coords(gs.dest_square)

    if right_side:
        menu.x = dest_coords_x + SQ_SIZE
    else:
        menu.x = dest_coords_x - menu.width

    if top_side:
        menu.y = dest_coords_y - menu.height
    else:
        menu.y = dest_coords_y + SQ_SIZE

    draw_menu_border(screen, menu, border_width, border_height)
    draw_menu_body(screen, menu, border_padding, body_color)

    mouse_pos = p.mouse.get_pos()

    body_top_left_x = menu.x + border_padding
    body_top_left_y = menu.y + border_padding

    for i,_ in enumerate(gs.menu.buttons):
        button = gs.menu.buttons[i]

        button.x = body_top_left_x
        button.width = menu.width

        button.y = body_top_left_y + (i * button_height)
        button.height = button_height

        draw_button(screen, button, mouse_pos, body_color,
                    body_top_left_x, element_height, button_padding)


def draw_menu_border(screen, menu, border_width, border_height):
    border_surface = p.Surface((border_width, border_height))
    border_surface.fill(BORDER_COLOR)
    screen.blit(border_surface, (menu.x, menu.y))


def draw_menu_body(screen, menu, border_padding, body_color):
    body_surface = p.Surface((menu.width, menu.height))
    body_surface.fill(body_color)
    screen.blit(body_surface, (menu.x + border_padding, menu.y + border_padding))


def draw_button(screen, button, mouse_pos, body_color, body_top_left_x, element_height, button_padding):
    element_spacing = 2 * SCALE  # spacing between the icon and the button
    icon_width = element_height
    button_color = None
    if mouse_in_button(mouse_pos, button):
        button_color = p.Color("Gray38")
    else:
        button_color = body_color
    button_surface = p.Surface((button.width, button.height))
    button_surface.fill(button_color)
    screen.blit(button_surface, (button.x, button.y))
    icon_image = button.icon
    icon_size = (element_height, element_height)
    icon_location = (body_top_left_x + button_padding,
                     button.y + button_padding)
    icon_image = p.transform.scale(icon_image, icon_size)
    screen.blit(icon_image, icon_location)
    font = p.font.Font('Fonts/PixeloidSansBold.ttf', 24)
    font_color = p.Color(255, 255, 127)
    text_bg_color = None
    text = font.render(button.text, True, font_color, text_bg_color)
    screen.blit(text, (body_top_left_x + button_padding +
                icon_width + element_spacing, button.y + button_padding))


def display_buy_menu(screen, gs):
    border_padding = 1 * SCALE
    button_padding = 2 * SCALE
    element_height = 6 * SCALE
    button_height = element_height + 2 * button_padding

    body_color = p.Color('gray50')

    menu = gs.menu
    menu.width = MAP_WIDTH * 7 / 8
    border_width = menu.width + 2 * border_padding

    menu.height = MAP_HEIGHT / 2.2
    border_height = menu.height + 2 * border_padding

    menu.x = 1 / 16 * WIDTH
    menu.y =  1 / 4 * HEIGHT

    draw_menu_border(screen, menu, border_width, border_height)
    draw_menu_body(screen, menu, border_padding, body_color)

    mouse_pos = p.mouse.get_pos()

    body_top_left_x = menu.x + border_padding
    body_top_left_y = menu.y + border_padding

    # render each button

    for i,_ in enumerate(gs.menu.buttons):
        button = gs.menu.buttons[i]

        button.x = body_top_left_x
        button.width = menu.width

        button.y = body_top_left_y + (i * button_height)
        button.height = button_height

        draw_button(screen, button, mouse_pos, body_color,
                    body_top_left_x, element_height, button_padding)


def display_info_bar(screen, gs):
    # draw the background
    info_rect = p.Surface((WIDTH, INFO_HEIGHT))
    info_rect.fill(BORDER_COLOR)
    screen.blit(info_rect, (0, HEIGHT - INFO_HEIGHT))

    # put the team text
    active_team = gs.get_active_team()
    text = engine.Team.to_string(active_team)
    text = text + " Team"
    font_color = engine.Team.to_color(active_team)
    text_bg_color = None

    font = p.font.Font('Fonts/PixeloidSansBold.ttf', 24)
    text_block = font.render(text, True, font_color, text_bg_color)
    screen.blit(text_block, (SCALE, HEIGHT - INFO_HEIGHT))

    # put the gold count
    player_gold = gs.player_gold[active_team.value]
    gold_string = str(player_gold)
    gold_string_length = len(gold_string)
    gold_font = p.font.Font('Fonts/PixeloidSansBold.ttf', 24)
    gold_color = p.Color(255, 255, 0)

    gold_text_block = gold_font.render(gold_string, True, gold_color, text_bg_color)

    screen.blit(gold_text_block, (WIDTH - INFO_HEIGHT * (1 + gold_string_length), HEIGHT - INFO_HEIGHT))
    screen.blit(COINSART, (WIDTH - INFO_HEIGHT, HEIGHT - INFO_HEIGHT))


def display_units(screen, gs):
    for r in range(MAP_Y):
        for c in range(MAP_X):
            index = gs.map[r][c]
            coords = (r, c)
            if index > -1:
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
                if isinstance(this_anim, anim.DoorExplodingAnim):
                    animate_expoding_door(this_unit, screen, gs)


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

    gs.menu = engine.game_menu.GameMenu()

    # move to new method
    gs.find_in_range_hostiles()
    if gs.found_hostiles:
        gs.menu.buttons.append(engine.game_menu.AttackButton())

    # adj_squares = [(ref_square[0] + 1, ref_square[1]), (ref_square[0] - 1, ref_square[1]),
    #                (ref_square[0], ref_square[1] + 1), (ref_square[0], ref_square[1] - 1)]
    # for adj_square in adj_squares:
    #     if gs.is_on_map(adj_square):
    #     # if it's in range AND if it's occupied
    #         if gs.square_is_occupied_by_hostile(adj_square):
    #             gs.menu.buttons.append(engine.game_menu.AttackButton())
    #             break

    gs.menu.buttons.append(engine.game_menu.WaitButton())
    gs.menu.buttons.append(engine.game_menu.CancelButton())


def prep_unit_attack(ref_square, gs):
    dest_square = gs.dest_square
    selected_unit = gs.selected_unit
    gs.target_square = ref_square
    col = ref_square[0]
    row = ref_square[1]
    target_unit_index = gs.map[row][col]
    target_unit = gs.unit_list[target_unit_index]

    # confirm the move here
    (sel_x, sel_y) = gs.selected_square
    (dest_x, dest_y) = dest_square
    gs.map[sel_y][sel_x] = -1
    gs.map[dest_y][dest_x] = gs.selected_unit_index

    selected_unit.anim = anim.AttackAnim(dest_square, ref_square, SQ_SIZE)
    target_unit.anim = anim.TakingDamageAnim(ref_square)
    gs.transition_to_animating_instruction()


def animate_still(coords, this_unit, screen):
    if this_unit.anim.square == None:
        (r, c) = coords
    else:
        (r, c) = this_unit.anim.square
    this_type = this_unit.unit_name()
    this_team = engine.Team.to_abbreviation(this_unit.team())
    active = this_unit.is_active
    if active:
        unit_sprite = IMAGES[this_team, this_type]
    else:
        unit_sprite = INACTIVE_IMAGES[this_team, this_type]

    screen.blit(unit_sprite, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


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
    this_team = engine.Team.to_abbreviation(this_unit.team())

    screen.blit(IMAGES[this_team, this_unit.unit_name()], p.Rect(
        c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    this_unit.anim.timer += 1
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.anim = anim.StillAnim((end_square[1], end_square[0]))
        gs.phase = engine.Phase.AWAITING_MENU_INSTRUCTION


def animate_attacking(this_unit, screen, gs):
    this_anim = this_unit.anim
    this_team = engine.Team.to_abbreviation(this_unit.team())
    this_sprite = IMAGES[this_team, this_unit.unit_name()]
    (c, r) = gs.dest_square
    (dx, dy) = this_anim.get_current_offset()

    screen.blit(this_sprite, p.Rect(c*SQ_SIZE + dx, r*SQ_SIZE + dy, SQ_SIZE, SQ_SIZE))

    this_anim.increment_timer()
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.anim = anim.StillAnim()
        this_unit.is_active = False


def animate_taking_damage(this_unit, screen, gs):
    this_anim = this_unit.anim
    this_team = engine.Team.to_abbreviation(this_unit.team())
    this_sprite = IMAGES[this_team, this_unit.unit_name()].copy()
    (c, r) = gs.target_square
    color_offset = this_anim.get_whiteness_offset()

    shade_color = (color_offset, color_offset, color_offset)

    sprite_color = shade_color + (color_offset,)
    # check this later, color offset should not be needed here? TODO

    this_sprite.fill(sprite_color, None, p.BLEND_RGB_ADD)
    screen.blit(this_sprite, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    this_anim.increment_timer()
    if this_unit.anim.timer >= this_unit.anim.duration:

        # find the atttacking units power
        power = gs.selected_unit.attack_power

        this_unit.hit_points -= power
        if this_unit.hit_points <= 0:
            if isinstance(this_unit, units.Door):
                this_unit.anim = anim.DoorExplodingAnim()
                gs.transition_to_player_winning()
            else:
                this_unit.anim = anim.DeathAnim()

        else:
            this_unit.anim = anim.StillAnim()
            gs.transition_to_awaiting_unit_selection()


def animate_dying(this_unit, screen, gs):
    this_anim = this_unit.anim
    this_team = engine.Team.to_abbreviation(this_unit.team())
    this_sprite = IMAGES[this_team, this_unit.unit_name()].copy()
    (c, r) = gs.target_square
    alpha_offset = this_anim.get_alpha_offset()

    shade_color = (255, 255, 255)

    sprite_color = shade_color + (alpha_offset,)

    this_sprite.fill(sprite_color, None, p.BLEND_RGBA_MULT)
    screen.blit(this_sprite, p.Rect(c*SQ_SIZE, r* SQ_SIZE, SQ_SIZE, SQ_SIZE))

    this_anim.increment_timer()
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.anim = anim.StillAnim()
        gs.map[r][c] = -1
        gs.phase = engine.Phase.AWAITING_UNIT_SELECTION


def animate_expoding_door(this_unit, screen, gs):
    this_anim = this_unit.anim
    (c, r) = gs.target_square
    (x, y) = (c * SQ_SIZE, r * SQ_SIZE)

    # if it's in the first phase
    if this_anim.phase == 0:
        this_team = engine.Team.to_abbreviation(this_unit.team())

        # really the team doesn't matter ma vabbè
        this_sprite = IMAGES[this_team, this_unit.unit_name()].copy()

        color_offset = this_anim.get_alpha_offset()

        shade_color = (color_offset, color_offset, color_offset)

        sprite_color = shade_color + (color_offset,)
        # check this later, color offset should not be needed here? TODO

        this_sprite.fill(sprite_color, None, p.BLEND_RGB_ADD)
        screen.blit(this_sprite, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        this_anim.increment_timer()
        if this_unit.anim.timer >= this_unit.anim.durations[0]:
            this_unit.anim.advance_phase()

    elif this_anim.phase == 1:
        fragment_sprite = IMAGES["fragment"]
        for row in this_anim.shards:
            for shard in row:
                sprite_copy = fragment_sprite
                angle = shard.angle
                sprite_copy = p.transform.rotate(sprite_copy, angle)
                offset = shard.offset
                offset_x = offset[0]
                offset_y = offset[1]
                screen.blit(sprite_copy, p.Rect(x + SCALE * offset_x,
                            y + SCALE * offset_y, 2 * SCALE,2 * SCALE))

        this_anim.increment_timer()
        if this_unit.anim.timer >= this_unit.anim.durations[1]:
            pass
            # for now just freeze the game whatever we'll add a main menu later



def animate_turn_banner(screen, gs):
    time = gs.banner_anim.timer
    dura = gs.banner_anim.duration
    team = gs.get_active_team()
    text = engine.Team.to_string(team)
    text += " Turn"

    font = p.font.Font('Fonts/PixeloidSansBold.ttf', 32)

    font_color = engine.Team.to_color(team)
    text_bg_color = None
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
        gs.transition_from_turn_transition_to_counting_gold()


def animate_win_banner(screen, gs):
    banner_anim = gs.banner_anim
    alpha_offset = banner_anim.get_alpha_offset()

    team = gs.get_active_team()
    text = engine.Team.to_string(team)
    text += " Wins!"

    font = p.font.Font('Fonts/PixeloidSansBold.ttf', 32)

    font_color = engine.Team.to_color(team)
    outline_color = p.Color("black")

    thickness = 3

    # text = font.render(text, True, font_color, text_bg_color)
    text_surface = font_util.surface_render_w_outline(text, font, font_color,
                                                      outline_color, thickness, alpha_offset)

    text_width = text_surface.get_width()
    text_height = text_surface.get_height()

    x = (MAP_WIDTH - text_width) / 2
    y = (MAP_HEIGHT - text_height) / 2

    screen.blit(text_surface, (x, y))

    banner_anim.increment_timer()

    if gs.phase == engine.Phase.PLAYER_WON and banner_anim.anim_done():
        gs.transition_to_ready_for_main_menu()


def animate_coins(screen, gs):
    if gs.coin_anim is None:
        coin_index = gs.coin_index
        for i in range(coin_index, len(gs.coin_squares)):
            current_square = gs.coin_squares[i]
            if gs.square_is_occupied_by_friendly(current_square):
                gs.coin_index = i
                gs.coin_anim = anim.CoinAnim()
                break
        if gs.coin_anim is None: # as in, STILL no anim
            gs.transition_from_counting_gold_to_awaiting_unit_selection()
            return

    current_square = gs.coin_squares[gs.coin_index]
    x = current_square[0]
    y = current_square[1]
    coin_anim = gs.coin_anim
    coin_image = coin_anim.get_sprite(SQ_SIZE)
    coin_offset = coin_anim.get_current_offset()

    screen.blit(coin_image, (x * SQ_SIZE + SQ_SIZE / 4, y * SQ_SIZE + coin_offset))

    coin_anim.increment_timer()

    if coin_anim.timer >= coin_anim.duration: 
        gs.coin_anim = None
        gs.add_money()
        gs.coin_index += 1


def get_the_row_and_col(pos):
    x = pos[0] // SQ_SIZE
    y = pos[1] // SQ_SIZE
    return (x, y)


def get_square_coords(square):
    (c, r) = square
    return (c*SQ_SIZE, r*SQ_SIZE)


def mouse_in_button(mouse_pos, button):
    return button.x <= mouse_pos[0] < button.x + button.width \
        and button.y <= mouse_pos[1] <= button.y + button.height


def mouse_in_menu(mouse_pos, menu):
    return menu.x <= mouse_pos[0] < menu.x + menu.width \
        and menu.y <= mouse_pos[1] <= menu.y + menu.height


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
