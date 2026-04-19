import asyncio
import json
from js import window, document, console, Math, Date
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

# --- UI State Management ---
selected_algorithm = 'astar'

def select_algo(e):
    global selected_algorithm
    target = e.currentTarget
    
    for btn in document.querySelectorAll('.algo-btn'):
        btn.classList.remove('selected')
        
    target.classList.add('selected')
    selected_algorithm = target.dataset.algo
    document.getElementById('current-algo').innerText = target.querySelector('.algo-title').innerText

def on_start(e):
    document.getElementById('start-screen').classList.add('hidden')
    document.getElementById('game-ui').classList.remove('hidden')
    start_game(selected_algorithm)
    
def on_restart(e):
    document.getElementById('game-over-modal').classList.add('hidden')
    start_game(selected_algorithm)

def bind_ui():
    for btn in document.querySelectorAll('.algo-btn'):
        btn.addEventListener('click', create_proxy(select_algo))
        
    document.getElementById('start-btn').addEventListener('click', create_proxy(on_start))
    document.getElementById('restart-btn').addEventListener('click', create_proxy(on_restart))

bind_ui()

# --- Game Engine Variables ---
canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")

game_state = {
    "tileSize": 20,
    "map": [],
    "score": 0,
    "gameOver": False,
    "algo": "astar",
    "pacman": {"x": 22, "y": 17, "dirX": 0, "dirY": 0, "nextDirX": 0, "nextDirY": 0},
    "ghosts": [],
    "lastTime": 0,
    "pacmanAccumulator": 0,
    "ghostAccumulator": 0,
    "pacmanInterval": 180,
    "ghostInterval": 260,
    "isFetchingPaths": False,
    "scaredMode": False,
    "scaredTimer": None
}

canvas.width = 45 * game_state["tileSize"]
canvas.height = 25 * game_state["tileSize"]

def on_keydown(e):
    keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "]
    if e.code in keys:
        e.preventDefault()
        
    pacman = game_state["pacman"]
    key = e.key
    if key in ["ArrowUp", "w", "W"]:
        pacman["nextDirX"] = 0
        pacman["nextDirY"] = -1
    elif key in ["ArrowDown", "s", "S"]:
        pacman["nextDirX"] = 0
        pacman["nextDirY"] = 1
    elif key in ["ArrowLeft", "a", "A"]:
        pacman["nextDirX"] = -1
        pacman["nextDirY"] = 0
    elif key in ["ArrowRight", "d", "D"]:
        pacman["nextDirX"] = 1
        pacman["nextDirY"] = 0

window.addEventListener('keydown', create_proxy(on_keydown), {"passive": False})

# --- Network & Data ---
async def fetch_map():
    res = await pyfetch('/api/map')
    data = await res.json()
    game_state["map"] = data["map"]
    
async def fetch_ghost_moves():
    if game_state["isFetchingPaths"]: return
    game_state["isFetchingPaths"] = True
    
    algo_to_use = "flee" if game_state["scaredMode"] else game_state["algo"]
    p = game_state["pacman"]
    
    payload = {
        "pacman": {"x": p["x"], "y": p["y"]},
        "ghosts": [{"id": g["id"], "x": g["x"], "y": g["y"]} for g in game_state["ghosts"]],
        "algo": algo_to_use
    }
    
    try:
        req = await pyfetch(
            '/api/pathfind', 
            method="POST", 
            headers={"Content-Type": "application/json"}, 
            body=json.dumps(payload)
        )
        data = await req.json()
        
        for move in data.get("moves", []):
            for g in game_state["ghosts"]:
                if g["id"] == move["id"]:
                    g["x"] = move["x"]
                    g["y"] = move["y"]
                    
        check_collisions()
    except Exception as e:
        console.error(f"Error fetching path: {e}")
    finally:
        game_state["isFetchingPaths"] = False

