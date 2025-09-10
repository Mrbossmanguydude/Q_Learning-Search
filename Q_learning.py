import random
import pygame

pygame.init()

WIDTH, HEIGHT = 640, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS 

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Q Learning")
epsilon = 0.65
discount_factor = 0.9
learning_rate = 0.1
Q_table = {}
episodes = 8000
for i in range(8):
    for j in range(8):
        Q_table[(i,j)] = [0,0,0,0]

actions = {0 : (0, 1), 1 : (0, -1), 2 : (-1, 0), 3 : (1, 0)}

grid = [
	[-1, -1, -1, -100, -1, -1, -1, -1],
	[-1, -1, -1, -1, -1, -1, -1, -1],
	[-1, -100, -1, -100, -1, -100, -1, -1],
	[-1, -1, -1, -100, -1, -1, -1, -1],
	[-1, -1, -100, -1, -1, -1, -100, -1],
    [-1, -1, -1, -1, -1, -100, -100, -1],
	[100, -1, -1, -1, -100, -1, -100, -1],
	[-100, -1, -1, -1, -1, 100, -100, -100]
]

class Agent:
    def __init__(self, state, discount_factor, learning_rate, epsilon, num_actions):
        self.state = state
        self.initial_state = state
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.actions = num_actions

    def get_qvalue(self, Q_table, action, reward, new_state):
        Q_table[self.state][action] = Q_table[self.state][action] + self.learning_rate * (reward + self.discount_factor * max(Q_table[new_state]) - Q_table[self.state][action])
        return Q_table

    def find_newstate(self, Q_table):
        x, y = self.state
        actions = {0 : (0, 1), 1 : (0, -1), 2 : (-1, 0), 3 : (1, 0)}
        if self.epsilon < random.random():
            while True:
                max_qvalue_index = random.choice(list(actions.keys()))
                action = actions[max_qvalue_index]
                new_state = (action[0] + x, action[1] + y)
                if new_state in Q_table:
                    return new_state, Q_table, max_qvalue_index
        else:
            for _ in Q_table[self.state]:
                max_qvalue = max(Q_table[self.state])
                max_qvalue_index = Q_table[self.state].index(max_qvalue)
                action = actions[max_qvalue_index]

                if (action[0] + x < 8 and action[0] + x >= 0) and (action[1] + y < 8 and action[1] + y >= 0): 
                    return (action[0] + x, action[1] + y), Q_table, max_qvalue_index
                else:
                    Q_table[self.state][max_qvalue_index] = -float('inf') 

    def num_rewards(self, grid):
        rewards = []
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == 100:
                    rewards.append((i, j))
        return rewards

    def Q_learning(self, grid, Q_table, episodes):
        paths = {}
        for episode in range(episodes):
            done = False
            total_reward = 0
            path = [] 
            while not done:
                new_state, Q_table, action = self.find_newstate(Q_table)
                reward = grid[self.state[1]][self.state[0]]
                total_reward += reward
                path.append(self.state)

                Q_table = self.get_qvalue(Q_table, action, reward, new_state) 
                self.state = new_state

                if reward == 100:
                    self.state = self.initial_state
                    total_reward += 100
                    done = True
                elif reward == -100:
                    self.state = self.initial_state
                    total_reward -= 100
                    done = True
                elif reward == -1:
                    total_reward -= 1

            paths[episode] = [total_reward, path]
        return Q_table, grid, paths

def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(screen, WHITE, (i*SQUARE_SIZE, j*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_lines(screen, rows, width):
    gap = width // rows 
    for i in range(rows):
        pygame.draw.line(screen, (128, 128, 128), (0, i* gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(screen, (128, 128, 128), (j * gap, 0), (j * gap, width))

def draw_path(path):
    for i,j in path:
        pygame.draw.rect(screen ,GREEN, (i*SQUARE_SIZE, j*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_highlighted_rect(surface, rect, border_color, highlight_color, border_thickness, highlight_thickness):
    pygame.draw.rect(surface, border_color, rect, border_thickness)
    inner_rect = pygame.Rect(rect.left + border_thickness, rect.top + border_thickness,rect.width - 2 * border_thickness, rect.height - 2 * border_thickness)
    pygame.draw.rect(surface, highlight_color, inner_rect, highlight_thickness)

def main(grid, Q_table):                                        
    clock = pygame.time.Clock()
    run = True
    font = pygame.font.Font("fonts\\pixel_font-1.ttf", 45)
    initial_state = (0, 0)
    best_path = None
    border_color = (255, 255, 255)
    highlight_color = (80, 80, 80)
    border_thickness = 1
    highlight_thickness = 5
    control_panel = pygame.Rect(0, 640, 640, 160)

    while run:
        clock.tick(60)

        pos = pygame.mouse.get_pos()
        i, j = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE

        if i <= 7 and j <= 7:
            rect = pygame.Rect(i*SQUARE_SIZE, j*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

        screen.fill((129, 133, 137))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                i, j = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
                if event.button == 1:
                    initial_state = (i, j)
                elif event.button == 2:
                    grid[j][i] = 100
                elif event.button == 3:
                    grid[j][i] = -100 if grid[j][i] != -100 else -1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = [[-1]*8 for _ in range(8)]
                    best_path = None
                elif event.key == pygame.K_SPACE:
                    pygame.display.set_caption("Q learning - LOADING...")
                    agent_train = Agent(initial_state, discount_factor, learning_rate, epsilon, 4)
                    Q_table, grid, paths = agent_train.Q_learning(grid, Q_table, episodes)
                    best_path = max(paths.items(), key=lambda x: x[1][0])
                    pygame.display.set_caption("Q learning")

        draw_grid()
        if best_path != None:
            draw_path(best_path[1][1])
        for i in range(ROWS):
            for j in range(COLS):
                if (i, j) == initial_state:
                    color = BLUE
                elif grid[j][i] == -100:
                    color = (255, 0, 0)
                elif grid[j][i] == 100:
                    color = (50, 100, 150)
                else:
                    color = (0, 0, 0)
                text_surface = font.render(str(grid[j][i]), True, color) 
                screen.blit(text_surface, ((i*SQUARE_SIZE) + 5, (j*SQUARE_SIZE) + 10))  
                draw_highlighted_rect(screen, rect, border_color, highlight_color, border_thickness, highlight_thickness)
                draw_highlighted_rect(screen, control_panel, (80, 80 ,80), (80, 80, 80), 10, 5)

        draw_lines(screen, 8, WIDTH)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main(grid, Q_table)