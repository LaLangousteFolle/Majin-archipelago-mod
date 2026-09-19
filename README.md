# Majin and the Forsaken Kingdom Archipelago Mod

> An Archipelago randomizer mod for **Majin and the Forsaken Kingdom**, currently in development.

This is my first Archipelago mod and my first real game modification, so please be gentle >:3c

More seriously, I'm still very new to game modding and am currently learning my way around **Cheat Engine**. I love this game, though, and I'd absolutely love to turn it into a proper randomizer.

---

## 🗺️ Roadmap

| Status | Milestone |
|:---:|---|
| 🚧 | Reverse engineering / game research |
| ⬜ | Basic item randomization |
| ⬜ | Archipelago integration |
| ⬜ | Location / check system |
| ⬜ | Configuration & options |
| ⬜ | Testing & bug fixing |
| ⬜ | First playable release |
| ⬜ | More advanced features |
| ⬜ | ~~Become a competent modder~~ |

**Legend**

- 🚧 Currently working on
- ⬜ Planned
- ~~Cancelled / unrealistic~~

---

## 🔬 Current Focus

I'm currently working on finding where the game's items and values are stored in ROM memory. This might take a while, as I'm learning as I go.

### Currently Working On

- Locate where Tepeu EXP is stored
- Interact with Tepeu's EXP amount

### Known Issues

- The EXP amount does not update immediately when modified.
- The game only appears to recognize the new value after gaining EXP normally, such as by opening a chest or defeating an enemy.
- Once that happens, the level increase should work correctly.

---

## 🌐 APWorld

The game should have **169 checks**, currently planned as:

| Check | Amount |
|---|---:|
| Memory shards | 35 |
| EXP shard chests | 79 |
| Tepeu cosmetic chests | 18 |
| Majin cosmetic chests | 2 |
| Life fruits* | 9 |
| Strength fruits | 10 |
| Wind fruits | 3 |
| Electric fruits | 3 |
| Fire fruits | 3 |
| Purification fruits | 3 |
| Boss masks | 4 |
| **Total** | **169** |

> * Not counting the Life Fruit used to free the Majin.

---

## ✨ Optional / Future Features

Some features I'd like to implement eventually, but I currently lack the experience and knowledge required to do so:

- [ ] Randomize the main power fruit
- [ ] Add teleport rooms as locations/items
- [ ] Add fast-travel progression between zones

---

## 🔍 Possible Additional Checks

If the game supports them cleanly, these could become additional Archipelago locations:

- [ ] Animal dialogues
- [ ] Using statues for the first time
- [ ] Defeating bosses
- [ ] Defeating each enemy type
- [ ] Achievements

---

## 🎯 Goal

**Defeat the King.**

---

*This project is a work in progress. Expect bugs, questionable decisions, and an unhealthy amount of Cheat Engine.*
