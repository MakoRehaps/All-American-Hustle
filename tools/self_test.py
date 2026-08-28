from __future__ import print_function

import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from rpg_mechanics.rpg_system import GameState, SaveManager
from import_animation import balanced_end, find_anim_block


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


def test_rpg_round_trip():
    folder = tempfile.mkdtemp(prefix="aah-test-")
    try:
        path = os.path.join(folder, "save.json")
        state = GameState("Tester")
        start_level = state.character.level
        state.character.gain_experience(500)
        state.inventory.add_item("Soda", 2)
        state.event("enemy_defeated", 5)
        manager = SaveManager(path)
        assert_true(manager.save(state), "save failed")
        loaded = manager.load("Wrong Name")
        assert_true(loaded.character.name == "Tester", "player name did not persist")
        assert_true(loaded.character.level > start_level, "level did not increase")
        assert_true(loaded.inventory.has_item("Soda", 2), "inventory did not persist")
        assert_true(loaded.total_kos == 5, "KO count did not persist")
    finally:
        shutil.rmtree(folder)


def test_character_definitions():
    players = os.path.join(ROOT, "data", "players")
    definitions = 0
    for folder_name in os.listdir(players):
        folder = os.path.join(players, folder_name)
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            if not name.lower().endswith(".txt"):
                continue
            path = os.path.join(folder, name)
            with io.open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            start = text.find("(character")
            if start >= 0:
                balanced_end(text, start)
                definitions += 1
    assert_true(definitions > 0, "no player definitions found")


def test_known_animation():
    path = os.path.join(ROOT, "data", "players", "JohnDutch", "JohnDutch.txt")
    with io.open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    assert_true(find_anim_block(text, "idle") is not None, "JohnDutch idle animation missing")
    assert_true(find_anim_block(text, "attack1") is not None, "JohnDutch attack1 animation missing")


def main():
    tests = [test_rpg_round_trip, test_character_definitions, test_known_animation]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print("All %d self-tests passed." % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
