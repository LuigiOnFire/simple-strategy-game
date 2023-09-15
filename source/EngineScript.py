from enum import Enum
import Anim

class GameState():
    def __init__(self):
        # 000 - empty
        # f* - foot soldier
        # h* - horse soldier
        # a* - armored soldier
        # k* - armored horse soldier (knight)
        # *s - sword
        # *l - spear/lance
        # *b - bow
        self.map = [
            [-1, -1, -1, 0, 1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, 2, 3, -1, -1, -1],
        ] 
        self.production_tiles = [(0, 0), (0, 1),(0, 2) ,(0, 3), (0, 4), (0, 5), (0, 6), (0, 7), 
                                (1, 0), (1, 1),(1, 2) ,(1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
        self.blueToMove = True
        self.moveLog = []
        self.unitList = [FootSoldier("b"), FootSoldier("b"), FootSoldier("r"), FootSoldier("r")]
        self.phase = Phase.AWAITING_UNIT_SELECTION
        self.selected_unit = None
        self.selected_square = None

    def makeMove(self, move):
        self.map[move.startRow][move.startCol] = -1
        self.map[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move for later reference
        self.blueToMove = not self.blueToMove    
    
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.map[move.startRow][move.startCol] = move.pieceMoved
            self.map[move.endRow][move.endCol] = move.pieceCaptured

    def getAllMoves(self):
        moves = []        
        for r in range(len(self.map)):
            for c in range(len(self.map[r])):
                unitIndex = self.map[r][c]
                if unitIndex != -1:
                    piece = self.unitList[unitIndex]
                    turn = piece.team
                    if (turn == "red" and not self.blueToMove) or (turn == "blue" and self.blueToMove):                                        
                        moves = getValidMoves(r, c, piece._move_range)
        return moves
                        
    def squareContainsUnit(self, row, col):
        return self.map[row][col] != -1

    def getValidMoves(self, row, col, move_range):
        moves = []
        for i in range(1, move_range + 1):
            for j in range(1, move_range + 1):
                rt = row + j
                ct = col + (i - j)
                if self.validatePair(rt, ct):
                    moves.append((Move((row, col), (rt, ct), self.map)))
                rt = row + (i - j)
                ct = col + j
                if self.validatePair(rt, ct):
                    moves.append((Move((row, col), (rt, ct), self.map)))
                rt = row - j
                ct = col - (i - j)
                if self.validatePair(rt, ct):
                    moves.append((Move((row, col), (rt, ct), self.map)))
                rt = row + (i - j)
                ct = col - j
                if self.validatePair(rt, ct):
                    moves.append((Move((row, col), (rt, ct), self.map)))
        return moves

    def validatePair(self, r, c):
        r_in = ( r >= 0 and r < len(self.map))
        c_in = ( c >= 0 and c < len(self.map[0]))
        if not r_in or not c_in:
            return False
        no_unit = (self.map[r][c] < 0)
        return no_unit
                        
    # for each 1 to move range
        # look at the pair (row + j, col + (move_range - j))
            # make sure no part of that goes over max or min
        # look at the pair (row - j, col + (move_range - j))
            # 


class Move():
    def __init__(self, startSq, endSq, map):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = map[self.startRow][self.startCol]
        self.pieceCaptured = map[self.endRow][self.endCol]
        self.moveID = self.startRow * pow(11, 3) + self.startCol * pow(11, 2) + self.endRow * 11 + self.endCol * 1

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    

class ArmyUnit:
    def __init__(self, **kwargs):
        self.attack_range = kwargs["attack_range"]
        self.move_range = kwargs["move_range"]
        self._hit_points = kwargs["hit_points"]
        self._max_hit_points = kwargs["max_hit_points"]
        self._team = "blue"
        self._unit_name = kwargs["unit_name"]
        self.anim = kwargs["anim"]

    def unit_name(self):
        return self._unit_name

    def team(self):
        return self._team # team should really be an enum

class FootSoldier(ArmyUnit):
    def __init__(self, team):
        kwargs = {
            "attack_range": 1,
            "move_range": 1,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "footsoldier",
            "anim": Anim.StillAnim(),            
        }
        super().__init__(**kwargs)
        self._team = team        

class Phase(Enum):
    AWAITING_UNIT_SELECTION = 0
    UNIT_SELECTED = 1
    ANIMATING_MOVE = 2
    AWAITING_MENU_INSTRUCTION = 3
    SELECTING_TARGET = 4
    ANIMATING_INSTRUCTION = 5
    TURN_TRANSITION = 6