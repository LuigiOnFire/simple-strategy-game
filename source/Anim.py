"""Contains animations for units and other game objects"""
import pygame as p

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
        scale = 1- diff / half_time

        return scale * 255

    def increment_timer(self):
        """Increments the timer by one tick"""
        self.timer += 1

class DeathAnim:
    duration = 20 # this will be a constant
    def __init__(self):
        self.timer = 0

    def get_alpha_offset(self):
        scale = 1 - self.timer / DeathAnim.duration

        return scale * 255

    def increment_timer(self):
        """Increments the timer by one tick"""
        self.timer += 1

class DoorExplodingAnim:
    durations = [40, 80]
    x_pixels = 16
    y_pixels = 12
    shard_cols = x_pixels / 1.5
    shard_rows = y_pixels / 1.5
    def __init__(self):
        self.timer = 0
        self.phase = 0

        shards = []

        for x in range (1, DoorExplodingAnim.shard_cols):
            for y in range (1, DoorExplodingAnim.shard_rows):
                
                shard.offset = (
                    DoorExplodingAnim.x_pixels * x / DoorExplodingAnim.shard_rows,
                    DoorExplodingAnim.y_pixels * y / DoorExplodingAnim.shard_cols
                )
                shards.append


    def get_alpha_offset(self):
        scale = 1 - self.timer / DoorExplodingAnim.durations[0]

        return scale * 255    

    def increment_timer(self):
        """Increments the timer by one tick"""
        self.timer += 1



    def advance_phase(self):
        self.phase = 1


class TurnBannerAnim:
    def __init__(self, team):
        self.timer = 0
        self.duration = 60
        self.team = team

        p.image.load("Sprites/field.png")

class CoinAnim:
    coin_sprite_0 = p.image.load("Sprites/coin_0.png")
    coin_sprite_1 = p.image.load("Sprites/coin_1.png")
    coin_sprite_2 = p.image.load("Sprites/coin_2.png")

    def __init__(self):
        self.timer = 0
        self.duration = 10


    def increment_timer(self):
        """Increments the timer by one tick"""
        self.timer += 1


    def get_sprite(self, SQ_SIZE):
        """Gets the right phase of the coinsprite animation depending on the timer"""
        # 0 1 2 1 0
        sprite = None
        if self.timer % 2 == 1:
            sprite = CoinAnim.coin_sprite_1

        elif self.timer % 4 == 0:
            sprite = CoinAnim.coin_sprite_0

        elif self.timer % 4 == 2:
            sprite = CoinAnim.coin_sprite_2

        return p.transform.scale(sprite, (SQ_SIZE / 2, SQ_SIZE / 2))

    def get_current_offset(self):
        return 0 # for now, later we'll make it slowly rise
        