import pygame as p
import EngineScript

SCALE = 4
WIDTH = 128*SCALE
HEIGHT = 192*SCALE
BOARD_X = 8
BOARD_Y = 11
SQ_SIZE = 16*SCALE
MAX_FPS = 15
IMAGES = {}
BOARDART = p.image.load("Sprites/field.png")
BOARDART = p.transform.scale(BOARDART, (WIDTH, HEIGHT))
WALLSIZE = 8*SCALE

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
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = (location[1] - WALLSIZE) // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                if len(playerClicks) == 0:
                    if gs.squareContainsUnit(row, col): # make sure the square is nonempty
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                        print(f"{playerClicks}")
                        # the square is now selected
                        # calculate the moves and highlight the squares here
                        unitToMove = gs.unitList[gs.map[row][col]]                        
                        validMoves = gs.getValidMoves(row, col, unitToMove.move_range)
                elif len(playerClicks) == 1: #player has made two different clicks
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                    print(f"{playerClicks}")

                    move = EngineScript.Move(playerClicks[0], playerClicks[1], gs.map)
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                    sqSelected = ()
                    playerClicks = []
            elif e.type == p.KEYDOWN:  # later move this to menu
                if e.key == p.K_z:
                    gs.undoMove()
                    validMoves = gs.getAllMoves()

        moveMade = False
        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSqures(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        s = p.Surface((SQ_SIZE - SCALE, SQ_SIZE - SCALE))
        s.set_alpha(100) # 255 is opaque
        s.fill(p.Color('blue'))
        screen.blit(s, (c*(SQ_SIZE), r*(SQ_SIZE) + WALLSIZE)) # add y offset later
        s.fill(p.Color('blue'))
        for move in validMoves:
            if move.startRow == r and move.startCol == c:
                screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE + WALLSIZE)) # add y offset later


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSqures(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.map, gs.unitList)


def drawBoard(screen):
    screen.blit(BOARDART, p.Rect(0, 0, WIDTH, HEIGHT))


def drawPieces(screen, map, unitList):
    for r in range(BOARD_Y):
        for c in range(BOARD_X):
            # print(f"the vertical value is {r*SQ_SIZE+WALLSIZE}")
            index = map[r][c]
            if index != -1:
                thisUnit = unitList[index]
                thisType = thisUnit.unit_name()
                thisTeam = thisUnit.team()
                screen.blit(IMAGES[thisTeam, thisType], p.Rect(c*SQ_SIZE, r*SQ_SIZE+WALLSIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()