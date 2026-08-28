# All-American Hustle – Working Build Guide

## Play on Windows

Use `run_game.bat` in the repository root. The launcher performs the required preparation step and then starts the existing Paintown-based executable.

The preparation step:

- checks that the EXE, required DLLs, Paintown script bridge, RPG module, and shared level RPG script exist;
- adds `(script python "levels/paintown/rpg.py")` to every Paintown stage exactly once;
- stops instead of launching if the install is incomplete.

You can run the preparation step manually with:

```text
python tools/prepare_game.py
```

## RPG System

`rpg_mechanics/rpg_system.py` now provides the persistent game-side systems:

- player level and XP, up to level 50;
- health, attack, and defense scaling;
- skill points and perks;
- currency;
- inventory with capacity and quantities;
- quest objectives, completion, and rewards;
- persistent save/load using JSON;
- automatic quest reward claiming;
- autosave through the Paintown script bridge.

On Windows the save file is stored at:

```text
%APPDATA%\AllAmericanHustle\save.json
```

This avoids save failures when the game directory is read-only.

## Paintown Integration

`data/scripts/paintown.py` is an embedded-engine bridge, not a standalone Pygame application. It must not open its own window or fake player actions.

Each stage loads `data/levels/paintown/rpg.py`, which registers the All-American Hustle engine with Paintown. The bridge records real combat callbacks, mirrors player health into persistent state, awards progression, and saves periodically.

Paintown upstream documents this level-script registration model in `scripting.txt`.

## Import AI / Rendered Animation Frames

The animation importer accepts a folder containing ordered PNG frames and installs it into an existing fighter.

Example:

```text
python tools/import_animation.py JohnDutch walk C:\frames\walk --delay 6
```

Attack example:

```text
python tools/import_animation.py JohnDutch attack1 C:\frames\attack1 --delay 4 --key key_attack1 --range 60 --damage 5 --attack-frame 4
```

The importer will:

1. find the character under `data/players/<character>`;
2. sort the source PNG sequence naturally;
3. copy it into the action directory as `01.png`, `02.png`, etc.;
4. find the matching `(anim ...)` block in the Paintown character definition;
5. replace that block, or append a new one if the action does not already exist;
6. optionally create a basic attack box that can then be hand-tuned.

This lets AI-generated or rotoscoped frame sequences become normal Paintown actions without manually renaming every image or rewriting the animation block.

## Validation

Run:

```text
python tools/self_test.py
```

The tests verify RPG save/load, progression, inventory persistence, character-definition parenthesis integrity, and known JohnDutch animation blocks.

GitHub Actions also runs:

- `tools/self_test.py`;
- `tools/prepare_game.py`;
- Python syntax compilation;
- CMake configure;
- CMake preparation target.

## CMake

The repository contains the prebuilt Windows game runtime. There is no local `src/*.cpp` engine tree, so CMake no longer tries to compile an imaginary executable target.

Instead it validates/prepares the real game and can package the EXE, DLLs, data, RPG module, tools, and launcher.

Typical validation build:

```text
cmake -S . -B build
cmake --build build
```

## Character Data

Current player folders include custom fighters such as `ArnoldBacks`, `JohnDutch`, and `StevenStegals`, along with other existing Paintown player data. Their normal Paintown text definitions remain the source of truth for animation offsets, collision boxes, attack boxes, damage, sounds, and combo sequences.

For exact combat feel, use the animation importer for the bulk frame conversion and then tune attack boxes/offsets in the resulting character definition.
