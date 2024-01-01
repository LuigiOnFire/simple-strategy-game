from abc import ABC, abstractmethod

class AIModule(ABC):
    move_queue = []

    @abstractmethod
    def do_next_turn(self, map, unit_list):
        self.convert_map(map, unit_list)

        # once the map is converted, generate the action space        

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
                # our format shall be
                # [unit_type][team][hp]
                type_code = unit.abbrev
                team = unit.team
                team_code = team.to_abbreviation()
                hp = unit.hp
                code = f"{type_code}{team_code}{hp}"
                ai_row.append(code)