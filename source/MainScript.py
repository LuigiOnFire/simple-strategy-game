import pygame as p
import EngineScript
import Anim
import math

SCALE = 4
MAP_X = 8
MAP_Y = 11
SQ_SIZE = 16*SCALE
WALLSIZE = 8*SCALE
MAP_WIDTH = MAP_X * SQ_SIZE
MAP_HEIGHT = MAP_Y * SQ_SIZE + WALLSIZE * 2
MENU_WIDTH = MAP_WIDTH / 2.5
WIDTH = 128 * SCALE
HEIGHT = 192 * SCALE
MAX_FPS = 30
IMAGES = {}
BOARDART = p.image.load("Sprites/field.png")
BOARDART = p.transform.scale(BOARDART, (MAP_WIDTH, MAP_HEIGHT))


def loadImages():
    teams = ["b", "r"]
    unit_types = ["footsoldier"]
    for team in teams:
        for unit_type in unit_types:
            IMAGES[team, unit_type] = p.image.load("Sprites/" + team + "_" + unit_type + ".png")
            IMAGES[team, unit_type] = p.transform.scale(IMAGES[team, unit_type], (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = EngineScript.GameState()
    moveMade = False # flag variable for when a move is made
    loadImages()
    running = True
    sqSelected = () #tracks the row and the column
    playerClicks = [] #two tuples that keep track of the two squares the player has clicked
    gs.setup_still_anims()
    kwargs = {
        "attack_range": 1,
        "move_range": 1,
        "hit_points": 1,
        "max_hit_points": 1,
        "unit_name": "Foot Soldier",
        "team": "blue",
        "anim": Anim.StillAnim(), 
    }
    this_unit = EngineScript.FootSoldier
    #this_unit = EngineScript.ArmyUnit(kwargs)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                target = p.mouse.get_pos()
                if is_in_map(target):
                    map_event_handler(target, gs)
                elif is_in_menu(target):
                    menu_event_handler(target, gs.map, gs.menu)
            elif e.type == p.KEYDOWN:  # later move this to menu
                if e.key == p.K_z:
                    gs.undoMove()
        draw_game_state(screen, gs, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

def map_event_handler(mouse_pos, gs):
    phase = gs.phase
    if phase in {
        EngineScript.Phase.ANIMATING_MOVE, 
        EngineScript.Phase.AWAITING_MENU_INSTRUCTION, 
        EngineScript.Phase.ANIMATING_INSTRUCTION, 
        EngineScript.Phase.TURN_TRANSITION}:
        return
    selected_square = get_the_row_and_col(mouse_pos)
    if phase == EngineScript.Phase.AWAITING_UNIT_SELECTION:
        select_space(selected_square, gs) # also need to support buying
    elif phase == EngineScript.Phase.UNIT_SELECTED:
        prep_unit_move(selected_square, gs)

def menu_event_handler(mouse_pos, gs):
    # fill in later
    pass

def highlight_spaces(screen, gs):    
        c, r = gs.selected_square
        s = p.Surface((SQ_SIZE - SCALE / 2, SQ_SIZE - SCALE / 2))
        s.set_alpha(100) # 255 is opaque
        s.fill(p.Color('blue'))
        screen.blit(s, (c*(SQ_SIZE), r*(SQ_SIZE) + WALLSIZE))
        s.fill(p.Color('blue'))
        validMoves = gs.get_all_moves()
        for move in validMoves:
            if move.startRow == r and move.startCol == c:
                screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE + WALLSIZE))

def select_space(selected_square, gs):
    if gs.square_is_occupied(selected_square):
        unit_index = gs.map[selected_square[1]][selected_square[0]]
        gs.selected_unit = gs.unit_list[unit_index]
        gs.selected_square = selected_square
        gs.phase = EngineScript.Phase.UNIT_SELECTED
    # elif gs.square_can_produce(selected_square):
    #     gs.selected_square = selected_square
    #     gs.phase = EngineScript.Phase.UNIT_SELECTED

def draw_game_state(screen, gs, sqSelected):
    if gs.phase == EngineScript.Phase.AWAITING_UNIT_SELECTION:
        display_map(screen)
        display_units(screen, gs)
    elif gs.phase == EngineScript.Phase.UNIT_SELECTED:
        display_map(screen)        
        highlight_spaces(screen, gs)
        display_units(screen, gs)
    elif gs.phase == EngineScript.Phase.ANIMATING_MOVE:
        display_map(screen)        
        display_units(screen, gs)
    elif gs.phase == EngineScript.Phase.AWAITING_MENU_INSTRUCTION:
        display_map(screen)
        display_units(screen, gs)
        display_menu(screen, gs)
    elif gs.phase == EngineScript.Phase.SELECTING_TARGET:
        display_map(screen)        
        display_units(screen, gs)
        highlight_spaces(screen, gs)
    elif gs.phase == EngineScript.Phase.ANIMATING_INSTRUCTION:
        display_map(screen)        
        display_units(screen, gs)
    elif gs.phase == EngineScript.Phase.TURN_TRANSITION:
        display_map(screen)        
        display_units(screen, gs)        
        animate_turn_banner()

    
def display_map(screen):
    screen.blit(BOARDART, p.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))

