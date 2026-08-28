from __future__ import print_function

import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
LEVEL_DIR = os.path.join(DATA, "levels", "paintown", "levels")
SCRIPT_LINE = '  (script python "levels/paintown/rpg.py")\n'


def patch_level(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    if "levels/paintown/rpg.py" in text:
        return False
    match = re.search(r"\(level\s*\n", text)
    if not match:
        raise RuntimeError("Not a Paintown level: %s" % path)
    text = text[:match.end()] + SCRIPT_LINE + text[match.end():]
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return True


def validate_required_files():
    required = [
        os.path.join(ROOT, "All American Hustle.exe"),
        os.path.join(ROOT, "SDL.dll"),
        os.path.join(ROOT, "alleg42.dll"),
        os.path.join(DATA, "scripts", "paintown.py"),
        os.path.join(DATA, "levels", "paintown", "rpg.py"),
        os.path.join(ROOT, "rpg_mechanics", "rpg_system.py"),
    ]
    missing = [path for path in required if not os.path.exists(path)]
    if missing:
        raise RuntimeError("Missing required files:\n" + "\n".join(missing))


def main():
    validate_required_files()
    if not os.path.isdir(LEVEL_DIR):
        raise RuntimeError("Missing level directory: %s" % LEVEL_DIR)
    patched = 0
    for name in sorted(os.listdir(LEVEL_DIR)):
        if name.lower().endswith(".txt"):
            if patch_level(os.path.join(LEVEL_DIR, name)):
                patched += 1
    print("All-American Hustle ready. RPG script enabled in %d level(s)." % patched)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print("PREPARE FAILED: %s" % error)
        sys.exit(1)
