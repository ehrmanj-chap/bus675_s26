class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, player, game):
        # To be overridden by subclasses (Potion, Weapon, etc.)
        print(f"You can't use the {self.name} right now.")

class Location:
    def __init__(self, name, description, is_locked=False):
        self.name = name
        self.description = description
        self.connections = {}  # e.g., {'north': server_room}
        self.items = []
        self.enemy = None
        self.is_locked = is_locked
        self.event_used = False # For things like the Break Room coffee

    def add_connection(self, direction, room):
        self.connections[direction] = room

    def get_details(self):
        print(f"\n--- {self.name} ---")
        print(self.description)
        if self.items:
            item_names = [item.name for item in self.items]
            print(f"Items here: {', '.join(item_names)}")
        if self.enemy:
            print(f"⚠️ A {self.enemy.name} is glaring at you!")
        
        exits = list(self.connections.keys())
        print(f"Exits: {', '.join(exits)}")

class Character:
    def __init__(self, name, hp, base_attack, base_defense):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.base_attack = base_attack
        self.base_defense = base_defense

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        damage_taken = max(0, amount - self.base_defense) # Armor reduces damage
        self.hp -= damage_taken
        print(f"{self.name} takes {damage_taken} damage! (HP: {max(0, self.hp)}/{self.max_hp})")
