from abc import ABC, abstractmethod

class AIModule(ABC):
    move_queue = []

    @abstractmethod
    def do_next_turn(self, map, unit_list):
        self.convert_map(map, unit_list)

    def _generate_action_space(self):
        pass

    def convert_map(self, engine_map, unit_list):
        """
        Converts the double array of pointers from the game engine (engine_map)
          into a matrix of bytes (ai_map)
        """
        ai_map = []
        for engine_row in engine_map:
            ai_row = []
            for unit_index in engine_row:
                unit = unit_list[unit_index] 
