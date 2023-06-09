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
                print(f"{playerClicks}")
                col = location[0] // SQ_SIZE
                row = (location[1] - WALLSIZE) // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2: #player has made two different clicks
                    move = EngineScript.Move(playerClicks[0], playerClicks[1], gs.map)
                    gs.makeMove(move)
                    sqSelected = ()
                    playerClicks = []


        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)
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