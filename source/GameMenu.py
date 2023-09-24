class GameMenu():    
    self.buttons = []

class Button():
    self.icon = None # p.image.load("Sprites/[ASSET_NAME]") UNIMPLEMENTED
    self.text = None
    self.priority = None

# attack
class AttackButton(Button):
    def __init__:
        # self.icon = BLA
        self.text = "Attack"
        self.priority = 0

# wait
class WaitButton(Button):
    def __init__:
        # self.icon = p.image.load()
        self.text = "Wait"
        self.priorit = 1

# cancel
class CancelButton(Button):