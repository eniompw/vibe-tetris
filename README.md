# 🎮 Tetris

A classic Tetris game built with Python and Pygame, featuring modern gameplay mechanics and polished visuals.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Pygame](https://img.shields.io/badge/Pygame-2.x-green)

## Features

- **Ghost Piece** — transparent drop shadow shows where the piece will land
- **Hold Piece** — stash the current piece and swap it back later
- **Level System** — speed increases as you clear more lines
- **Wall Kicks** — rotation nudges pieces away from walls/obstacles automatically
- **Line Clear Animation** — cleared rows flash before disappearing
- **Pause** — freeze the game at any time
- **Standard Tetris Scoring** — singles, doubles, triples, and Tetrises with level multiplier

## Requirements

- Python 3.x
- Pygame 2.x

## Installation

```bash
pip install pygame
```

## How to Play

```bash
python tetris.py
```

## Controls

| Key | Action |
|---|---|
| ← → | Move piece left / right |
| ↑ | Rotate |
| ↓ | Soft drop (+1 point per cell) |
| Space | Hard drop (+2 points per cell) |
| C | Hold piece |
| P / Esc | Pause / Unpause |
| R | Restart (after game over) |

## Scoring

| Lines Cleared | Points |
|---|---|
| 1 (Single) | 100 × level |
| 2 (Double) | 300 × level |
| 3 (Triple) | 500 × level |
| 4 (Tetris) | 800 × level |

Level increases every 10 lines cleared. Higher levels mean faster piece drops.
