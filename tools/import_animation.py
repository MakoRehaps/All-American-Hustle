from __future__ import print_function

import argparse
import io
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAYERS = os.path.join(ROOT, "data", "players")


def png_frames(folder):
    names = [name for name in os.listdir(folder) if name.lower().endswith(".png")]
    def natural_key(name):
        return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", name)]
    return sorted(names, key=natural_key)


def balanced_end(text, start):
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        ch = text[index]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("Unbalanced character definition")


def find_anim_block(text, action):
    cursor = 0
    needle = '(name "%s")' % action
    while True:
        start = text.find("(anim", cursor)
        if start < 0:
            return None
        end = balanced_end(text, start)
        if needle in text[start:end]:
            return (start, end)
        cursor = end


def build_animation(character_folder, action, frame_count, delay, offset_x, offset_y, key=None,
                    range_value=None, damage=None, attack_frame=None):
    lines = ["  (anim", '    (name "%s")' % action]
    if key:
        lines.append("    (keys %s)" % key)
    if range_value is not None:
        lines.append("    (range %d)" % int(range_value))
    lines.append("    (basedir players/%s/%s/)" % (character_folder, action))
    lines.append("    (delay %.1f)" % float(delay))
    lines.append("    (offset %d %d)" % (int(offset_x), int(offset_y)))
    for index in range(1, frame_count + 1):
        if damage is not None and attack_frame == index:
            lines.extend([
                "    (attack",
                "      (box",
                "        (x1 35)",
                "        (y1 10)",
                "        (x2 90)",
                "        (y2 55)",
                "        (force 2.0 3.5)",
                "        (damage %d)))" % int(damage),
            ])
        lines.append("    (frame %02d.png)" % index)
        if damage is not None and attack_frame == index:
            lines.append("    (attack)")
    lines[-1] += ")"
    return "\n".join(lines)


def resolve_definition(character_folder):
    folder = os.path.join(PLAYERS, character_folder)
    if not os.path.isdir(folder):
        raise IOError("Unknown player folder: %s" % character_folder)
    txt = [name for name in os.listdir(folder) if name.lower().endswith(".txt")]
    if not txt:
        raise IOError("No character definition found in %s" % folder)
    exact = character_folder + ".txt"
    name = exact if exact in txt else sorted(txt)[0]
    return folder, os.path.join(folder, name)


def install_frames(source, target):
    frames = png_frames(source)
    if not frames:
        raise IOError("No PNG frames in %s" % source)
    if not os.path.isdir(target):
        os.makedirs(target)
    for old in os.listdir(target):
        if old.lower().endswith(".png"):
            os.remove(os.path.join(target, old))
    for index, name in enumerate(frames, 1):
        shutil.copy2(os.path.join(source, name), os.path.join(target, "%02d.png" % index))
    return len(frames)


def apply_animation(definition_path, action, block):
    with io.open(definition_path, "r", encoding="utf-8") as handle:
        text = handle.read()
    found = find_anim_block(text, action)
    if found:
        start, end = found
        text = text[:start] + block + text[end:]
    else:
        last = text.rfind(")")
        if last < 0:
            raise ValueError("Invalid character definition")
        text = text[:last] + "\n" + block + "\n" + text[last:]
    with io.open(definition_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Import an AI/rendered PNG sequence into a Paintown fighter.")
    parser.add_argument("character", help="Folder under data/players, for example JohnDutch")
    parser.add_argument("action", help="Animation name, for example walk or attack1")
    parser.add_argument("source", help="Folder containing ordered PNG frames")
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--offset-x", type=int, default=0)
    parser.add_argument("--offset-y", type=int, default=0)
    parser.add_argument("--key", default=None, help="Paintown key token, e.g. key_attack1")
    parser.add_argument("--range", dest="range_value", type=int, default=None)
    parser.add_argument("--damage", type=int, default=None)
    parser.add_argument("--attack-frame", type=int, default=None)
    args = parser.parse_args(argv)

    source = os.path.abspath(args.source)
    if not os.path.isdir(source):
        parser.error("Source folder does not exist: %s" % source)
    player_dir, definition = resolve_definition(args.character)
    target = os.path.join(player_dir, args.action)
    count = install_frames(source, target)
    attack_frame = args.attack_frame
    if args.damage is not None and attack_frame is None:
        attack_frame = max(1, (count + 1) // 2)
    if attack_frame is not None and not 1 <= attack_frame <= count:
        parser.error("--attack-frame must be between 1 and %d" % count)

    block = build_animation(args.character, args.action, count, args.delay,
                            args.offset_x, args.offset_y, args.key,
                            args.range_value, args.damage, attack_frame)
    apply_animation(definition, args.action, block)
    print("Installed %d frame(s) into %s and updated %s" % (count, target, definition))
    return 0


if __name__ == "__main__":
    sys.exit(main())
