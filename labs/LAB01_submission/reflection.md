# Reflection: OOP Design Decisions

Write 2-3 paragraphs reflecting on your object-oriented design. Some questions to consider:

- Why did you structure your classes the way you did?
- What inheritance relationships did you use and why?
- What was challenging about managing multiple interacting objects?
- If you had more time, what would you refactor or add?
- How does this experience connect to working with OOP in analytics/ML codebases?

---

For Bottlenose, the class structure was driven by the need to encapsulate distinct behaviors, states, and properties for the different entities in the game. I utilized a base Character class to hold shared attributes like health (or "sanity"), name, and the core dice-rolling mechanics needed for encounters. From there, I used inheritance to create specific Player and Enemy subclasses. The Player class extended the base functionality to manage inventory (specifically, holding mashed potatoes) and room navigation. Meanwhile, the Enemy subclass-representing the Intern, Linguistics Researcher, and Lead Marine Biologist-incorporated specific detection thresholds and evasion modifiers. This hierarchical approach kept the code DRY and made it incredibly easy to instantiate different researcher types with unique combat behaviors without rewriting the underlying encounter logic.

Managing the interactions between multiple instantiated objects was arguably the most challenging aspect of the lab. Specifically, linking Room objects to create a navigable map and handling the state changes when the Player entered a room containing an Enemy required careful state management. Passing object instances into other objects' methods (e.g., passing a Player to an Enemy's attack method) meant I had to be hyper-aware of variable scope and ensure I wasn't creating circular dependencies. If I had more time, I would refactor the combat and movement logic by extracting it into a dedicated GameManager or EncounterSystem class. This would decouple the Room state from the game loop, making the architecture cleaner and paving the way for more dynamic mechanics, like researchers actively roaming between adjacent rooms rather than remaining static.

Ultimately, this experience closely mirrors the realities of working with OOP in analytics and machine learning codebases. Whether building custom data pipelines, structuring text-processing applications, or managing complex analytical tools, the core principles of modularity remain exactly the same. Just as a Player object must interact with a Room object through strict, well-defined methods, a custom ML model object must ingest, transform, and output data through predictable interfaces. Building this text adventure reinforced the importance of encapsulation, iterative testing, and robust state management-skills that are just as crucial for deploying reliable AI architectures as they are for navigating a bottlenose dolphin out of a flooded jacuzzi.
