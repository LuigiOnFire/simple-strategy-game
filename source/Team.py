from enum import Enum

class Team(Enum):
    BLUE = 0
    RED = 1

    @staticmethod
    def to_string(color):
        names = ["b", "r"]
        return names[color.value]