def build_world():
    # 1. Instantiate Rooms
    lobby = Location("The Lobby", "Fluorescent lights flicker. The receptionist's desk is covered in dust and denied PTO requests.")
    break_room = Location("The Break Room", "A smell of burnt coffee and regret hangs in the air. The espresso machine hums menacingly.")
    open_office = Location("The Open Office", "A sea of gray cubicles. You can hear the faint sound of aggressive typing.")
    server_room = Location("The Server Room", "It's freezing in here. Towers of blinking lights tower over you like monoliths.")
    hr_labyrinth = Location("The HR Labyrinth", "The carpet here is aggressively beige. The walls seem to shift when you aren't looking.")
    ceo_office = Location("The CEO's Corner Office", "Mahogany desk, panoramic windows, and pure corporate malice.", is_locked=True)

    # 2. Connect Rooms (Two-way where appropriate)
    lobby.add_connection("north", open_office)
    lobby.add_connection("south", break_room)
    
    break_room.add_connection("north", lobby)
    
    open_office.add_connection("south", lobby)
    open_office.add_connection("east", server_room)
    open_office.add_connection("north", hr_labyrinth)
    
    server_room.add_connection("west", open_office)
    
    hr_labyrinth.add_connection("south", open_office)
    hr_labyrinth.add_connection("north", ceo_office) # CEO office locked by default!

    return lobby # Returning the starting room
