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
    def __init__(self, start_square, ref_square, SQ_SIZE):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant
        self.start_square = start_square
        self.ref_square = ref_square
        self.dist = SQ_SIZE / 4

        x_dir = self.get_direction("x", start_square, ref_square)
        y_dir = self.get_direction("y", start_square, ref_square)

        self.x_base = x_dir * self.dist
        self.y_base = y_dir * self.dist


    def get_current_offset(self):
        """Gets the offset from the unit's current square at which it is to be animated"""
        half_time = CONST_ATTACK_DURATION / 2

        if self.timer <= half_time:
            time_scale = self.timer / half_time

        else:
            time_scale = 1 - (self.timer - half_time) / half_time # Error in the arithmetic here

        x_offset = self.x_base * time_scale
        y_offset = self.y_base * time_scale

        return (x_offset, y_offset)

    def increment_timer(self):
        """Increments the timer by one tick"""
        self.timer += 1

    @staticmethod
    def get_direction(dimension, start_square, ref_square):
        """Indicates which direction we should animate the unit in"""
        if dimension == "x":
            ind = 0
        else:
            ind = 1        
        if start_square[ind] < ref_square[ind]:
            return 1
        if start_square[ind] == ref_square[ind]:
            return 0
        if start_square[ind] > ref_square[ind]:
            return -1


class TakingDamageAnim:
    def __init__(self, square):
        self.timer = 0
        self.duration = CONST_ATTACK_DURATION # this will be a constant
        self.square = square

    def get_alpha_offset(self):
        half_time = self.duration / 2
        diff = abs(self.timer - half_time)
        scale = diff / half_time

        return scale * 255

    def increment_timer(self):
        """Increments the timer by one tick"""
        self.timer += 1

class TurnBannerAnim:
    def __init__(self, team):
        self.timer = 0
        self.duration = 60
        self.team = team
