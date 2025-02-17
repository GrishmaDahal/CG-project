import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Simulation")

# Simulation parameters
ANT_COUNT, PREDATOR_COUNT = 50, 3
ANT_SPEED, PHEROMONE_LIFETIME = 1, 1500

# Load images
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load('background.png'), (WIDTH, HEIGHT))
ANT_ICON = pygame.transform.scale(pygame.image.load('ant.png'), (20, 20))
ANT_WITH_FOOD_ICON = pygame.transform.scale(pygame.image.load('ant_with_food.png'), (20, 20))
FOOD_ICON = pygame.image.load('food.png')
HOLE_ICON = pygame.transform.scale(pygame.image.load('hole.png'), (60, 60))

# Predator images
SPIDER_ICON = pygame.transform.scale(pygame.image.load('spider.png'), (40, 40))
LIZARD_ICON = pygame.transform.scale(pygame.image.load('lizard.png'), (50, 50))
BIRD_ICON = pygame.transform.scale(pygame.image.load('bird.png'), (80, 80))

# Nest position
NEST_POS, NEST_RADIUS = (WIDTH // 2, HEIGHT // 2), 20

# Fixed food positions
FIXED_FOOD_POSITIONS = [(250, 150), (600, 100), (210, 400), (550, 500)]

# Pheromone class
class Pheromone:
    def __init__(self, x, y):
        self.x, self.y, self.time_placed = x, y, time.time() * 1000
    def is_active(self):
        return (time.time() * 1000 - self.time_placed) < PHEROMONE_LIFETIME
    def get_alpha(self):
        age = (time.time() * 1000 - self.time_placed) / PHEROMONE_LIFETIME
        return max(0, int(255 * (1 - age)))

# Ant class
class Ant:
    def __init__(self, x, y):
        self.x, self.y, self.angle, self.carrying_food = x, y, random.uniform(0, 2 * math.pi), False
    
    def move(self):
        self.angle += random.uniform(-0.2, 0.2)
        self.x = (self.x + math.cos(self.angle) * ANT_SPEED) % WIDTH
        self.y = (self.y + math.sin(self.angle) * ANT_SPEED) % HEIGHT

    def detect_food(self, food_sources):
        for food in food_sources:
            if food.amount > 0 and math.hypot(self.x - food.x, self.y - food.y) < 10:
                self.carrying_food = True
    
    def return_to_nest(self):
        if self.carrying_food:
            dx, dy = NEST_POS[0] - self.x, NEST_POS[1] - self.y
            self.angle = math.atan2(dy, dx)
            self.move()
            pheromone_map.append(Pheromone(self.x, self.y))
            if math.hypot(self.x - NEST_POS[0], self.y - NEST_POS[1]) < NEST_RADIUS:
                self.carrying_food = False
    
    def follow_pheromone(self):
        best_angle, max_pheromone = self.angle, 0
        for pheromone in pheromone_map:
            dist = math.hypot(self.x - pheromone.x, self.y - pheromone.y)
            if dist < 50 and (strength := 1 / (dist + 1)) > max_pheromone:
                max_pheromone, best_angle = strength, math.atan2(pheromone.y - self.y, pheromone.x - self.x)
        self.angle = best_angle

# Food class
class Food:
    def __init__(self, x, y, amount=40):
        self.x, self.y, self.amount, self.size = x, y, amount, 15

# Predator base class
class Predator:
    def __init__(self, x, y, speed, detection_radius, image):
        if type(self) == Predator:
            raise TypeError("Cannot instantiate abstract class Predator directly.")
        self.x, self.y, self.angle = x, y, random.uniform(0, 2 * math.pi)
        self.speed, self.detection_radius, self.image = speed, detection_radius, image
    
    def move(self):
        self.angle += random.uniform(-0.1, 0.1)
        self.x = (self.x + math.cos(self.angle) * self.speed) % WIDTH
        self.y = (self.y + math.sin(self.angle) * self.speed) % HEIGHT
    
    def hunt(self, ants):
        for ant in ants[:]:
            if math.hypot(self.x - ant.x, self.y - ant.y) < self.detection_radius:
                ants.remove(ant)
                return

# Different predator types
class Spider(Predator):
    def __init__(self, x, y):
        super().__init__(x, y, speed=0.5, detection_radius=15, image=SPIDER_ICON)

class Lizard(Predator):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1.0, detection_radius=20, image=LIZARD_ICON)

class Bird(Predator):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1.5, detection_radius=25, image=BIRD_ICON)

# Create entities
pheromone_map, ants = [], [Ant(*NEST_POS) for _ in range(ANT_COUNT)]
food_sources = [Food(x, y) for x, y in FIXED_FOOD_POSITIONS]
#predators = [random.choice([Spider, Lizard, Bird])(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(PREDATOR_COUNT)]
predators = [
                    Spider(random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                    Lizard(random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                    Bird(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                ]
# Main simulation loop
running, paused, clock = True, False, pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            if event.key == pygame.K_r:
                ants, pheromone_map = [Ant(*NEST_POS) for _ in range(ANT_COUNT)], []
                food_sources = [Food(x, y) for x, y in FIXED_FOOD_POSITIONS]
                predators = [
                    Spider(random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                    Lizard(random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                    Bird(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                ]
            if event.key == pygame.K_SPACE:  # Add 10 new ants when spacebar is pressed
                ants.extend([Ant(*NEST_POS) for _ in range(20)])
        if event.type == pygame.MOUSEBUTTONDOWN:
            (food_sources if event.button == 1 else predators).append((Food if event.button == 1 else random.choice([Spider, Lizard, Bird]))(*event.pos))

    if paused:
        continue
    
    pheromone_map = [p for p in pheromone_map if p.is_active()]
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    screen.blit(HOLE_ICON, HOLE_ICON.get_rect(center=NEST_POS))

    for food in food_sources:
        screen.blit(pygame.transform.scale(FOOD_ICON, (food.size, food.size)), (food.x - food.size // 2, food.y - food.size // 2))
    
    for ant in ants:
        ant.return_to_nest() if ant.carrying_food else (ant.follow_pheromone(), ant.move(), ant.detect_food(food_sources))
        screen.blit(ANT_WITH_FOOD_ICON if ant.carrying_food else ANT_ICON, (ant.x - 10, ant.y - 10))
    
    for predator in predators:
        predator.move()
        predator.hunt(ants)
        screen.blit(predator.image, (predator.x - 20, predator.y - 20))

    pheromone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for pheromone in pheromone_map:
        pygame.draw.circle(pheromone_surface, (255, 255, 100, pheromone.get_alpha()), (int(pheromone.x), int(pheromone.y)), 2)

    screen.blit(pheromone_surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
