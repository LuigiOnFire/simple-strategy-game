import anim

class ArmyUnit:
    def __init__(self, **kwargs):
        self.attack_range = kwargs["attack_range"]
        self.attack_power = kwargs["attack_power"]
        self.move_range = kwargs["move_range"]
        self.hit_points = kwargs["hit_points"]
        self._max_hit_points = kwargs["max_hit_points"]
        self.cost = kwargs["max_hit_points"]
        self._team = "b"
        self._unit_name = kwargs["unit_name"]
        self.anim = kwargs["anim"]
        self.is_active = True

    def unit_name(self):
        return self._unit_name

    def team(self):
        return self._team

class FootSoldier(ArmyUnit):
    cost = 2

    def __init__(self, team):
        kwargs = {
            "attack_range": 1,
            "attack_power": 2,
            "move_range": 2,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "footsoldier",
            "anim": anim.StillAnim(None),
        }
        super().__init__(**kwargs)
        self._team = team


class Lancer(ArmyUnit):
    cost = 4

    def __init__(self, team):
        kwargs = {
            "attack_range": 2,
            "attack_power": 2,
            "move_range": 2,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "lancer",
            "anim": anim.StillAnim(None),
        }
        super().__init__(**kwargs)
        self._team = team


class Armored(ArmyUnit):
    cost = 4

    def __init__(self, team):
        kwargs = {
            "attack_range": 1,
            "attack_power": 2,
            "move_range": 2,
            "hit_points": 1,
            "max_hit_points": 2,
            "unit_name": "armored",
            "anim": anim.StillAnim(None),
        }
        super().__init__(**kwargs)
        self._team = team


class Archer(ArmyUnit):
    cost = 4

    def __init__(self, team):
        kwargs = {
            "attack_range": 4,
            "attack_power": 1,
            "move_range": 2,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "archer",
            "anim": anim.StillAnim(None),
        }
        super().__init__(**kwargs)
        self._team = team


class Knight(ArmyUnit):
    cost = 4 

    def __init__(self, team):
        kwargs = {
            "attack_range": 1,
            "attack_power": 2,
            "move_range": 4,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "knight",
            "anim": anim.StillAnim(None),
        }
        super().__init__(**kwargs)
        self._team = team

class Door(ArmyUnit):
    def __init__(self, team, side):
        kwargs = {
            "attack_range": 0,
            "attack_power": 0,
            "move_range": 0,
            "hit_points": 1,
            "max_hit_points": 1,
            "unit_name": "door",
            "anim": anim.StillAnim(None),
        }
        super().__init__(**kwargs)

        # this is to be 'left' or 'right'
        # it should technically be an enum but idc
        self.side = side
        self._unit_name = self._unit_name + "_" + side
        self._team = team