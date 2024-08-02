import random

class ProceduralDialogue:
    def __init__(self):
        self.templates = {
            'greeting': [
                "Hello, {player_name}! Welcome to {location}.",
                "Greetings, traveler. What brings you to {location}?",
                "Well met, {player_name}. How fares your journey?"
            ],
            'quest_offer': [
                "I need help with {quest_task}. Can you assist me?",
                "A {quest_enemy} has been causing trouble. Will you deal with it?",
                "I've lost my {quest_item}. Could you find it for me?"
            ],
            'quest_completion': [
                "Thank you for {quest_task}! Here's your reward.",
                "Excellent work dealing with that {quest_enemy}!",
                "You found my {quest_item}! I'm truly grateful."
            ],
            'shop': [
                "Welcome to my shop. What can I get for you today?",
                "Ah, a customer! Feel free to browse my wares.",
                "Looking for something specific? I might have just what you need."
            ],
            'combat': [
                "Prepare to face the wrath of {enemy_name}!",
                "You'll regret crossing paths with me, {player_name}!",
                "Let's see what you're made of, {player_name}!"
            ]
        }

    def generate_dialogue(self, dialogue_type, context):
        """
        Generate a dialogue based on the type and context.
        
        :param dialogue_type: The type of dialogue to generate (e.g., 'greeting', 'quest_offer')
        :param context: A dictionary containing context variables (e.g., {'player_name': 'Hero', 'location': 'Town'})
        :return: A generated dialogue string
        """
        if dialogue_type not in self.templates:
            return "Error: Invalid dialogue type"

        template = random.choice(self.templates[dialogue_type])
        return template.format(**context)

    def add_template(self, dialogue_type, template):
        """
        Add a new template to an existing dialogue type or create a new dialogue type.
        
        :param dialogue_type: The type of dialogue for the new template
        :param template: The new template string
        """
        if dialogue_type not in self.templates:
            self.templates[dialogue_type] = []
        self.templates[dialogue_type].append(template)

# Example usage
if __name__ == "__main__":
    dialogue_system = ProceduralDialogue()
    
    # Generate a greeting
    greeting = dialogue_system.generate_dialogue('greeting', {'player_name': 'Hero', 'location': 'Mystic Forest'})
    print(greeting)
    
    # Generate a quest offer
    quest_offer = dialogue_system.generate_dialogue('quest_offer', {'quest_task': 'defeating the dragon', 'quest_enemy': 'fierce dragon', 'quest_item': 'magical amulet'})
    print(quest_offer)
    
    # Add a new template
    dialogue_system.add_template('greeting', "Hail, {player_name}! The winds of {location} welcome you.")
    
    # Generate another greeting with the new template possibly being used
    another_greeting = dialogue_system.generate_dialogue('greeting', {'player_name': 'Warrior', 'location': 'Ancient Ruins'})
    print(another_greeting)
