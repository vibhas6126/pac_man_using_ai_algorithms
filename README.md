# AI Pac-Man Web App

An arcade-style Pac-Man project built with Flask, PyScript, and HTML5 canvas. The player controls Pac-Man in the browser while the ghosts use backend pathfinding algorithms to decide their next move.

## Features

- Play Pac-Man in the browser with arrow keys or `W`, `A`, `S`, `D`
- Choose the ghost pathfinding strategy before starting the game
- Generated maze map for each new run
- Power pellets trigger scared mode, causing ghosts to flee
- Flask API handles map generation and ghost movement decisions
- PyScript frontend manages rendering, input, and game state in the browser

## Algorithms Included

- `BFS` - shortest-path search
- `DFS` - depth-first exploration with less predictable routes
- `A*` - heuristic-guided pathfinding
- `Greedy` - direct pursuit using heuristic distance
- `Random` - random valid movement
- `Flee` - automatically used during scared mode so ghosts move away from Pac-Man

## Tech Stack

- Python
- Flask
- PyScript
- HTML/CSS
- HTML5 Canvas

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- START_GAME.bat
|-- game_logic/
|   |-- algorithms.py
|   `-- map_data.py
|-- static/
|   |-- css/style.css
|   `-- js/frontend.py
`-- templates/
    `-- index.html
```

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the app

Option A:

```bash
python app.py
```

Option B on Windows:

```bat
START_GAME.bat
```

### 3. Open the game

Visit:

```text
http://127.0.0.1:5000
```

## How to Play

1. Launch the app and choose a ghost algorithm.
2. Click `INITIALIZE SIMULATION`.
3. Move Pac-Man using the arrow keys or `W`, `A`, `S`, `D`.
4. Collect pellets to increase score.
5. Pick up power pellets to trigger scared mode and eat ghosts for bonus points.
6. Avoid ghosts when scared mode is not active.

## How It Works

The frontend in `static/js/frontend.py` runs in the browser through PyScript. It draws the board on a canvas, handles player input, updates score, and requests ghost moves from the Flask backend.

The backend exposes two main endpoints:

- `GET /api/map` generates a fresh maze
- `POST /api/pathfind` returns the next move for each ghost based on the selected algorithm

Core logic lives in:

- `game_logic/map_data.py` for maze generation
- `game_logic/algorithms.py` for pathfinding and ghost movement

## Notes

- `requirements.txt` currently only includes Flask.
- The UI loads PyScript and Google Fonts from external CDNs, so an internet connection may be needed for full frontend styling and runtime assets.

## Future Improvements

- Add difficulty levels
- Add lives and level progression
- Track high scores
- Add sound effects and music
- Add unit tests for pathfinding and map generation

## License

No license file is currently included in this repository.
