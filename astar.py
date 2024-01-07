import heapq

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0  # Cost from the start node to this node
        self.h = 0  # Heuristic (estimated cost from this node to the goal)
        self.parent = None  # Parent node

    def __lt__(self, other):
        # Comparison function for heapq
        return (self.g + self.h) < (other.g + other.h)

    def __eq__(self, other):
        # Equality comparison for nodes
        return self.x == other.x and self.y == other.y

def heuristic(node, goal):
    # Simple Manhattan distance as the heuristic
    return abs(node.x - goal.x) + abs(node.y - goal.y)

def get_neighbors(grid, node):
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        x, y = node.x + dx, node.y + dy
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
            if grid[y][x] == 0:  # Check if the cell is walkable
                neighbors.append(Node(x, y))
    return neighbors

def astar(grid, start, goal):
    open_set = []
    closed_set = set()

    heapq.heappush(open_set, start)

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.x == goal.x and current_node.y == goal.y:
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]

        closed_set.add((current_node.x, current_node.y))

        for neighbor in get_neighbors(grid, current_node):
            if (neighbor.x, neighbor.y) in closed_set:
                continue

            if neighbor not in open_set or neighbor.g < current_node.g + 1:
                neighbor.g = current_node.g + 1
                neighbor.h = heuristic(neighbor, goal)
                neighbor.parent = current_node

                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)

    return []
