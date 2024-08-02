class Character:
    def __init__(self, name, base_health=100, base_attack=10):
        self.name = name
        self.level = 1
        self.experience = 0
        self.base_health = base_health
        self.base_attack = base_attack
        self.health = base_health
        self.attack = base_attack

    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.experience_to_next_level():
            self.level_up()

    def experience_to_next_level(self):
        return self.level * 100

    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level()
        self.base_health += 10
        self.base_attack += 2
        self.health = self.base_health
        self.attack = self.base_attack
        print(f"{self.name} leveled up to level {self.level}!")

    def get_stats(self):
        return {
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "health": self.health,
            "attack": self.attack
        }

class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, item, quantity=1):
        if item in self.items:
            self.items[item] += quantity
        else:
            self.items[item] = quantity

    def remove_item(self, item, quantity=1):
        if item in self.items:
            self.items[item] -= quantity
            if self.items[item] <= 0:
                del self.items[item]

    def get_items(self):
        return self.items

class Quest:
    def __init__(self, name, description, objectives):
        self.name = name
        self.description = description
        self.objectives = objectives
        self.progress = {objective: 0 for objective in objectives}
        self.completed = False

    def update_progress(self, objective, amount=1):
        if objective in self.objectives:
            self.progress[objective] += amount
            if self.progress[objective] >= self.objectives[objective]:
                self.progress[objective] = self.objectives[objective]
            self.check_completion()

    def check_completion(self):
        self.completed = all(self.progress[obj] >= self.objectives[obj] for obj in self.objectives)
        if self.completed:
            print(f"Quest '{self.name}' completed!")

    def get_status(self):
        return {
            "name": self.name,
            "description": self.description,
            "progress": self.progress,
            "completed": self.completed
        }

# Example usage:
if __name__ == "__main__":
    # Create a character
    player = Character("Hero")

    # Level up the character
    player.gain_experience(150)
    print(player.get_stats())

    # Create an inventory and add items
    inventory = Inventory()
    inventory.add_item("Health Potion", 3)
    inventory.add_item("Sword", 1)
    print(inventory.get_items())

    # Create a quest
    quest = Quest("Defeat Goblins", "Defeat 5 goblins in the forest", {"goblins_defeated": 5})

    # Update quest progress
    quest.update_progress("goblins_defeated", 3)
    print(quest.get_status())
    quest.update_progress("goblins_defeated", 2)
    print(quest.get_status())