# --- Core Logic ---
def start_game(algo):
    game_state["algo"] = algo
    game_state["score"] = 0
    document.getElementById('score-display').innerText = "0"
    game_state["gameOver"] = False
    
    game_state["pacman"] = {"x": 22, "y": 17, "dirX": 0, "dirY": 0, "nextDirX": 0, "nextDirY": 0}
    game_state["ghosts"] = [
        {"id": 1, "x": 20, "y": 11, "color": "#ff0000"},
        {"id": 2, "x": 21, "y": 11, "color": "#ffb8ff"},
        {"id": 3, "x": 22, "y": 11, "color": "#00ffff"},
        {"id": 4, "x": 23, "y": 11, "color": "#ffb852"}
    ]
    
    game_state["scaredMode"] = False
    if game_state["scaredTimer"]:
        window.clearTimeout(game_state["scaredTimer"])
        
    async def init_and_loop():
        await fetch_map()
        game_state["lastTime"] = window.performance.now()
        window.requestAnimationFrame(create_proxy(loop))
        
    asyncio.create_task(init_and_loop())

def is_valid_move(x, y):
    m = game_state["map"]
    if y < 0 or y >= len(m) or x < 0 or x >= len(m[0]):
        return False
    return m[y][x] != 1

def end_scared():
    game_state["scaredMode"] = False

def update_pacman():
    p = game_state["pacman"]
    
    # Try next direction
    if p["nextDirX"] != 0 or p["nextDirY"] != 0:
        if is_valid_move(p["x"] + p["nextDirX"], p["y"] + p["nextDirY"]):
            p["dirX"] = p["nextDirX"]
            p["dirY"] = p["nextDirY"]
            
    # Move
    if p["dirX"] != 0 or p["dirY"] != 0:
        nxt_x = p["x"] + p["dirX"]
        nxt_y = p["y"] + p["dirY"]
        if is_valid_move(nxt_x, nxt_y):
            p["x"] = nxt_x
            p["y"] = nxt_y
            
    # Collision with map items
    m = game_state["map"]
    if p["y"] < len(m):
        cell = m[p["y"]][p["x"]]
        if cell == 0:
            m[p["y"]][p["x"]] = 3
            game_state["score"] += 10
            document.getElementById('score-display').innerText = str(game_state["score"])
        elif cell == 2:
            m[p["y"]][p["x"]] = 3
            game_state["score"] += 50
            document.getElementById('score-display').innerText = str(game_state["score"])
            
            game_state["scaredMode"] = True
            if game_state["scaredTimer"]:
                window.clearTimeout(game_state["scaredTimer"])
            game_state["scaredTimer"] = window.setTimeout(create_proxy(end_scared), 8000)
            
    check_collisions()

def show_game_over():
    document.getElementById('final-score').innerText = str(game_state["score"])
    document.getElementById('game-over-modal').classList.remove('hidden')

def check_collisions():
    p = game_state["pacman"]
    for g in game_state["ghosts"]:
        if g["x"] == p["x"] and g["y"] == p["y"]:
            if game_state["scaredMode"]:
                game_state["score"] += 200
                document.getElementById('score-display').innerText = str(game_state["score"])
                g["x"] = len(game_state["map"][0]) // 2
                g["y"] = len(game_state["map"]) // 2
            else:
                game_state["gameOver"] = True
                window.setTimeout(create_proxy(show_game_over), 100)

