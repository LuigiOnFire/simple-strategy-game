"""Contains animations for units and other game objects"""
CONST_ATTACK_DURATION = 10

class StillAnim():
    """Animation for a still unit"""
    def __init__(self, square=None):
        self.square = square
    
class MovingAnim:
    def __init__(self, duration, start_square, end_square):
        self.timer = 0
        self.duration = duration
        self.start_square = start_square
        self.end_square = end_square
        
class AttackAnim:
    def __init__(self, square):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant
        self.square = square

class DamageAnim:
    def __init__(self, square):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant
        self.square = square

class TakingDamageAnim:
    def __init__(self, square):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant
        self.square = square

class TurnBannerAnim:
    def __init__(self, team):        
        self.timer = 0
        self.duration = 60
        self.team = team
