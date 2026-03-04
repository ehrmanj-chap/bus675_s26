![](bottlenose)

BOTTLENOSE: The Official Manual
The Story
You are a bottlenose dolphin. You have been abducted by a group of well-meaning but incredibly misguided researchers who have partially flooded a suburban house to serve as a makeshift domestic marine biology and linguistics lab. They are trying to teach you English. You do not care about English. You care about the leftover mashed potatoes they cruelly ate in front of you three days ago. You know they hid the rest in a mini-fridge somewhere in this house. You must find them.

How to Play
Bottlenose is a text-based, dice-rolling adventure game. You will navigate the flooded rooms of the research facility, searching for your starchy prize while avoiding the researchers who want to study you. When confronted by a researcher, you will enter a dice-based evasion/combat sequence where you must rely on your raw dolphin instincts (and a lucky roll) to escape.

Running the Game
Since the game is built in a Jupyter Notebook (.ipynb):

Open the notebook in your environment (Jupyter, VS Code, Google Colab, etc.).

Run all the cells containing the game's class definitions (Room, Player, Enemy, etc.).

Run the final code cell containing the GameLoop or main() function.

Type your commands directly into the text input box that appears below the cell and press Enter.

Commands

go [direction] (e.g., go north, go east): Move to an adjacent flooded room.

look: Examine your current surroundings and spot obvious exits or items.

search: Dig a little deeper into the room to find hidden mini-fridges or clues.

attack / evade: Use these during an encounter with a researcher to roll the dice and attempt an escape.

eat: Consume items you find (specifically, mashed potatoes).

status: Check your current health/sanity and inventory.

quit: Exit the game.

Goals

Primary Objective: Locate the final stash of mashed potatoes, eat them, immediately roll over and die, and achieve VICTORY.

Survival Objective: Avoid being caught by the researchers. If you lose a dice encounter, you will be banished back to the Jacuzzi and awkwardly propped up against the brick, ending your run.

Tips for Survival

Know Your Enemy: The Intern is easily distracted and has weak dice rolls. The Lead Marine Biologist is highly perceptive and will likely catch you. Avoid the main kitchen if you can!

Mind Your Sanity: The Linguistics Researcher doesn't want to capture you physically; they want to force you to look at flashcards. Losing against them will drain your patience/sanity.

Map It Out: The house layout doesn't change. Remember which rooms connect to the Hallway so you don't get cornered.