def display_menu(screen, gs):
    X_SCREEN_PADDING = WIDTH // 8
    Y_SCREEN_PADDING = HEIGHT // 8
    BORDER_PADDING = 1 * SCALE
    BUTTON_HEIGHT = 6 * SCALE
    BUTTON_PADDING = 4 * SCALE
    ELEMENT_SPACING = 2 * SCALE # spacing between the icon and the button
    border_width = MENU_WIDTH + 2 * BORDER_PADDING    
    icon_width = BUTTON_HEIGHT

    border_color = p.Color('gray25')
    body_color = p.Color('gray50')

    # maybe move MENU_WIDTH here    
    right_side = True
    top_side = True
    if gs.selected_square != None: # later this should probably be an exception
        if gs.selected_square[0] >= MAP_X // 2:
            right_side = False
        if gs.selected_square[1] <= MAP_Y // 2:
            top_side = False
    
    button_count = (len(gs.menu.buttons))
    menu_height = (button_count * BUTTON_HEIGHT) + (button_count * BUTTON_PADDING) 
    border_height = menu_height + 2 * BORDER_PADDING

    if right_side:
        border_top_left_x = WIDTH - X_SCREEN_PADDING - border_width
    else:
        border_top_left_x = X_SCREEN_PADDING

    if top_side:
        border_top_left_y = Y_SCREEN_PADDING
    else: 
        border_top_left_y = HEIGHT - Y_SCREEN_PADDING - border_height
    border_position = (border_top_left_x, border_top_left_y)

    body_top_left_x = border_top_left_x + BORDER_PADDING
    body_top_left_y = border_top_left_y + BORDER_PADDING
    body_position = (body_top_left_x, body_top_left_y)


    # display the border
    border_surface = p.Surface((border_width, border_height))
    border_surface.fill(border_color)
    screen.blit(border_surface, border_position)

    # display the body
    body_surface = p.Surface((MENU_WIDTH, menu_height))
    body_surface.fill(body_color)
    screen.blit(body_surface, body_position)


    for i in range(0, len(gs.menu.buttons)):
        
        button = gs.menu.buttons[i]
        icon_image = button.icon
        icon_size = (BUTTON_HEIGHT, BUTTON_HEIGHT)
        icon_location = (body_top_left_x + BUTTON_PADDING, body_top_left_y + (i * BUTTON_HEIGHT) + (i + 1 / 2) * BUTTON_PADDING)
        icon_image = p.transform.scale(icon_image, icon_size)

        screen.blit(icon_image, icon_location)

        font = p.font.Font('Fonts/PressStart2P-Regular.ttf', 24)
        font_color = p.Color(255, 255, 127)        
        text = font.render(button.text, True, font_color, body_color)
        textRect = text.get_rect()
        screen.blit(text, (body_top_left_x + BUTTON_PADDING + icon_width + ELEMENT_SPACING, body_top_left_y + (i * BUTTON_HEIGHT) + (i + 1 / 2) * BUTTON_PADDING))

    pass

