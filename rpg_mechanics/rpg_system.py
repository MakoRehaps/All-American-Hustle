from __future__ import print_function

import json
import os
import random
import tempfile

SAVE_VERSION = 2
MAX_LEVEL = 50


def _clamp(value, low, high):
    return max(low, min(high, value))


def default_save_path():
    if os.name == "nt":
        root = os.environ.get("APPDATA") or os.path.expanduser("~")
        folder = os.path.join(root, "AllAmericanHustle")
    else:
        folder = os.path.join(os.path.expanduser("~"), ".all_american_hustle")
    if not os.path.isdir(folder):
        try:
            os.makedirs(folder)
        except OSError:
            pass
    return os.path.join(folder, "save.json")


class Character(object):
    def __init__(self, name, base_health=100, base_attack=10, base_defense=0):
        self.name = name or "Fighter"
        self.level = 1
        self.experience = 0
        self.base_health = int(base_health)
        self.base_attack = int(base_attack)
        self.base_defense = int(base_defense)
        self.health = self.max_health()
        self.skill_points = 0
        self.perks = []
        self.currency = 0

    def max_health(self):
        return self.base_health + (self.level - 1) * 8

    def attack_power(self):
        return self.base_attack + (self.level - 1) * 2

    def defense(self):
        return self.base_defense + (self.level - 1) // 4

    def experience_to_next_level(self):
        if self.level >= MAX_LEVEL:
            return 0
        return 75 + (self.level * 35) + ((self.level - 1) * (self.level - 1) * 5)

    def gain_experience(self, amount):
        amount = max(0, int(amount))
        if self.level >= MAX_LEVEL or amount == 0:
            return []
        self.experience += amount
        gained = []
        while self.level < MAX_LEVEL:
            needed = self.experience_to_next_level()
            if needed <= 0 or self.experience < needed:
                break
            self.experience -= needed
            self.level += 1
            self.skill_points += 1
            self.health = self.max_health()
            gained.append(self.level)
        if self.level >= MAX_LEVEL:
            self.experience = 0
        return gained

    def heal(self, amount):
        self.health = _clamp(self.health + max(0, int(amount)), 0, self.max_health())
        return self.health

    def damage(self, amount):
        amount = max(0, int(amount) - self.defense())
        self.health = max(0, self.health - amount)
        return amount

    def is_alive(self):
        return self.health > 0

    def add_perk(self, perk):
        if perk and perk not in self.perks:
            self.perks.append(perk)
            return True
        return False

    def get_stats(self):
        return {
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "next_level": self.experience_to_next_level(),
            "health": self.health,
            "max_health": self.max_health(),
            "attack": self.attack_power(),
            "defense": self.defense(),
            "skill_points": self.skill_points,
            "perks": list(self.perks),
            "currency": self.currency,
        }

    def to_dict(self):
        return self.get_stats()

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("name", "Fighter"))
        obj.level = _clamp(int(data.get("level", 1)), 1, MAX_LEVEL)
        obj.experience = max(0, int(data.get("experience", 0)))
        obj.health = _clamp(int(data.get("health", obj.max_health())), 0, obj.max_health())
        obj.skill_points = max(0, int(data.get("skill_points", 0)))
        obj.perks = list(data.get("perks", []))
        obj.currency = max(0, int(data.get("currency", 0)))
        return obj


class Inventory(object):
    def __init__(self, capacity=40):
        self.capacity = max(1, int(capacity))
        self.items = {}

    def slots_used(self):
        return len(self.items)

    def add_item(self, item, quantity=1):
        quantity = max(0, int(quantity))
        if not item or quantity == 0:
            return False
        if item not in self.items and self.slots_used() >= self.capacity:
            return False
        self.items[item] = self.items.get(item, 0) + quantity
        return True

    def remove_item(self, item, quantity=1):
        quantity = max(0, int(quantity))
        if item not in self.items or quantity == 0 or self.items[item] < quantity:
            return False
        self.items[item] -= quantity
        if self.items[item] <= 0:
            del self.items[item]
        return True

    def has_item(self, item, quantity=1):
        return self.items.get(item, 0) >= int(quantity)

    def get_items(self):
        return dict(self.items)

    def to_dict(self):
        return {"capacity": self.capacity, "items": self.get_items()}

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("capacity", 40))
        for name, quantity in data.get("items", {}).items():
            if int(quantity) > 0:
                obj.items[name] = int(quantity)
        return obj


