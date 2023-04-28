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
        self.blueToMove = True
        self.moveLog = []
        self.unitList = [FootSoldier("b"), FootSoldier("b"), FootSoldier("r"), FootSoldier("r")]

    def makeMove(self, move):
        self.map[move.startRow][move.startCol] = -1
        self.map[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move for later reference
        self.blueToMove = not self.blueToMove

    # def getAllPossibleMoves(self):


class Move():
    def __init__(self, startSq, endSq, map):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = map[self.startRow][self.startCol]
        self.pieceCaptured = map[self.endRow][self.endCol]


class ArmyUnit:
    def __init__(self, **kwargs):
        self._attack_range = kwargs["attack_range"]
        self._move_range = kwargs["move_range"]
        self._hit_points = kwargs["hit_points"]
        self._max_hit_points = kwargs["max_hit_points"]
        self._team = "blue"
        self._unit_name = kwargs["unit_name"]

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
            "unit_name": "footsoldier"
        }
        super().__init__(**kwargs)
        self._team = team