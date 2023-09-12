class StillAnim:
    pass

class MovingAnim:
    def __init__(self, ref_square):
        self.timer = 0
        self.end_time = 10 # this will be a design parameter
        self.ref_square = ref_square