def display_units(screen, gs):
    for r in range(MAP_Y):
        for c in range(MAP_X):
            # print(f"the vertical value is {r*SQ_SIZE+WALLSIZE}")
            index = gs.map[r][c]
            coords = (r, c)
            if index != -1:
                this_unit = gs.unit_list[index]
                anim = this_unit.anim
                if isinstance(anim, Anim.StillAnim):
                    animate_still(coords, this_unit,  screen)
                if isinstance(anim, Anim.MovingAnim):
                    animate_moving(coords, this_unit, screen, gs)
                if isinstance(anim, Anim.AttackAnim):
                    animate_attacking(index, coords, this_unit, screen)
                if isinstance(anim, Anim.TakingDamageAnim):
                    anim_taking_damage(unit, coords, this_unit, screen)
                
def prep_unit_move(ref_square, gs):
    if gs.square_is_occupied(ref_square):
        return
    frames_per_square = 5 # change this as desired
    start_square = gs.selected_square
    distance = math.sqrt((start_square[0]-ref_square[0])**2 + (start_square[1]-ref_square[1])**2)    
    duration = distance*frames_per_square
    anim = Anim.MovingAnim(duration, start_square, ref_square)
    unit = gs.selected_unit
    unit.anim = anim
    gs.phase = EngineScript.Phase.ANIMATING_MOVE

    # move to new method
    adj_squares = [(ref_square[0] + 1, ref_square[1]), (ref_square[0] - 1, ref_square[1]), (ref_square[0], ref_square[1] + 1), (ref_square[0], ref_square[1] - 1)]
    for adj_square in adj_squares:        
        # if it's in range AND if it's occupied
        if gs.square_is_occupied(adj_square):
            gs.menu.buttons.append(EngineScript.GameMenu.AttackButton())
            break
    gs.menu.buttons.append(EngineScript.GameMenu.WaitButton())
    gs.menu.buttons.append(EngineScript.GameMenu.CancelButton())

def animate_still(coords, this_unit, screen): 
    if this_unit.anim.square == None:
        (r, c) = coords  
    else:
        (r, c) = this_unit.anim.square    
    this_type = this_unit.unit_name()
    this_team = EngineScript.Team.to_string(this_unit.team())
    screen.blit(IMAGES[this_team, this_type], p.Rect(c*SQ_SIZE, r*SQ_SIZE+WALLSIZE, SQ_SIZE, SQ_SIZE))

def animate_moving(coords, this_unit, screen, gs):
    anim = this_unit.anim
    start_square = anim.start_square
    end_square = anim.end_square

    # in our square variables, I believe first is column (x), then row (y)

    dR = end_square[1] - start_square[1]
    dC = end_square[0] - start_square[0]
    dura = this_unit.anim.duration
    curr = this_unit.anim.timer
    r, c = (start_square[1] + dR*curr/dura, start_square[0] + dC*curr/dura)

    # show moving piece
    this_team = EngineScript.Team.to_string(this_unit._team)

    screen.blit(IMAGES[this_team, this_unit.unit_name()], p.Rect(c*SQ_SIZE, r*SQ_SIZE + WALLSIZE, SQ_SIZE, SQ_SIZE))

    this_unit.anim.timer += 1
    if this_unit.anim.timer >= this_unit.anim.duration:
        this_unit.anim = Anim.StillAnim((end_square[1], end_square[0]))
        gs.phase = EngineScript.Phase.AWAITING_MENU_INSTRUCTION


def drawMenu(menu, screen):
    menu_bg = p.Surface((MENU_WIDTH, MENU_HEIGHT))
    menu_bg.fill(p.Color('black'))
    screen.blit(0, MAP_HEIGHT, menu_bg)
    button_width = SCALE
    starting_x = SCALE * 2 # two scaled "pixels"
    starting_y = MAP_HEIGHT + SCALE * 2
    button_spacing_x = SQ_SIZE * 3
    draw_x = SCALE*2
    draw_y = starting_y
    for button in menu.buttons:
        button_s = p.Surface(())

def square_can_produce(square, gs):
    if square in gs.production_tiles:
        return true
    return false

def is_in_map(pos):
    return pos[1] < MAP_HEIGHT

def get_the_row_and_col(pos):
    x = pos[0] // SQ_SIZE
    y = (pos[1] - WALLSIZE) // SQ_SIZE
    return (x, y)

if __name__ == "__main__":
    main()