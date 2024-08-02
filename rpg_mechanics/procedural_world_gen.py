import random
import os

class ProceduralWorldGen:
    def __init__(self):
        self.atmospheres = ['rain', 'sunny', 'foggy', 'night']
        self.backgrounds = ['city', 'forest', 'beach', 'mountains']
        self.music_files = ['track1.mp3', 'track2.mp3', 'track3.mp3']
        self.enemy_types = ['thug', 'ninja', 'boxer', 'biker']
        self.item_types = ['apple', 'energy_drink', 'first_aid_kit']
        self.level_layouts = [
            'linear',
            'branching',
            'hub_and_spoke',
            'maze',
            'open_world'
        ]

    def generate_world(self, num_levels=5):
        world = []
        for i in range(num_levels):
            level = self.generate_level(i)
            world.append(level)
        return world

    def generate_level(self, level_number):
        layout = random.choice(self.level_layouts)
        level = f"""(level
    (name "Level {level_number + 1}")
    (layout {layout})
    (z
        (minimum {random.randint(100, 200)})
        (maximum {random.randint(201, 300)}))
    (atmosphere {random.choice(self.atmospheres)})
    (background-parallax {round(random.uniform(1.0, 5.0), 1)})
    (background {random.choice(self.backgrounds)})
    (music "{random.choice(self.music_files)}")
    {self.generate_objects()}
)"""
        return level

    def generate_objects(self):
        objects = ""
        num_enemies = random.randint(5, 10)
        num_items = random.randint(3, 7)
        
        for _ in range(num_enemies):
            objects += self.generate_enemy()
        for _ in range(num_items):
            objects += self.generate_item()
        return objects

    def generate_enemy(self):
        enemy_type = random.choice(self.enemy_types)
        return f"""
    (object
        (type enemy)
        (id {random.randint(1, 100)})
        (name "{enemy_type.capitalize()}")
        (path "chars/{enemy_type}/{enemy_type}.txt")
        (health {random.randint(50, 100)})
        (coords {random.randint(-1000, 1000)} {random.randint(0, 100)})
    )"""

    def generate_item(self):
        item_type = random.choice(self.item_types)
        return f"""
    (object
        (type item)
        (id {random.randint(101, 200)})
        (name "{item_type}")
        (path "items/{item_type}.txt")
        (coords {random.randint(-1000, 1000)} {random.randint(0, 100)})
    )"""

    def create_world_file(self, world, filename="procedural_world.txt"):
        file_path = f"/home/ubuntu/All-American-Hustle/levels/paintown/worlds/{filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write("(world\n")
            for level in world:
                f.write(level)
            f.write(")")
        print(f"World file created successfully at {file_path}")

if __name__ == "__main__":
    world_gen = ProceduralWorldGen()
    new_world = world_gen.generate_world()
    world_gen.create_world_file(new_world)
