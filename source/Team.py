from enum import Enum
import pygame as p

class Team(Enum):
    BLUE = 0
    RED = 1

    @staticmethod
    def to_abbreviation(color):
        abbreviations = ["b", "r"]
        return abbreviations[color.value]

    @staticmethod    
    def to_string(color):
        names = ["Blue", "Red"]
        return names[color.value]

    @staticmethod    
    def to_color(color):
        # this blue corresponds to azure
        colors = [p.Color(0, 128, 255), p.Color(255, 0, 0)]
        return colors[color.value]
    