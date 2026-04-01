# 🐉 PythonicDragons

> *"Roll for initiative."*

A text-based, choose-your-own-adventure RPG built in Python — heavily inspired by Dungeons & Dragons combat and character mechanics. This is my first unguided personal project, built from scratch after working through the [Boot.dev](https://www.boot.dev) curriculum. No tutorials, no hand-holding, just Python and stubbornness.

**This is an MVP release.** It is playable, it works, and it has enough content to show what the system is capable of. More is coming.

---

## ✨ Features

- **Turn-based combat** with initiative rolls, attack rolls, crits, hits, and misses — all narrated dynamically
- **Three playable classes** at level 2: Fighter, Wizard, and Runeblade (a martial/arcane hybrid loosely inspired by Flesh and Blood's Runeblade)
	- The Fighter and Wizard classes are adapted to fit the game engine. Runeblade is a complete homebrew.
- **D&D-style point buy** stat allocation during character creation
- **Abilities with real effects** — damage, healing, buffs, debuffs, and spell slots that are tracked and consumed
- **Skill checks** with advantage and disadvantage support in story scenes
- **Story-driven scenes** — branching narrative choices that lead to different encounters and outcomes
- **Data-driven design** — enemies, classes, and stories are all defined in JSON, making the system moddable without touching engine code
- **Short rest system** — recover HP and spell slots between encounters

---

## 🚀 Getting Started

### Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
git clone https://github.com/AggroSec/PythonicDragons.git
cd PythonicDragons
```

**With uv (recommended):**
```bash
uv sync
uv run main.py
```

**With pip:**
```bash
pip install tabulate colorama
python main.py
```

### Running Tests

```bash
bash test.sh
```

---

## 🎮 How to Play

When you launch the game you'll be walked through:

1. **Character creation** — name your character, pick a class, choose a starting weapon, and allocate your stats using the point buy system
2. **Story selection** — choose from any available stories in the `stories/` folder
3. **Adventure** — make choices at each scene. Some scenes will trigger skill checks, some trigger combat, and some just move the story forward

### Combat Commands

During your turn in combat the prompt will show your available abilities. You have a few options beyond just picking a number:

- `1`, `2`, `3`... — use that ability
- `info [num]` — show full details on an ability before committing (e.g. `info 2`)
- `status` — print your current HP, spell slots, buffs, debuffs, and usage tracking

### Story Commands

- `1`, `2`, `3`... — choose that option
- The game will tell you when a skill check is happening automatically

---

## 🗂️ Project Structure

```
.
├── data/
│   ├── classes.json        # Playable class definitions
│   └── enemies.json        # Enemy definitions
├── engine/
│   ├── character.py        # Character, Player, and EnemyNPC classes
│   ├── choice.py           # Story scene handling and skill checks
│   ├── combat.py           # Full combat engine
│   ├── dice.py             # Dice roller (advantage/disadvantage supported)
│   └── game.py             # Game loop, character creation, scene routing
├── stories/
│   └── test_story/
│       └── story.json      # The included MVP story
├── tests/
│   ├── test_character_python_classes.py
│   ├── test_combat.py
│   └── test_dice_roller.py
├── main.py
├── pyproject.toml
└── test.sh
```

---

## 🛠️ Modding

PythonicDragons is built to be moddable. The engine reads everything — classes, enemies, stories — from JSON files, so you can create entirely new content without touching a single line of Python.

A full modding wiki is planned and will cover in detail how to create your own stories with branching scenes and skill checks, define new enemy types with custom abilities, and build new playable classes with unique ability sets. For now, the existing JSON files in `data/` and `stories/` are well-structured enough to reverse engineer if you want to experiment before the wiki lands.

---

## 🗺️ Roadmap

### Full Release (`v1.0`)
- A full original story balanced for **level 2–3 characters** (playable with all three MVP classes — more challenging at level 2, better balanced at level 3)
- **3 level 3 subclasses:**
  - Champion Fighter
  - Elemental Wizard
  - Shadow Runeblade *(complete homebrew matching the vibe of Chane/Vynnset from Flesh and Blood)*
  **Note:** Champion and Elemental Wizard will again be adapted to fit the system There are just some skills that don't match the damage/heal/buff/debuff paradigm that I set up.

### Later Down the Road
- Full **modding wiki** so the community can build their own stories and classes
- Additional **inline code comments** for parts of the engine that need more explanation
- More **unit tests** for logic that doesn't require player input — because the best test for player-facing stuff is just playing the game

---

## 📄 License

MIT — do whatever you want with it, just don't blame me if your Fighter rolls a 1 at the worst possible moment.

---

*Built with Python 3.11, tabulate, and an unreasonable amount of d20 rolls.*
