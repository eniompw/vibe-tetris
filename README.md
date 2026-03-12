# 🎮 Tetris

A classic Tetris game built with Python and Pygame, featuring modern gameplay mechanics and polished visuals.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Pygame](https://img.shields.io/badge/Pygame-2.x-green)

## Features

- **Ghost Piece** — transparent drop shadow shows where the piece will land
- **Hold Piece** — stash the current piece and swap it back later (once per drop)
- **Level System** — speed increases as you clear more lines
- **Wall Kicks** — rotation nudges pieces away from walls/obstacles automatically
- **Line Clear Animation** — cleared rows flash before disappearing
- **Pause** — freeze the game at any time
- **Resizable Window + Fullscreen** — play windowed, resize freely, or toggle fullscreen with F11
- **Standard Tetris Scoring** — singles, doubles, triples, and Tetrises with level multiplier

## Requirements

- Python 3.x
- Pygame 2.x
- (*Optional*) Pygbag (for WebAssembly/browser support)

## Installation

```bash
# Core requirements for Desktop
pip install pygame

# Optional: To build and run in the browser
pip install pygbag
```

## How to Play

### 🖥️ Desktop Player
Run the game locally like any standard Python script:
```bash
python main.py
```

### 🌐 Web Browser (WASM)
This game has been fully updated with `asyncio` to run natively in your web browser. To launch the web version of the game:

```bash
pygbag main.py
```
*Note: If you run this in a remote environment like GitHub Codespaces, you may need to run `cd build/web && python3 -m http.server 8080`, and make sure your forwarded port is set to **Public** to avoid CORS issues.*

## Deployment (Vercel)

This repository comes pre-configured to be easily deployed as a web application via [Vercel](https://vercel.com).

1. Push your code to GitHub.
2. Log into Vercel and click **Add New** -> **Project**.
3. Import your GitHub repository.
4. Keep all default configurations (Vercel will automatically read the included `vercel.json` and `build.sh`).
5. Click **Deploy**.

Vercel will install Pygbag, compile the game to WebAssembly, and host the web version on a live public URL!

## Controls

| Key | Action |
|---|---|
| ← → | Move piece left / right |
| ↑ | Rotate |
| ↓ | Soft drop (+1 point per cell) |
| Space | Hard drop (+2 points per cell) |
| C | Hold piece |
| P / Esc | Pause / Unpause |
| F11 | Toggle fullscreen |
| R | Restart (after game over) |

## Scoring

| Lines Cleared | Points |
|---|---|
| 1 (Single) | 100 × level |
| 2 (Double) | 300 × level |
| 3 (Triple) | 500 × level |
| 4 (Tetris) | 800 × level |

Level increases every 10 lines cleared. Higher levels mean faster piece drops.