def draw():
    ctx.fillStyle = "#000"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    m = game_state["map"]
    if not m: return
    
    ts = game_state["tileSize"]
    
    # Draw Map
    for y in range(len(m)):
        for x in range(len(m[y])):
            val = m[y][x]
            if val == 1:
                ctx.fillStyle = '#0a192f'
                ctx.fillRect(x*ts, y*ts, ts, ts)
                ctx.strokeStyle = '#45f3ff'
                ctx.lineWidth = 1.5
                ctx.strokeRect(x*ts + 2, y*ts + 2, ts - 4, ts - 4)
            elif val == 0:
                ctx.fillStyle = '#ffb852'
                ctx.beginPath()
                ctx.arc(x*ts + ts/2, y*ts + ts/2, 3, 0, Math.PI*2)
                ctx.fill()
            elif val == 2:
                ctx.fillStyle = '#ffeb3b'
                ctx.beginPath()
                ctx.arc(x*ts + ts/2, y*ts + ts/2, 6, 0, Math.PI*2)
                ctx.fill()
                
    # Draw Pacman
    p = game_state["pacman"]
    ctx.fillStyle = '#ffeb3b'
    ctx.beginPath()
    mouth_offset = (Math.sin(Date.now() / 150) + 1) * 0.25
    base_angle = 0
    if p["dirX"] == 1: base_angle = 0
    elif p["dirX"] == -1: base_angle = Math.PI
    elif p["dirY"] == 1: base_angle = Math.PI/2
    elif p["dirY"] == -1: base_angle = -Math.PI/2
    
    ctx.arc(
        p["x"]*ts + ts/2,
        p["y"]*ts + ts/2,
        ts/2 * 0.8,
        base_angle + mouth_offset,
        base_angle + 2*Math.PI - mouth_offset
    )
    ctx.lineTo(p["x"]*ts + ts/2, p["y"]*ts + ts/2)
    ctx.fill()
    
    # Draw Ghosts
    for g in game_state["ghosts"]:
        ctx.fillStyle = '#2563eb' if game_state["scaredMode"] else g["color"]
        ctx.beginPath()
        gx = g["x"]*ts + ts/2
        gy = g["y"]*ts + ts/2
        size = ts/2 * 0.85
        
        ctx.arc(gx, gy - size*0.1, size, Math.PI, 0)
        ctx.lineTo(gx + size, gy + size)
        ctx.lineTo(gx - size, gy + size)
        ctx.fill()
        
        # Eyes
        ctx.fillStyle = '#fca5a5' if game_state["scaredMode"] else 'white'
        ctx.beginPath()
        ctx.arc(gx - size*0.4, gy - size*0.2, size*0.35, 0, Math.PI*2)
        ctx.fill()
        
        ctx.beginPath()
        ctx.arc(gx + size*0.4, gy - size*0.2, size*0.35, 0, Math.PI*2)
        ctx.fill()
        
        # Pupils
        ctx.fillStyle = '#0b0c10'
        lookX = 1 if p["x"] > g["x"] else (-1 if p["x"] < g["x"] else 0)
        lookY = 1 if p["y"] > g["y"] else (-1 if p["y"] < g["y"] else 0)
        
        if game_state["scaredMode"]:
            lookX = 1 if Math.random() > 0.5 else -1
            lookY = 1 if Math.random() > 0.5 else -1
            
        ctx.beginPath()
        ctx.arc(gx - size*0.4 + lookX*1.5, gy - size*0.2 + lookY*1.5, size*0.15, 0, Math.PI*2)
        ctx.fill()
        ctx.beginPath()
        ctx.arc(gx + size*0.4 + lookX*1.5, gy - size*0.2 + lookY*1.5, size*0.15, 0, Math.PI*2)
        ctx.fill()

def loop(time):
    if game_state["gameOver"]: return
    
    delta = time - game_state["lastTime"]
    game_state["lastTime"] = time
    
    game_state["pacmanAccumulator"] += delta
    game_state["ghostAccumulator"] += delta
    
    if game_state["pacmanAccumulator"] >= game_state["pacmanInterval"]:
        update_pacman()
        game_state["pacmanAccumulator"] = 0
        
    if game_state["ghostAccumulator"] >= game_state["ghostInterval"]:
        asyncio.create_task(fetch_ghost_moves())
        game_state["ghostAccumulator"] = 0
        
    draw()
    window.requestAnimationFrame(create_proxy(loop))
