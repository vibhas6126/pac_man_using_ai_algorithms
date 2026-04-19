import collections
import heapq
import random

def get_neighbors(pos, grid):
    x, y = pos
    neighbors = []
    # Up, down, left, right
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
            if grid[ny][nx] != 1:  # 1 is wall
                neighbors.append((nx, ny))
    return neighbors

def bfs(start, end, grid):
    queue = collections.deque([(start, [start])])
    visited = {start}
    
    while queue:
        current, path = queue.popleft()
        if current == end:
            return path
        
        for neighbor in get_neighbors(current, grid):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []

def dfs(start, end, grid):
    stack = [(start, [start])]
    visited = {start}
    
    while stack:
        current, path = stack.pop()
        
        if current == end:
            return path
            
        for neighbor in get_neighbors(current, grid):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))
    return []

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, end, grid):
    # priority queue stores (f_score, index, current_node, path)
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start, [start]))
    
    g_score = {start: 0}
    
    while open_set:
        _, _, current, path = heapq.heappop(open_set)
        
        if current == end:
            return path
            
        for neighbor in get_neighbors(current, grid):
            tentative_g = g_score.get(current, 0) + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, end)
                count += 1
                heapq.heappush(open_set, (f_score, count, neighbor, path + [neighbor]))
    return []

def greedy(start, end, grid):
    count = 0
    open_set = []
    heapq.heappush(open_set, (heuristic(start, end), count, start, [start]))
    
    visited = {start}
    
    while open_set:
        _, _, current, path = heapq.heappop(open_set)
        
        if current == end:
            return path
            
        for neighbor in get_neighbors(current, grid):
            if neighbor not in visited:
                visited.add(neighbor)
                count += 1
                heapq.heappush(open_set, (heuristic(neighbor, end), count, neighbor, path + [neighbor]))
    return []

def flee(start, end, grid):
    neighbors = get_neighbors(start, grid)
    if not neighbors:
        return []
    
    best_neighbors = []
    max_dist = -1
    
    for n in neighbors:
        dist = heuristic(n, end)
        if dist > max_dist:
            max_dist = dist
            best_neighbors = [n]
        elif dist == max_dist:
            best_neighbors.append(n)
            
    if best_neighbors:
        return [start, random.choice(best_neighbors)]
    return [start, start]

def random_choice(start, end, grid):
    neighbors = get_neighbors(start, grid)
    if not neighbors:
        return []
    return [start, random.choice(neighbors)]

def get_next_move(start, end, grid, algo):
    """
    Returns the next position (x, y) the ghost should move to.
    """
    if start == end:
        return start
        
    path = []
    if algo == 'bfs':
        path = bfs(start, end, grid)
    elif algo == 'dfs':
        path = dfs(start, end, grid)
    elif algo == 'astar':
        path = astar(start, end, grid)
    elif algo == 'greedy':
        path = greedy(start, end, grid)
    elif algo == 'flee':
        path = flee(start, end, grid)
    elif algo == 'random':
        path = random_choice(start, end, grid)
        
    # path includes the start node [0], so next step is path[1]
    if len(path) > 1:
        return path[1]
    # No path found or already there. Try to fall back to random valid neighbor so it doesn't get stuck forever
    fallback = random_choice(start, end, grid)
    if len(fallback) > 1:
        return fallback[1]
    return start
