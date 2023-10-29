from enum import Enum
import anim
import game_menu
from team import Team

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
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1,  0,  1,  2,  3, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1,  4,  5,  6,  7, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
        ]
        self.production_tiles = {
                               Team.BLUE: [(0, 0), (1, 0), (2, 0) ,(3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                               Team.RED: [(11, 0), (11, 0),(12, 0) ,(13, 0), (14, 0), (15, 0), (16, 0), (17, 0)]
                                  }
        self.blue_to_move = True
        self.moveLog = []
        self.unit_list = [FootSoldier(Team.BLUE), FootSoldier(Team.BLUE), FootSoldier(Team.BLUE), FootSoldier(Team.BLUE),
                          FootSoldier(Team.RED), FootSoldier(Team.RED), FootSoldier(Team.RED), FootSoldier(Team.RED)]
        self.phase = Phase.TURN_TRANSITION
        self.selected_unit = None
        self.selected_unit_index = None
        self.selected_square = []
        self.dest_square = []
        self.target_square = []
        self.next_move = None
        self.menu = game_menu.GameMenu()
        # self.buy_menu = game_menu.GameMenu()
        self.valid_moves = []
        self.found_hostiles = []
        self.banner_anim = anim.TurnBannerAnim(Team.BLUE)

    def setup_still_anims(self):
        for r in range(len(self.map)):
            for c in range(len(self.map[0])):
                index = self.map[r][c]
                if index > -1:
                    this_unit = self.unit_list[index]
                    this_unit.anim = anim.StillAnim((r, c))

    def makeMove(self, move):
        self.map[move.startRow][move.startCol] = -1
        self.map[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move for later reference

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.map[move.startRow][move.startCol] = move.pieceMoved
            self.map[move.endRow][move.endCol] = move.pieceCaptured

    def squareContainsUnit(self, row, col):
        return self.map[row][col] != -1

    def update_valid_moves(self, unit):
        move_range = unit.move_range
        col = self.selected_square[0]
        row = self.selected_square[1]
        to_seek = []
        visited = set()
        valid_squares = [(col, row)]
        team = unit.team()

        to_seek.append(((col, row), move_range))
        visited.add((col, row))
        while to_seek:            
            q = to_seek.pop()
            sq = q[0]
            check_range = q[1]

            adj_list = (
                (sq[0] + 1, sq[1]), 
                (sq[0] - 1, sq[1]), 
                (sq[0], sq[1] + 1), 
                (sq[0], sq[1] - 1)
            )
            for adj in adj_list: # need to add make sure that square is not occupied by hostile
                if self.is_on_map(adj) and self not in visited and check_range - 1 >= 0:
                    if not self.square_is_occupied_by_hostile(adj, team):
                        to_seek.append((adj, check_range - 1))
                    if not self.square_is_occupied(adj):
                        valid_squares.append(adj)
                    visited.add((adj))
        self.valid_moves = valid_squares

    def find_in_range_hostiles(self):   # currently does not support any minimum range
                                        # would need a substantial refactoring
        unit = self.selected_unit
        attack_range = unit.attack_range
        col = self.dest_square[0]
        row = self.dest_square[1]
        to_seek = []
        visited = set()
        self.found_hostiles = []
        team = unit.team()

        to_seek.append(((col, row), attack_range))
        visited.add((col, row))
        while to_seek:
            q = to_seek.pop()
            sq = q[0]
            check_range = q[1]

            adj_list = (
                (sq[0] + 1, sq[1]), 
                (sq[0] - 1, sq[1]), 
                (sq[0], sq[1] + 1), 
                (sq[0], sq[1] - 1)
            )

            for adj in adj_list:
                if self.is_on_map(adj) and self not in visited and check_range - 1 >= 0:
                    to_seek.append((adj, check_range - 1))
                    if self.square_is_occupied_by_hostile(adj, team):
                        self.found_hostiles.append(adj)
                    visited.add((adj))


    def validatePair(self, r, c):
        r_in = ( r >= 0 and r < len(self.map))
        c_in = ( c >= 0 and c < len(self.map[0]))
        if not r_in or not c_in:
            return False
        no_unit = self.map[r][c] < 0
        return no_unit


    def square_is_occupied(self, square):
        # needs IF list is in range (where is this coming from?)
        return self.map[square[1]][square[0]] != -1


    def square_is_occupied_by_hostile(self, square, active_team):
        unit_index = self.map[square[1]][square[0]]
        if unit_index == -1:
            return False
        unit = self.unit_list[unit_index]
        # active_team = Team.BLUE if self.blue_to_move == true else Team.RED
        return active_team != unit.team()


    def square_is_occupied_by_other(self, square, this_unit):
        unit_index = self.map[square[1]][square[0]]
        if unit_index == -1:
            return False
        other_unit = self.unit_list[unit_index]
        return not this_unit == other_unit


    def square_can_produce(self, square):
        active_team = self.get_active_team()
        active_production_tiles = self.production_tiles[active_team]
        return square in active_production_tiles


    def prep_buy_menu(self):
        self.menu = game_menu.GameMenu()
        self.menu.buttons.append(game_menu.BuyFootSoldierButton())
        self.menu.buttons.append(game_menu.CancelButton())


    def is_on_map(self, sq):
        width = len(self.map[0])
        height = len(self.map)

        if not 0 <= sq[0] < width:
            return False

        if not 0 <= sq[1] < height:
            return False

        return True


    def reset_select(self):
        self.selected_square = None
        self.selected_unit = None
        self.selected_unit_index = None
        self.dest_square = None


    def transition_to_awaiting_unit_selection(self):
        self.phase = Phase.AWAITING_UNIT_SELECTION


    def transition_to_turn_transition(self):
        team = Team.BLUE if self.blue_to_move else Team.RED
        self.blue_to_move = not self.blue_to_move
        self.refresh_all_units()
        self.phase = Phase.TURN_TRANSITION
        self.banner_anim = anim.TurnBannerAnim(team)


    def transition_to_selecting_target(self):
        self.phase = Phase.SELECTING_TARGET
        self.find_in_range_hostiles()


    def transition_to_animating_instruction(self):
        self.menu = game_menu.GameMenu()
        self.phase = Phase.ANIMATING_INSTRUCTION


    def transition_from_selecting_target_to_awaiting_menu_instruction(self):
        self.phase = Phase.AWAITING_MENU_INSTRUCTION


    def prep_end_menu(self): # Move to engine TODO
        self.phase = Phase.AWAITING_MENU_INSTRUCTION
        self.menu = game_menu.GameMenu()
        self.menu.buttons.append(game_menu.CancelButton())
        self.menu.buttons.append(game_menu.EndTurnButton())


    def refresh_all_units(self):
        for unit in self.unit_list:
            unit.is_active = True

    def unit_has_active_team(self, unit):
        active_team = self.get_active_team()
        return unit.team() == active_team


    def get_active_team(self):
        return Team.BLUE if self.blue_to_move else Team.RED


class Move():
    def __init__(self, startSq, endSq, map):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = map[self.startRow][self.startCol]
        self.pieceCaptured = map[self.endRow][self.endCol]
        self.moveID = (
            self.startRow * pow(11, 3) +
            self.startCol * pow(11, 2) +
            self.endRow * 11 +
            self.endCol * 1
        )

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


class ArmyUnit:
    def __init__(self, **kwargs):
        self.attack_range = kwargs["attack_range"]
        self.move_range = kwargs["move_range"]
        self.hit_points = kwargs["hit_points"]
        self._max_hit_points = kwargs["max_hit_points"]
        self._team = "b"
        self._unit_name = kwargs["unit_name"]
        self.anim = kwargs["anim"]
        self.is_active = True

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
            "anim": anim.StillAnim((0, 0)),
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
    AWAITNIG_UNIT_PURCHASE = 7
