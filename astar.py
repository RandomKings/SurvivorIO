import heapq

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0  # Cost from the start node to this node
        self.h = 0  # Heuristic (estimated cost from this node to the goal)
        self.parent = None  # Parent node

    def __lt__(self, other):
        # Comparison function for heapq, used to prioritize nodes with lower total cost (g + h)
        return (self.g + self.h) < (other.g + other.h)

    def __eq__(self, other):
        # Equality comparison for nodes
        return self.x == other.x and self.y == other.y

def heuristic(node, goal):
    # Simple Manhattan distance as the heuristic
    return abs(node.x - goal.x) + abs(node.y - goal.y)

def get_neighbors(grid, node):
    # Get neighboring nodes that are walkable based on the grid
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        x, y = node.x + dx, node.y + dy
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
            if grid[y][x] == 0:  # Check if the cell is walkable (0 represents walkable)
                neighbors.append(Node(x, y))
    return neighbors

def astar(grid, start, goal):
    open_set = []  # Priority queue to keep track of nodes to be explored
    closed_set = set()  # Set to keep track of nodes that have been explored

    heapq.heappush(open_set, start)  # Add the start node to the open set

    while open_set:
        current_node = heapq.heappop(open_set)  # Get the node with the lowest total cost (g + h)

        if current_node.x == goal.x and current_node.y == goal.y:
            # Reconstruct and return the path if the goal is reached
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]  # Reverse the path to get it from start to goal

        closed_set.add((current_node.x, current_node.y))  # Mark the current node as explored

        for neighbor in get_neighbors(grid, current_node):
            if (neighbor.x, neighbor.y) in closed_set:
                # Skip neighbors that have already been explored
                continue

            if neighbor not in open_set or neighbor.g < current_node.g + 1:
                # Update the neighbor's cost and parent if it's not in the open set or a better path is found
                neighbor.g = current_node.g + 1
                neighbor.h = heuristic(neighbor, goal)
                neighbor.parent = current_node

                if neighbor not in open_set:
                    # Add the neighbor to the open set if it's not already there
                    heapq.heappush(open_set, neighbor)

    return []  # Return an empty list if no path is found
