import random
import os

class ProceduralLevelCreator:
    def __init__(self):
        self.atmospheres = ['rain', 'sunny', 'foggy', 'night']
        self.backgrounds = ['city', 'forest', 'beach', 'mountains']
        self.music_files = ['track1.mp3', 'track2.mp3', 'track3.mp3']
        self.enemy_types = ['thug', 'ninja', 'boxer', 'biker']
        self.item_types = ['apple', 'energy_drink', 'first_aid_kit']

    def generate_level(self):
        level = f"""(level
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
        for _ in range(random.randint(5, 10)):
            objects += self.generate_enemy()
        for _ in range(random.randint(3, 7)):
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

    def create_level_file(self, level_number):
        level_content = self.generate_level()
        file_path = f"/home/ubuntu/All-American-Hustle/levels/paintown/levels/{level_number}.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(level_content)
        print(f"Level {level_number} created successfully at {file_path}")

if __name__ == "__main__":
    creator = ProceduralLevelCreator()
    creator.create_level_file(random.randint(1, 100))
