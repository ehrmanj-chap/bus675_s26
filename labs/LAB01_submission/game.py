"""
BOTTLENOSE: The Escape Room
A Text-Based Adventure RPG
"""

import random
import time

# =============================================================================
# BASE CLASSES
# =============================================================================

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, player, game):
        print(f"You nudge the {self.name} with your snout. It doesn't do anything.")


class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  
        self.items = []
        self.enemy = None

    def add_connection(self, direction, room):
        self.connections[direction] = room

    def get_details(self):
        print(f"\n{'='*50}")
        print(f"📍 {self.name}")
        print(f"{'='*50}")
        print(self.description)
        
        if self.items:
            item_names = [item.name for item in self.items]
            print(f"\nItems here: {', '.join(item_names)}")
        if self.enemy:
            print(f"\n⚠️ WARNING: A {self.enemy.name} is in the room!")
        
        exits = list(self.connections.keys())
        print(f"\nExits: {', '.join(exits)}")


class Character:
    def __init__(self, name, health, base_attack, base_defense):
        self.name = name
        self.health = health
        self.max_health = health
        self.base_attack = base_attack
        self.base_defense = base_defense

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        damage_taken = max(0, amount - self.base_defense) 
        self.health -= damage_taken
        print(f"💥 {self.name} takes {damage_taken} sanity damage! (Sanity: {max(0, self.health)}/{self.max_health})")

# =============================================================================
# DERIVED CLASSES (ITEMS & CHARACTERS)
# =============================================================================

class MashedPotatoes(Item):
    def __init__(self, name, description):
        super().__init__(name, description)

    def use(self, player, game):
        print(f"🐬 You rapidly consume the {self.name}.")
        game.state = Game.VICTORY
        game.game_running = False

class Player(Character):
    def __init__(self):
        super().__init__("Bottlenose", 20, 5, 2) 
        self.inventory = []

    def attack(self, target):
        roll = random.randint(1, 20) + self.base_attack
        print(f"You roll a {roll} to evade!")
        if roll > target.base_defense:
            print(f"Success! You outmaneuver the {target.name}!")
            return True
        else:
            print(f"Failure! The {target.name} blocks your path.")
            return False

class Enemy(Character):
    def __init__(self, name, health, attack, defense, description):
        super().__init__(name, health, attack, defense)
        self.description = description

    def special_ability(self, player):
        pass 


class Intern(Enemy):
    def __init__(self):
        super().__init__("Intern", 10, 2, 8, "They are looking at their phone and clearly don't want to be here.")

class LinguisticsResearcher(Enemy):
    def __init__(self):
        super().__init__("Linguistics Researcher", 15, 6, 12, "They are holding up a flashcard with the letter 'A' on it.")
        
    def special_ability(self, player):
        print(f"   🗣️ The Linguistics Researcher yells, 'Say APPLE! A-P-P-L-E!' It hurts your brain.")

class LeadBiologist(Enemy):
     def __init__(self):
        super().__init__("Lead Marine Biologist", 30, 8, 16, "They have a clipboard and a very determined look in their eyes.")

# =============================================================================
# WORLD BUILDER
# =============================================================================

def build_world():
    # 1. Instantiate Rooms
    jacuzzi = Location("The Jacuzzi", "The water is warm, but the vibes are terrible. You are propped against the brick.")
    living_room = Location("Flooded Living Room", "Waist-high water covers the carpet. A soggy sofa floats nearby.")
    hallway = Location("The Hallway", "A central hub. The water is murky here.")
    lab = Location("Linguistics Lab", "Filled with waterproof flashcards. There is a small mini-fridge in the corner.")
    kitchen = Location("The Main Kitchen", "Pots and pans float by. It smells like danger and researchers.")
    storage = Location("Storage Closet", "A dark, damp closet attached to the kitchen.")

    # 2. Connect Rooms 
    jacuzzi.add_connection("south", living_room)
    living_room.add_connection("north", jacuzzi)
    living_room.add_connection("south", hallway)
    hallway.add_connection("north", living_room)
    hallway.add_connection("east", lab)
    hallway.add_connection("south", kitchen)
    lab.add_connection("west", hallway)
    kitchen.add_connection("north", hallway)
    kitchen.add_connection("south", storage)
    storage.add_connection("north", kitchen)

    # 3. Populate Items and Enemies
    lab.items.append(Item("Decoy Fridge", "It just contains sparkling water. Useless."))
    lab.enemy = LinguisticsResearcher()
    
    living_room.enemy = Intern()
    
    kitchen.enemy = LeadBiologist()
    
    storage.items.append(MashedPotatoes("Mashed Potatoes", "Cold, starchy, and exactly what you've been waiting for."))

    return jacuzzi 

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

