import pygame as p
import EngineScript
import AnimAction

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
        "team": "blue"
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
                    map_event_handler(target, gs.map)
                elif is_in_menu(target):
                    menu_event_handler(target, gs.map, gs.menu)
            elif e.type == p.KEYDOWN:  # later move this to menu
                if e.key == p.K_z:
                    gs.undoMove()
                    validMoves = gs.getAllMoves()        
        draw_game_state(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

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


def draw_game_state(screen, gs, validMoves, sqSelected, phase):
    if phase == gs.Phase.AWAITING_UNIT_SELECTION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, map, gs.unitList, [])
    elif phase == gs.Phase.UNIT_SELECTED:
        display_map(screen)
        display_menu(screen, gs)
        highligh_spaces(gs.activeUnit, gs.map)
        display_units(screen, map, gs.unitList, [])
    elif phase == gs.Phase.ANIMATING_MOVE:
        display_map(screen)
        display_menu(screen, gs)
        display_units(screen, gs.activeUnit)
    elif phase == gs.Phase.AWAITING_MENU_INSTRUCTION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(None)
    elif phase == gs.Phase.SELECTING_TARGET:
        display_map(screen)
        display_menu(screen, gs)
        highlight_spaces(screen, gs, map)
    elif phase == gs.Phase.ANIMATING_INSTRUCTION:
        display_map(screen)
        display_menu(screen, gs)
        display_units(gs.activeUnit, AnimAction.Attacking)
    elif phase == gs.Phase.TURN_TRANSITION:
        display_map(screen)
        display_menu(screen, gs)
        animate_turn_banner()

    


def display_map(screen):
    screen.blit(BOARDART, p.Rect(0, 0, WIDTH, HEIGHT))


def display_units(screen, map, unitList):
    for r in range(BOARD_Y):
        for c in range(BOARD_X):
            # print(f"the vertical value is {r*SQ_SIZE+WALLSIZE}")
            index = map[r][c]
            if index != -1:
                thisUnit = unitList[index]
                thisType = thisUnit.unit_name()
                thisTeam = thisUnit.team()
                screen.blit(IMAGES[thisTeam, thisType], p.Rect(c*SQ_SIZE, r*SQ_SIZE+WALLSIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, clock, gs):
    coords = []
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
    starting_x = SCALE*2 # two scaled "pixels"
    starting_y = BOARD_HEIGHT + SCALE*2
    button_spacing_x = SQ_SIZE * 3
    draw_x = SCALE*2
    draw_y = starting_y
    for button in menu.buttons:
        button_s = p.Surface(())




if __name__ == "__main__":
    main()