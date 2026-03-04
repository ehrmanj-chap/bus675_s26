Game Design Document
Theme / Setting
Absurdist 90s indie CGI / Escape Room. The setting is a partially flooded suburban house that has been haphazardly repurposed into a makeshift marine biology and linguistics research facility. The researchers are attempting to domesticate the player (a bottlenose dolphin) and teach him English.

Player's Goal
Navigate the flooded house to locate the researchers' mini-fridges. The ultimate goal is to find and consume the leftover mashed potatoes that the researchers cruelly ate in front of the player three days prior.

Locations (4-6)

The Jacuzzi: The starting area and the player's "prison."

Flooded Living Room: A transitional space with waist-high water.

The Hallway: The central hub connecting the rest of the house.

Linguistics Lab (Bedroom): Filled with flashcards; contains a decoy or smaller mini-fridge.

The Main Kitchen: A high-traffic, dangerous area.

The Storage Closet: A hidden area attached to the kitchen containing the final stash of mashed potatoes.

Map

Plaintext
[ The Jacuzzi ] 
      |
      v
[ Flooded Living Room ]
      |
      v
[ The Hallway ] -----> [ Linguistics Lab ]
      |
      v
[ The Main Kitchen ]
      |
      v
[ Storage Closet ]
Enemies (3 types)

The Intern: * Stats/Behavior: Low perception, weak dice rolls. Easily distracted. Represents a low-level threat that introduces the player to the evasion mechanics.

Linguistics Researcher: * Stats/Behavior: Medium perception. Does not attack physical health; instead attacks the player's "patience/sanity" by aggressively showing them English language flashcards.

Lead Marine Biologist: * Stats/Behavior: High perception, very difficult to evade. Encountering them usually results in a swift capture unless the player rolls a critical success.

Win Condition
The player successfully navigates to the Storage Closet, finds the correct mini-fridge, and executes the eat mashed_potatoes command. The dolphin will immediately roll over and die from the carbs, but the screen will display a triumphant "VICTORY."

Lose Condition
The player is caught by a researcher (failing a dice-based evasion/combat encounter). The player is subsequently banished back to the Jacuzzi, awkwardly propped up against the brick wall, ending the run.

Class Hierarchy

Plaintext
Character (base class: handles name, base sanity/health, core dice-roll mechanics)
├── Player (adds inventory management, room navigation, `eat` action)
└── Enemy (adds detection thresholds, unique encounter dialogue)
    ├── Intern (low stats)
    ├── LinguisticsResearcher (sanity-damage attacks)
    └── LeadBiologist (high stats, high capture rate)

Room (handles connected rooms, descriptions, item/enemy presence)

Game (handles the main loop, command parsing, win/loss state checks)
Additional Notes

Combat System: "Combat" is actually an evasion/resistance system. When entering a room with an enemy, a dice roll (e.g., a simulated d20) modified by the enemy's stats determines if the dolphin escapes to an adjacent room or is captured.

Vibe: The tone should remain completely austere and serious, playing the absolute absurdity of a dolphin navigating a house completely straight.
