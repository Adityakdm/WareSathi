import pygame
import heapq
import sys
import random

CELL_SIZE = 40
GRID_WIDTH = 25
GRID_HEIGHT = 20
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE + 50
FPS = 30

WHITE = (236, 240, 241)     
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)      
RACK_COLOR = (211, 84, 0)   
BROWN = (139, 69, 19)       
GREEN = (39, 174, 96)       
RED = (192, 57, 43)         
YELLOW = (241, 196, 15)     
LIGHT_BLUE = (173, 216, 230)
PRODUCT_COLOR = (241, 196, 15) 
DARK_BG = (52, 73, 94)      

pygame.init()
try:
    GLOBAL_FONT = pygame.font.SysFont("Segoe UI", 16, bold=True)
    UI_FONT = pygame.font.SysFont("Segoe UI", 20, bold=True)
except:
    GLOBAL_FONT = pygame.font.Font(None, 24)
    UI_FONT = pygame.font.Font(None, 28)

INITIAL_POS = (0, 0)
OBSTACLES = set()
DEBRIS = set()
PRODUCTS = {}

for x in range(3, GRID_WIDTH - 3, 5):
    for y in range(3, GRID_HEIGHT - 3):
        if y != GRID_HEIGHT // 2 and y != GRID_HEIGHT // 2 + 1: 
            OBSTACLES.add((x, y))
            OBSTACLES.add((x+1, y))

empty_spaces = []
for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):
        if (x, y) not in OBSTACLES and (x, y) != INITIAL_POS:
            empty_spaces.append((x, y))

random.shuffle(empty_spaces)

for i in range(8):
    pos = empty_spaces[i]
    PRODUCTS[pos] = True

for i in range(8, 48): 
    pos = empty_spaces[i]
    DEBRIS.add(pos)

def astar(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = []

    while frontier:
        _, current = heapq.heappop(frontier)
        
        if current not in explored:
            explored.append(current)

        if current == goal:
            break

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_node = (current[0] + dx, current[1] + dy)
            
            if 0 <= next_node[0] < GRID_WIDTH and 0 <= next_node[1] < GRID_HEIGHT:
                if next_node not in OBSTACLES: 
                    step_cost = 15 if next_node in DEBRIS else 1
                    new_cost = cost_so_far[current] + step_cost
                    
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + abs(goal[0] - next_node[0]) + abs(goal[1] - next_node[1])
                        heapq.heappush(frontier, (priority, next_node))
                        came_from[next_node] = current
                        
    path = []
    if goal in came_from:
        curr = goal
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
        path.append(start)
        path.reverse()
        
    return path, explored

def draw_grid(screen):
    screen.fill(WHITE)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)
            
    for pit in DEBRIS:
        rect = pygame.Rect(pit[0] * CELL_SIZE, pit[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, BROWN, rect)
        
    for obs in OBSTACLES:
        rect = pygame.Rect(obs[0] * CELL_SIZE, obs[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RACK_COLOR, rect)
        pygame.draw.rect(screen, BLACK, rect, 1) 
        
    for p_pos in PRODUCTS:
        rect = pygame.Rect(p_pos[0] * CELL_SIZE + 6, p_pos[1] * CELL_SIZE + 6, CELL_SIZE - 12, CELL_SIZE - 12)
        pygame.draw.rect(screen, PRODUCT_COLOR, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        
        p_label = GLOBAL_FONT.render("P", True, BLACK)
        screen.blit(p_label, (p_pos[0] * CELL_SIZE + CELL_SIZE//2 - p_label.get_width()//2, p_pos[1] * CELL_SIZE + 10))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simplified A* Robot - Warehouse Mode")
    clock = pygame.time.Clock()
    
    robot_pos = INITIAL_POS
    target_pos = None
    path = []
    explored_nodes = []
    
    animating_search = False
    animating_path = False
    search_index = 0
    path_index = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not animating_search and not animating_path:
                mx, my = pygame.mouse.get_pos()
                if my < HEIGHT - 50: 
                    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                    if (gx, gy) not in OBSTACLES: 
                        target_pos = (gx, gy)
                        path, explored_nodes = astar(robot_pos, target_pos)
                        animating_search = True
                        search_index = 0
                        path_index = 0
        
        draw_grid(screen)
        
        for i in range(min(search_index, len(explored_nodes))):
            node = explored_nodes[i]
            if node != robot_pos and node != target_pos and node not in DEBRIS and node not in OBSTACLES and node not in PRODUCTS:
                rect = pygame.Rect(node[0] * CELL_SIZE + 2, node[1] * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(screen, LIGHT_BLUE, rect)
                
        if animating_path or (not animating_search and len(path) > 0):
            for i in range(min(path_index, len(path))):
                node = path[i]
                if node != INITIAL_POS and node != target_pos:
                    rect = pygame.Rect(node[0] * CELL_SIZE + 10, node[1] * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
                    pygame.draw.rect(screen, YELLOW, rect)
                    
        if animating_search:
            search_index += 5 
            if search_index >= len(explored_nodes):
                animating_search = False
                animating_path = True
                
        elif animating_path:
            if path_index < len(path):
                robot_pos = path[path_index]
                path_index += 1
                pygame.time.delay(60) 
            else:
                animating_path = False
                if not animating_path and robot_pos in PRODUCTS:
                    del PRODUCTS[robot_pos]
                
        if target_pos:
            pygame.draw.rect(screen, GREEN, (target_pos[0] * CELL_SIZE + 4, target_pos[1] * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8), 3)
            
        robot_center = (robot_pos[0] * CELL_SIZE + CELL_SIZE//2, robot_pos[1] * CELL_SIZE + CELL_SIZE//2)
        pygame.draw.circle(screen, RED, robot_center, CELL_SIZE//2 - 6)
        pygame.draw.circle(screen, WHITE, robot_center, 4) 
        
        pygame.draw.rect(screen, DARK_BG, (0, HEIGHT - 50, WIDTH, 50))
        
        legend_y = HEIGHT - 35
        pygame.draw.rect(screen, RACK_COLOR, (20, legend_y + 4, 15, 15))
        pygame.draw.rect(screen, BLACK, (20, legend_y + 4, 15, 15), 1)
        s1 = UI_FONT.render("Rack", True, WHITE)
        screen.blit(s1, (40, legend_y))

        pygame.draw.rect(screen, BROWN, (100, legend_y + 4, 15, 15))
        s2 = UI_FONT.render("Debris", True, WHITE)
        screen.blit(s2, (120, legend_y))
        
        pygame.draw.rect(screen, PRODUCT_COLOR, (190, legend_y + 4, 15, 15))
        s3 = UI_FONT.render("Product", True, WHITE)
        screen.blit(s3, (210, legend_y))

        ui_text = "Click a Product 'P' to fetch it"
        if animating_search:
            ui_text = "A* Searching..."
        elif animating_path:
            ui_text = "Fetching..."
        elif target_pos and not animating_path and len(path) == 0:
            ui_text = "Target unreachable!"
            
        text_sw = UI_FONT.render(ui_text, True, YELLOW)
        screen.blit(text_sw, (WIDTH - text_sw.get_width() - 20, legend_y))
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