class Game:
    EXPLORING = "exploring"
    VICTORY = "victory"
    
    def __init__(self):
        self.player = Player()
        self.current_location = build_world() 
        self.game_running = True
        self.state = Game.EXPLORING

    def play(self):
        print("\n" + "="*50)
        print("                BOTTLENOSE")
        print("="*50)
        print("You are a bottlenose dolphin in a flooded house.")
        print("You want the mashed potatoes.")
        print("="*50)
        time.sleep(1)
        self.current_location.get_details()

        while self.game_running and self.player.is_alive():
            command = input("\n> ").lower().strip().split()
            if not command:
                continue

            action = command[0]
            target = " ".join(command[1:]) 

            if action in ["quit", "exit"]:
                print("You decide the potatoes aren't worth it and go to sleep.")
                self.game_running = False
            elif action == "help":
                print("📜 Commands: go [direction], look, take [item], search, inventory (or i), eat [item], evade, quit")
            elif action in ["look", "l", "search"]:
                self.current_location.get_details()
            elif action in ["inventory", "i"]:
                self.show_inventory()
            elif action == "go":
                self.move(target)
            elif action == "take":
                self.take_item(target)
            elif action == "eat":
                self.use_item(target)
            elif action in ["evade", "attack"]:
                self.combat()
            else:
                print("You click excitedly, but nothing happens.")
                
        if self.state == Game.VICTORY:
             print("\n" + "*"*50)
             print("                VICTORY!")
             print("*"*50)
             print("You devour the leftover mashed potatoes.")
             print("The sheer amount of carbohydrates instantly overwhelms your dolphin physiology.")
             print("You roll over and die.")
             print("It was totally worth it.")
             

    def move(self, direction):
        if self.current_location.enemy:
             print("You can't leave! You must 'evade' the researcher first!")
             return
             
        if direction in self.current_location.connections:
            self.current_location = self.current_location.connections[direction]
            self.current_location.get_details()
        else:
            print("You bump your snout into a wall. You can't go that way.")

    def take_item(self, target_name):
        for item in self.current_location.items:
            if item.name.lower() == target_name:
                self.player.inventory.append(item)
                self.current_location.items.remove(item)
                print(f"🐬 You carefully balance the {item.name} on your snout.")
                return
        print(f"You don't see a '{target_name}' here.")

    def use_item(self, target_name):
        for item in self.player.inventory:
            if item.name.lower() == target_name:
                item.use(self.player, self)
                return
        # Also check room items so you can eat it straight off the ground
        for item in self.current_location.items:
            if item.name.lower() == target_name:
                item.use(self.player, self)
                return
        print(f"You don't have a '{target_name}' to eat.")

    def show_inventory(self):
        print(f"\n--- DOLPHIN STATS ---")
        print(f"Sanity: {self.player.health}/{self.player.max_health}")
        
        print("\n--- INVENTORY ---")
        if not self.player.inventory:
            print("You are carrying nothing.")
        else:
            for item in self.player.inventory:
                print(f"- {item.name}: {item.description}")

    def combat(self):
        enemy = self.current_location.enemy
        if not enemy:
            print("You splash water everywhere. There is no one to evade.")
            return
            
        print(f"\n" + "!"*50)
        print(f"      EVASION INITIATED: {enemy.name.upper()}!")
        print("!"*50)
        
        success = self.player.attack(enemy)
        
        if success:
            print(f"\nYou successfully slip past the {enemy.name}!")
            self.current_location.enemy = None
            return
            
        time.sleep(1) 

        # --- ENEMY TURN ---
        print(f"\n--- {enemy.name} reacts! ---")
        if isinstance(enemy, LinguisticsResearcher):
            enemy.special_ability(self.player)
            
        self.player.take_damage(enemy.base_attack)
        
        if not self.player.is_alive():
             self.game_running = False
             print("\n" + "X"*50)
             print("                 CAPTURED")
             print("X"*50)
             print("Your sanity has reached 0.")
             print("You have been dragged back to the Jacuzzi and awkwardly propped up against the brick wall.")
             print("The run is over.")


if __name__ == "__main__":
    game = Game()
    game.play()
