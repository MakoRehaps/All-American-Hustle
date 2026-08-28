from __future__ import print_function

import os
import sys

# Paintown embeds Python and imports this file as its support module. Do not create a
# window, initialize pygame, or run a standalone loop here.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from rpg_mechanics.rpg_system import SaveManager


def _internal():
    import paintown_internal
    return paintown_internal


def _safe_name(raw, fallback):
    for attr in ("getName", "name"):
        try:
            value = getattr(raw, attr)
            value = value() if callable(value) else value
            if value:
                return str(value)
        except Exception:
            pass
    return fallback


class Object(object):
    def __init__(self, raw):
        self.object = raw

    def getObject(self):
        return self.object

    def getId(self):
        return _internal().getId(self.object)

    def getX(self):
        return _internal().getX(self.object)

    def setX(self, value):
        _internal().setX(self.object, value)

    def getY(self):
        return _internal().getY(self.object)

    def setY(self, value):
        _internal().setY(self.object, value)

    def getZ(self):
        return _internal().getZ(self.object)

    def setZ(self, value):
        _internal().setZ(self.object, value)

    def getHealth(self):
        return _internal().getHealth(self.object)

    def setHealth(self, health):
        return _internal().setHealth(self.object, int(health))

    def didCollide(self, him):
        pass

    def takeDamage(self, him, damage):
        pass

    def tick(self):
        pass


class Character(Object):
    def __init__(self, raw, engine=None):
        Object.__init__(self, raw)
        self.engine = engine
        self.name = _safe_name(raw, "Enemy")

    def isPlayer(self):
        return False

    def didAttack(self, him):
        pass


class Player(Character):
    def __init__(self, raw, engine=None):
        Character.__init__(self, raw, engine)
        self.name = _safe_name(raw, "Fighter")
        self._last_engine_health = None

    def isPlayer(self):
        return True

    def getScore(self):
        return _internal().getScore(self.object)

    def increaseScore(self, amount):
        self.setScore(self.getScore() + int(amount))

    def setScore(self, score):
        _internal().setScore(self.object, int(score))

    def didAttack(self, him):
        if self.engine is None or him is None:
            return
        self.engine.on_player_attack(self, him)

    def takeDamage(self, him, damage):
        if self.engine is not None:
            self.engine.on_player_damage(self, damage)


class Engine(object):
    """Bridge between Paintown callbacks and persistent All-American Hustle state."""

    def __init__(self):
        self.world = None
        self.players = {}
        self.characters = {}
        self.defeated_ids = set()
        self.save_manager = SaveManager()
        self.state = None
        self._ticks = 0
        self._dirty = False

    def createWorld(self, world):
        self.world = world

    def levelLength(self):
        if self.world is None:
            return 0
        return _internal().levelLength(self.world)

    def findObject(self, object_id):
        if self.world is None:
            return None
        return _internal().findObject(self.world, object_id)

    def getObjects(self):
        if self.world is None:
            return []
        return _internal().getObjects(self.world)

    def getEnemies(self):
        return [obj for obj in self.getObjects() if not obj.isPlayer()]

    def getPlayers(self):
        return [obj for obj in self.getObjects() if obj.isPlayer()]

    def addCharacter(self, path, name, map_number, health, x, z):
        return _internal().addCharacter(self.world, path, name, map_number, health, x, z)

    def cacheCharacter(self, path):
        _internal().cacheCharacter(path)

    def createCharacter(self, raw):
        wrapper = Character(raw, self)
        try:
            self.characters[wrapper.getId()] = wrapper
        except Exception:
            pass
        return wrapper

    def createPlayer(self, raw):
        wrapper = Player(raw, self)
        try:
            self.players[wrapper.getId()] = wrapper
        except Exception:
            self.players[id(raw)] = wrapper

        if self.state is None:
            self.state = self.save_manager.load(wrapper.name)
        self._apply_persistent_health(wrapper)
        return wrapper

    def _apply_persistent_health(self, player):
        if self.state is None:
            return
        maximum = self.state.character.max_health()
        # Paintown character definitions remain the collision/combat source of truth;
        # progression supplies a larger persistent health pool without moving actors.
        try:
            engine_health = player.getHealth()
            if engine_health > 0:
                player.setHealth(min(maximum, max(engine_health, self.state.character.health)))
                self.state.character.health = player.getHealth()
        except Exception:
            pass

    def on_player_attack(self, player, target):
        if self.state is None:
            return
        self.state.event("attack_landed", 1)
        self._dirty = True
        try:
            target_id = target.getId()
            target_health = target.getHealth()
        except Exception:
            return

        if target_health <= 0 and target_id not in self.defeated_ids:
            self.defeated_ids.add(target_id)
            self.state.event("enemy_defeated", 1)
            # KO reward scales gently with the player's level.
            self.state.character.gain_experience(20 + self.state.character.level * 2)
            self.state.character.currency += 5
            try:
                player.increaseScore(100)
            except Exception:
                pass
            self._dirty = True

    def on_player_damage(self, player, damage):
        if self.state is None:
            return
        try:
            current = player.getHealth()
        except Exception:
            current = self.state.character.health - int(damage)
        self.state.character.health = max(0, int(current))
        self._dirty = True

    def stage_completed(self):
        if self.state is None:
            return
        self.state.event("stage_survived", 1)
        self.state.stage += 1
        self.state.character.heal(max(15, self.state.character.max_health() // 4))
        self._dirty = True
        self.save()

    def save(self):
        if self.state is not None and self.save_manager.save(self.state):
            self._dirty = False
            return True
        return False

    def tick(self):
        self._ticks += 1
        if self.state is None:
            return

        # Mirror real engine health into the persistent record, but never move the
        # player or fabricate quest progress. The previous script did both each tick.
        for player in list(self.players.values()):
            try:
                health = int(player.getHealth())
            except Exception:
                continue
            if health >= 0 and health != self.state.character.health:
                self.state.character.health = min(health, self.state.character.max_health())
                self._dirty = True

        # Autosave about every 10 seconds at a typical 60-Hz game tick.
        if self._dirty and self._ticks % 600 == 0:
            self.save()


engines = []


def register(engine):
    engines.append(engine)


def checkEngine():
    if not engines:
        raise Exception("No Paintown script engine was registered")


def createCharacter(character):
    checkEngine()
    return engines[0].createCharacter(character)


def createPlayer(player):
    checkEngine()
    return engines[0].createPlayer(player)


def createWorld(world):
    checkEngine()
    for engine in engines:
        engine.createWorld(world)


def tick():
    checkEngine()
    for engine in engines:
        engine.tick()
