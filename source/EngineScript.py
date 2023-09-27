from enum import Enum
import Anim
import GameMenu

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
        self.unit_list = [FootSoldier(Team.BLUE), FootSoldier(Team.BLUE), FootSoldier(Team.RED), FootSoldier(Team.RED)]
        self.phase = Phase.AWAITING_UNIT_SELECTION
        self.selected_unit = None
        self.selected_square = None
        self.next_move = None
        self.menu = GameMenu.GameMenu()

    def setup_still_anims(self):
        for r in range(len(self.map)):
            for c in range(len(self.map[0])):
                index = self.map[r][c]
                if index > -1:
                    this_unit = self.unit_list[index]
                    this_unit.anim = Anim.StillAnim((r, c))

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

    def get_all_moves(self):
        moves = []
        piece = self.selected_unit
        turn = piece._team
        if (turn == Team.RED and not self.blueToMove) or (turn == Team.BLUE and self.blueToMove):                                        
            moves = self.get_valid_moves(piece.move_range)
        return moves
                        
    def squareContainsUnit(self, row, col):
        return self.map[row][col] != -1

    def get_valid_moves(self, move_range): # this is super scuffed and should be made into a proper bfs
        col = self.selected_square[0]
        row = self.selected_square[1]
        moves = []
        to_seek = []
        visited = set()

        to_seek.append(((row, col), move_range))
        while to_seek:            
            q = to_seek.pop()
            sq = q[0]
            range = q[1]

            adj_list = (
                (sq[0] + 1, sq[1]), 
                (sq[0] - 1, sq[1]), 
                (sq[0], sq[1] + 1), 
                (sq[0], sq[1] - 1)
            )
            for adj in adj_list:
                if self.is_on_map(adj) and self not in visited and range - 1 >= 0:
                    to_seek.append((adj, range - 1))
                    visited.add((adj))
        for v in visited:
            moves.append(Move((row, col), (v), self.map))
        
        return moves

    def validatePair(self, r, c):
        r_in = ( r >= 0 and r < len(self.map))
        c_in = ( c >= 0 and c < len(self.map[0]))
        if not r_in or not c_in:
            return False
        no_unit = (self.map[r][c] < 0)
        return no_unit

    def square_is_occupied(self, square):
        return self.map[square[1]][square[0]] != -1

    def square_is_occupied_by_hostile(self, square, team):
        unit_index = self.map[square[1]][square[0]]
        if unit_index == -1:
            return False
        unit = self.unit_list[unit_index]
        team = unit.team
        return team == unit.team
        

    def square_can_produce(self, square):        
        return square in self.production_tiles
        
    def is_on_map(self, sq):
        width = len(self.map[0])
        height = len(self.map)

        if not (0 <= sq[0] < width):
            return False

        if not (0 <= sq[1] < height):
            return False

        return True
        
                        
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
        self._team = "b"
        self._unit_name = kwargs["unit_name"]
        self.anim = kwargs["anim"]

    def unit_name(self):
        return self._unit_name

    def team(self):
        return self._team

class FootSoldier(ArmyUnit):
    def __init__(self, team):
        kwargs = {
            "attack_range": 1,
            "move_range": 1,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "footsoldier",
            "anim": Anim.StillAnim((0, 0)),
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

class Team(Enum):
    BLUE = 0
    RED = 1

    @staticmethod
    def to_string(color):
        names = ["b", "r"]
        return names[color.value]