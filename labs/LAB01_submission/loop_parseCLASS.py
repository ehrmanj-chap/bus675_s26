class Game:
    def __init__(self):
        self.player = Player()
        self.current_location = build_world() # From Step 2
        self.is_running = True
        
        # --- SEEDING THE WORLD ---
        # Grabbing references to the rooms based on the Lobby's connections
        break_room = self.current_location.connections["south"]
        open_office = self.current_location.connections["north"]
        server_room = open_office.connections["east"]
        hr_labyrinth = open_office.connections["north"]
        ceo_office = hr_labyrinth.connections["north"]

        # Dropping items and enemies into the rooms
        self.current_location.items.append(Weapon("Letter Opener", "A sharp, corporate blade.", 2))
        
        open_office.enemy = Minion("Calendar Wraith", 15, 3, 0, "It floats, wrapped in endless meeting invites.")
        open_office.items.append(Armor("Cufflinks of Courage", "Sparkly and defensive.", 2))
        
        server_room.items.append(KeyItem("Executive Keycard", "A gold-plated access card."))
        
        hr_labyrinth.enemy = Enemy("HR Poltergeist", 25, 4, 1, "It wields a spectral employee handbook.")
        
        ceo_office.enemy = Boss("The CEO Specter", 50, 6, 2, "A towering mass of buzzwords and malice.")

    def play(self):
        print("\n" + "="*40)
        print("          GLOAM & LEDGER LLC")
        print("="*40)
        print("You are Koi-san. You are wearing a suit.")
        print("Your gills are dry. You must clock out.")
        print("="*40)
        self.current_location.get_details()

        # THE GAME LOOP
        while self.is_running and self.player.is_alive():
            command = input("\n> ").lower().strip().split()
            if not command:
                continue

            action = command[0]
            target = " ".join(command[1:]) # Captures multi-word items like "executive keycard"

            if action in ["quit", "exit"]:
                print("You abandon your shift. HR will hear about this.")
                self.is_running = False
            elif action == "help":
                print("Commands: go [direction], look, take [item], inventory (or i), use [item], equip [item], fight, quit")
            elif action in ["look", "l"]:
                self.current_location.get_details()
            elif action in ["inventory", "i"]:
                self.show_inventory()
            elif action == "go":
                self.move(target)
            elif action == "take":
                self.take_item(target)
            elif action in ["use", "equip"]:
                self.use_item(target)
            elif action == "fight":
                self.combat()
            else:
                print("Command not recognized. The fluorescent lights buzz in disapproval.")

    def move(self, direction):
        if direction in self.current_location.connections:
            next_room = self.current_location.connections[direction]
            
            # Locked door check for the CEO Office
            if next_room.is_locked:
                has_key = any(item.name.lower() == "executive keycard" for item in self.player.inventory)
                if has_key:
                    print("\nYou swipe the Executive Keycard. The heavy oak doors unlock.")
                    next_room.is_locked = False
                else:
                    print("\nThe door is locked. You need an Executive Keycard.")
                    return
            
            self.current_location = next_room
            self.current_location.get_details()
        else:
            print("You can't go that way. There is only corporate drywall.")

    def take_item(self, target_name):
        for item in self.current_location.items:
            if item.name.lower() == target_name:
                self.player.inventory.append(item)
                self.current_location.items.remove(item)
                print(f"You put the {item.name} in your tiny briefcase.")
                return
        print(f"You don't see a '{target_name}' here.")

    def use_item(self, target_name):
        for item in self.player.inventory:
            if item.name.lower() == target_name:
                item.use(self.player, self)
                return
        print(f"You don't have a '{target_name}' in your briefcase.")

    def show_inventory(self):
        print(f"\n--- KOI-SAN STATS ---")
        print(f"HP: {self.player.hp}/{self.player.max_hp} | ATK: {self.player.attack_power} | DEF: {self.player.defense_power}")
        if not self.player.inventory:
            print("Your briefcase is empty except for some soggy crackers.")
        else:
            print("Briefcase contents:")
            for item in self.player.inventory:
                print(f"- {item.name}: {item.description}")

    def combat(self):
        enemy = self.current_location.enemy
        if not enemy:
            print("You aggressively flop your fins at the empty air. Nothing happens.")
            return
            
        print(f"\n--- COMBAT INITIATED: {enemy.name} ---")
        
        while self.player.is_alive() and enemy.is_alive():
            # Player turn
            print(f"You attack {enemy.name}!")
            enemy.take_damage(self.player.attack_power)
            
            if not enemy.is_alive():
                print(f"\nYou defeated the {enemy.name}!")
                self.current_location.enemy = None
                
                # Win Condition!
                if isinstance(enemy, Boss):
                    print("\n" + "*"*40)
                    print("                VICTORY!")
                    print("*"*40)
                    print("The CEO Specter dissolves into a cloud of buzzwords.")
                    print("He drops THE GOLDEN TIMESHEET. You stamp it.")
                    print("You are finally off the clock. Forever.")
                    self.is_running = False
                return

            # Enemy turn
            if isinstance(enemy, Boss) and enemy.hp < (enemy.max_hp / 2):
                enemy.special_ability(self.player) # The Synergy Slam!
            else:
                print(f"{enemy.name} retaliates!")
                self.player.take_damage(enemy.base_attack)

        if not self.player.is_alive():
            print("\n*** TERMINATED ***")
            print("Your HP reached 0. HR has processed your termination.")
            self.is_running = False

# --- KICK OFF THE GAME ---
if __name__ == "__main__":
    game = Game()
    game.play()
