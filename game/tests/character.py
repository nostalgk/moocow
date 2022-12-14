class character:
    def __init__(self):
        self.strength = None
        self.dexterity = None
        self.endurance = None
        self.intelligence = None
        self.perception = None
        self.willpower = None
        
    def heal(self, num):
        heal = num
        print("You are healed for " + str(num) + " damage")
        return heal
    
    def msg(self, message):
        print(message)
        return