class Quest(object):
    def __init__(self, quest_id, name, description, objectives, xp_reward=0, cash_reward=0, item_rewards=None):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.objectives = dict(objectives)
        self.progress = dict((key, 0) for key in self.objectives)
        self.xp_reward = int(xp_reward)
        self.cash_reward = int(cash_reward)
        self.item_rewards = dict(item_rewards or {})
        self.completed = False
        self.claimed = False

    def update_progress(self, objective, amount=1):
        if self.completed or objective not in self.objectives:
            return False
        self.progress[objective] = min(self.objectives[objective], self.progress.get(objective, 0) + max(0, int(amount)))
        self.completed = all(self.progress.get(key, 0) >= required for key, required in self.objectives.items())
        return True

    def claim(self, character, inventory):
        if not self.completed or self.claimed:
            return False
        character.gain_experience(self.xp_reward)
        character.currency += self.cash_reward
        for item, quantity in self.item_rewards.items():
            inventory.add_item(item, quantity)
        self.claimed = True
        return True

    def get_status(self):
        return {
            "id": self.quest_id,
            "name": self.name,
            "description": self.description,
            "objectives": dict(self.objectives),
            "progress": dict(self.progress),
            "completed": self.completed,
            "claimed": self.claimed,
            "xp_reward": self.xp_reward,
            "cash_reward": self.cash_reward,
            "item_rewards": dict(self.item_rewards),
        }

    def to_dict(self):
        return self.get_status()

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            data.get("id", "quest"),
            data.get("name", "Quest"),
            data.get("description", ""),
            data.get("objectives", {}),
            data.get("xp_reward", 0),
            data.get("cash_reward", 0),
            data.get("item_rewards", {}),
        )
        obj.progress.update(data.get("progress", {}))
        obj.completed = bool(data.get("completed", False))
        obj.claimed = bool(data.get("claimed", False))
        return obj


DEFAULT_QUESTS = [
    Quest("street_cleanup", "Street Cleanup", "Drop 5 enemies in one run.", {"enemy_defeated": 5}, 150, 75, {"Soda": 1}),
    Quest("combo_school", "Combo School", "Land 20 attacks.", {"attack_landed": 20}, 120, 50),
    Quest("survivor", "Still Standing", "Finish a stage without being knocked out.", {"stage_survived": 1}, 200, 100, {"Med Kit": 1}),
]


class GameState(object):
    def __init__(self, player_name="Fighter"):
        self.character = Character(player_name)
        self.inventory = Inventory()
        self.quests = dict((q.quest_id, Quest.from_dict(q.to_dict())) for q in DEFAULT_QUESTS)
        self.stage = 1
        self.total_kos = 0
        self.total_attacks = 0

    def event(self, event_name, amount=1):
        amount = max(0, int(amount))
        if event_name == "enemy_defeated":
            self.total_kos += amount
        elif event_name == "attack_landed":
            self.total_attacks += amount
        for quest in self.quests.values():
            quest.update_progress(event_name, amount)
        self.claim_completed_quests()

    def claim_completed_quests(self):
        for quest in self.quests.values():
            quest.claim(self.character, self.inventory)

    def to_dict(self):
        return {
            "version": SAVE_VERSION,
            "character": self.character.to_dict(),
            "inventory": self.inventory.to_dict(),
            "quests": [quest.to_dict() for quest in self.quests.values()],
            "stage": self.stage,
            "total_kos": self.total_kos,
            "total_attacks": self.total_attacks,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("character", {}).get("name", "Fighter"))
        obj.character = Character.from_dict(data.get("character", {}))
        obj.inventory = Inventory.from_dict(data.get("inventory", {}))
        obj.quests = {}
        for quest_data in data.get("quests", []):
            quest = Quest.from_dict(quest_data)
            obj.quests[quest.quest_id] = quest
        for default in DEFAULT_QUESTS:
            if default.quest_id not in obj.quests:
                obj.quests[default.quest_id] = Quest.from_dict(default.to_dict())
        obj.stage = max(1, int(data.get("stage", 1)))
        obj.total_kos = max(0, int(data.get("total_kos", 0)))
        obj.total_attacks = max(0, int(data.get("total_attacks", 0)))
        return obj


class SaveManager(object):
    def __init__(self, path=None):
        self.path = path or default_save_path()

    def load(self, player_name="Fighter"):
        try:
            with open(self.path, "r") as handle:
                data = json.load(handle)
            return GameState.from_dict(data)
        except (IOError, OSError, ValueError, TypeError):
            return GameState(player_name)

    def save(self, state):
        folder = os.path.dirname(self.path)
        if folder and not os.path.isdir(folder):
            try:
                os.makedirs(folder)
            except OSError:
                pass
        fd, temp_path = tempfile.mkstemp(prefix="aah-save-", suffix=".json", dir=folder or None)
        try:
            handle = os.fdopen(fd, "w")
            try:
                json.dump(state.to_dict(), handle, indent=2, sort_keys=True)
            finally:
                handle.close()
            if os.path.exists(self.path):
                try:
                    os.remove(self.path)
                except OSError:
                    pass
            os.rename(temp_path, self.path)
            return True
        except (IOError, OSError):
            try:
                os.remove(temp_path)
            except OSError:
                pass
            return False


def random_perk_choices(count=3, seed=None):
    perks = [
        "Heavy Hands", "Second Wind", "Street Smart", "Fast Feet", "Iron Jaw",
        "Crowd Control", "Cheap Shot", "Adrenaline", "Combo Keeper", "Lucky Break",
    ]
    rng = random.Random(seed)
    rng.shuffle(perks)
    return perks[:max(1, min(int(count), len(perks)))]
