import random

def generate_map(width=45, height=25):
    # Initialize with walls (1)
    grid = [[1 for _ in range(width)] for _ in range(height)]
    
    # Helper for creating paths safely within bounds
    # Using a simple recursive backtracker to carve a maze
    def carve(x, y):
        grid[y][x] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            # Check if within bounds and hitting a wall
            if 0 < nx < width-1 and 0 < ny < height-1 and grid[ny][nx] == 1:
                # Carve through the wall
                grid[y + dy//2][x + dx//2] = 0
                carve(nx, ny)

    # Start carving from a random odd node so maze logic aligns cleanly
    start_x = random.choice(range(1, width-1, 2))
    start_y = random.choice(range(1, height-1, 2))
    carve(start_x, start_y)

    # To make it more like Pac-Man (with loops instead of a perfect tree maze), 
    # we randomly knock down a significant number of walls that separate paths.
    for _ in range((width * height) // 3):
        rx = random.randint(1, width-2)
        ry = random.randint(1, height-2)
        if grid[ry][rx] == 1:
            grid[ry][rx] = 0

    # Ensure the "ghost house" area is fully clear near the center
    ghost_x_start = width // 2 - 3
    ghost_x_end = width // 2 + 3
    ghost_y_start = height // 2 - 2
    ghost_y_end = height // 2 + 2
    
    for y in range(ghost_y_start, ghost_y_end + 1):
        for x in range(ghost_x_start, ghost_x_end + 1):
            # Form a box with an opening
            if y == ghost_y_start:
                grid[y][x] = 1 # Top wall
            elif y == ghost_y_end:
                grid[y][x] = 1 # Bottom wall
            elif x == ghost_x_start or x == ghost_x_end:
                grid[y][x] = 1 # Side walls
            else:
                grid[y][x] = 0 # Empty inside
                
    # Create the top door for the ghost house
    grid[ghost_y_start][width // 2] = 0
    grid[ghost_y_start][width // 2 - 1] = 0

    # Ensure ghost spawn coordinates and pacman spawn are clear
    # Ghosts spawn around x=20-23, y=11 (which is typically around the center)
    
    # Place power pellets at corners 
    # Ensure corners are walkable first
    corners = [(1, 1), (width-2, 1), (1, height-2), (width-2, height-2)]
    for cx, cy in corners:
        grid[cy][cx] = 2
        
    # Ensure Pacman spawn at middle-bottom is clear 
    # Pacman spawns at x=22, y=17 (width//2, height//2 + 5)
    pacman_start_x = width // 2
    pacman_start_y = height // 2 + 5
    
    grid[pacman_start_y][pacman_start_x] = 0
    grid[pacman_start_y][pacman_start_x - 1] = 0
    grid[pacman_start_y][pacman_start_x + 1] = 0
    grid[pacman_start_y - 1][pacman_start_x] = 0
    grid[pacman_start_y + 1][pacman_start_x] = 0

    return grid
