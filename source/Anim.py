CONST_ATTACK_DURATION = 10

class StillAnim:
    pass

class MovingAnim:
    def __init__(self, duration, ref_square):
        self.timer = 0
        self.duration = duration
        self.ref_square = ref_square

class AttackAnim:
    def __init__(self, ref_square):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant
        self.ref_square = ref_square

class DamageAnim:
    def __init__(self, ref_square):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant    
