from flask import Flask, render_template, request, jsonify
from game_logic.algorithms import get_next_move
from game_logic.map_data import generate_map

app = Flask(__name__)
current_map = generate_map()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/map')
def get_map():
    global current_map
    current_map = generate_map()
    return jsonify({"map": current_map})

@app.route('/api/pathfind', methods=['POST'])
def pathfind():
    data = request.json
    ghosts = data.get('ghosts', [])
    pacman = data.get('pacman', {'x': 1, 'y': 1})
    algo = data.get('algo', 'bfs')

    moves = []
    # Only calculate new moves if necessary, though doing it per request is fast enough via python.
    for ghost in ghosts:
        next_pos = get_next_move((ghost['x'], ghost['y']), (pacman['x'], pacman['y']), current_map, algo)
        moves.append({
            'id': ghost.get('id'),
            'x': next_pos[0] if next_pos else ghost['x'],
            'y': next_pos[1] if next_pos else ghost['y']
        })

    return jsonify({"moves": moves})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
