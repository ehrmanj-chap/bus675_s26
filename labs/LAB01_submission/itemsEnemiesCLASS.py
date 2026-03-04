# --- ITEMS ---

class Potion(Item):
    def __init__(self, name, description, heal_amount):
        super().__init__(name, description)
        self.heal_amount = heal_amount

    def use(self, player, game):
        player.hp = min(player.hp + self.heal_amount, player.max_hp)
        print(f"You chug the {self.name}. You recover {self.heal_amount} HP! (HP: {player.hp}/{player.max_hp})")
        player.inventory.remove(self) # Consumed

class Weapon(Item):
    def __init__(self, name, description, attack_bonus):
        super().__init__(name, description)
        self.attack_bonus = attack_bonus

    def use(self, player, game):
        player.equipped_weapon = self
        print(f"You equip the {self.name}. Your fins feel deadly.")

class Armor(Item):
    def __init__(self, name, description, defense_bonus):
        super().__init__(name, description)
        self.defense_bonus = defense_bonus

    def use(self, player, game):
        player.equipped_armor = self
        print(f"You equip the {self.name}. Your suit integrity increases!")

class KeyItem(Item):
    def __init__(self, name, description):
        super().__init__(name, description)

    def use(self, player, game):
        # We will check this logic in the game loop when trying to go north to the CEO office
        print(f"You hold up the {self.name}. It gleams with bureaucratic authority.")


# --- CHARACTERS ---

class Player(Character):
    def __init__(self):
        # Name: Koi-san, 30 HP, 5 Base Attack, 0 Base Defense
        super().__init__("Koi-san", 30, 5, 0) 
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None

    @property # Dynamically calculates total attack
    def attack_power(self):
        bonus = self.equipped_weapon.attack_bonus if self.equipped_weapon else 0
        return self.base_attack + bonus

    @property # Dynamically calculates total defense
    def defense_power(self):
        bonus = self.equipped_armor.defense_bonus if self.equipped_armor else 0
        return self.base_defense + bonus

class Enemy(Character):
    def __init__(self, name, hp, attack, defense, description):
        super().__init__(name, hp, attack, defense)
        self.description = description

    def special_ability(self, player):
        # Default enemies don't have one, subclasses will override this!
        pass 

class Minion(Enemy):
    def special_ability(self, player):
        # 20% chance to Meeting Invite (stun) - logic handled in combat loop
        print(f"{self.name} sends a 'Quick Chat' calendar invite! It's super effective!")

class Boss(Enemy):
    def special_ability(self, player):
        if self.hp < (self.max_hp / 2):
            print(f"{self.name} uses SYNERGY SLAM! They are pivoting to a hostile takeover!")
            player.take_damage(self.base_attack + 5)
