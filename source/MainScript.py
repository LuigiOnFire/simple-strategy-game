import pygame as p
import EngineScript
import Anim

SCALE = 4
BOARD_X = 8
BOARD_Y = 11
SQ_SIZE = 16*SCALE
BOARD_WIDTH = BOARD_X*SQ_SIZE
BOARD_HEIGHT = BOARD_Y*SQ_SIZE
WALLSIZE = 8*SCALE
MENU_WIDTH = BOARD_WIDTH
MENU_HEIGHT = 16*SCALE # one square for now
WIDTH = 128*SCALE
HEIGHT = 192*SCALE
MAX_FPS = 15
IMAGES = {}
BOARDART = p.image.load("Sprites/field.png")
BOARDART = p.transform.scale(BOARDART, (BOARD_WIDTH, BOARD_HEIGHT))


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
    validMoves = gs.getAllMoves()
    moveMade = False # flag variable for when a move is made
    loadImages()
    running = True
    sqSelected = () #tracks the row and the column
    playerClicks = [] #two tuples that keep track of the two squares the player has clicked
    kwargs = {
        "attack_range": 1,
        "move_range": 1,
        "hit_points": 1,
        "max_hit_points": 1,
        "unit_name": "Foot Soldier",
        "team": "blue",
        "anim": Anim.StillAnim, 
    }
    thisUnit = EngineScript.FootSoldier
    #thisUnit = EngineScript.ArmyUnit(kwargs)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                target = p.mouse.get_pos()
                if is_in_map(target):
                    map_event_handler(target)
                elif is_in_menu(target):
                    menu_event_handler(target, gs.map, gs.menu)
            elif e.type == p.KEYDOWN:  # later move this to menu
                if e.key == p.K_z:
                    gs.undoMove()
                    validMoves = gs.getAllMoves()        
        draw_game_state(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

def map_event_handler(mouse_pos, gs):
    phase = gs.phase
    if phase == ANIMATING_MOVE or AWAITING_MENU_INSTRUCTION or ANIMATING_INSTRUCTION or TURN_TRANSITION:
        return
    selected_square = get_the_row_and_col(mouse_pos)
    if phase == AWAITING_UNIT_SELECTION:
        select_space(selected_square) # also need to support buying
    if phase == UNIT_SELECTED:
        prep_unit_move(selected_square, gs)

def menu_event_handler(mouse_pos, gs):
    # fill in later
    pass

def highlightSqures(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        s = p.Surface((SQ_SIZE - SCALE / 2, SQ_SIZE - SCALE / 2))
        s.set_alpha(100) # 255 is opaque
        s.fill(p.Color('blue'))
        screen.blit(s, (c*(SQ_SIZE), r*(SQ_SIZE) + WALLSIZE)) # add y offset later
        s.fill(p.Color('blue'))
        for move in validMoves:
            if move.startRow == r and move.startCol == c:
                screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE + WALLSIZE)) # add y offset later

def select_space(selected_square, gs):
    if square_is_occupised(selected_square):
        gs.select_space = gs.unit_list[selected_square[0]][selected_square[1]]
        gs.selected_square = selected_square
        gs.phase = Phase.UNIT_SELECTED
    elif square_can_produce(selected_square, gs.production_tiles):
        gs.selected_square = selected_square
        gs.phase = Phase.UNIT_SELECTED

def draw_game_state(screen, gs, validMoves, sqSelected):
    if gs.phase == EngineScript.Phase.AWAITING_UNIT_SELECTION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs)
    elif gs.phase == gs.Phase.UNIT_SELECTED:
        display_map(screen)
        display_menu(screen, gs)
        highligh_spaces(gs.activeUnit, gs.map)
        display_units(screen, gs)
    elif gs.phase == gs.Phase.ANIMATING_MOVE:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs)
    elif gs.phase == gs.Phase.AWAITING_MENU_INSTRUCTION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs)
    elif gs.phase == gs.Phase.SELECTING_TARGET:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs)
        highlight_spaces(screen, gs, map)
    elif gs.phase == gs.Phase.ANIMATING_INSTRUCTION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs)
    elif gs.phase == gs.Phase.TURN_TRANSITION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs)
        animate_turn_banner()

    
def display_map(screen):
    screen.blit(BOARDART, p.Rect(0, 0, WIDTH, HEIGHT))

def display_menu(screeen, gs):
    pass

def display_units(screen, gs):
    for r in range(BOARD_Y):
        for c in range(BOARD_X):
            # print(f"the vertical value is {r*SQ_SIZE+WALLSIZE}")
            index = gs.map[r][c]
            coords = (r, c)
            if index != -1:
                thisUnit = gs.unitList[index]
                anim = thisUnit.anim
                if isinstance(anim, Anim.StillAnim):
                    animate_still(index, coords, thisUnit, screen)
                if isinstance(anim, Anim.MovingAnim):
                    animate_moving(index, coords, thisUnit, screen)
                if isinstance(anim, Anim.AttackAnim):
                    animate_attacking(index, coords, thisUnit, screen)
                if isinstance(anim, Anim.TakingDamageAnim):
                    anim_taking_damage(unit, coords, thisUnit, screen)
                
def prep_unit_move(ref_square, gs):
    if check_square_occupied(ref_square):
        return
    start_square = gs.selected_unit_location
    distance = sqrt((start_square(0)-ref_square(0))**2 + (start_square(1)-ref_square(1))**2)
    frmes_per_square = 10 # change this as you like
    duration = distance*frames_per_square
    anim = MovingAnim(duration, ref_square)
    unit = unit_list[gs.selected_unit_index]
    unit.anim = anim
    gs.phase = Phase.ANIMATING_MOVE

def animate_still(index, coords, thisUnit, screen):
    (r, c) = coords
    thisType = thisUnit.unit_name()
    thisTeam = thisUnit.team()
    screen.blit(IMAGES[thisTeam, thisType], p.Rect(c*SQ_SIZE, r*SQ_SIZE+WALLSIZE, SQ_SIZE, SQ_SIZE))

def animate_move(move, screen, clock, gs):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) + framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, gs.map, gs.unitList)
        # erase the piece from its ending square
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE + WALLSIZE, SQ_SIZE, SQ_SIZE)
        screen.blit(BOARDART, endSquare, endSquare)
        # show moving piece
        screen.blit(IMAGES[gs.unitList[move.pieceMoved].team(), gs.unitList[move.pieceMoved].unit_name()], p.Rect(c*SQ_SIZE, r*SQ_SIZE + WALLSIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawMenu(menu, screen):
    menu_bg = p.Surface((MENU_WIDTH, MENU_HEIGHT))
    menu_bg.fill(p.Color('black'))
    screen.blit(0, BOARD_HEIGHT, menu_bg)
    button_width = SCALE
    starting_x = SCALE * 2 # two scaled "pixels"
    starting_y = BOARD_HEIGHT + SCALE * 2
    button_spacing_x = SQ_SIZE * 3
    draw_x = SCALE*2
    draw_y = starting_y
    for button in menu.buttons:
        button_s = p.Surface(())

def square_can_produce(square, production_tiles):
    if square in gs.production:
        return true
    return false

if __name__ == "__main__":
    main()