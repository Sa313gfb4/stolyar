import pygame
import sys
from enum import Enum

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.6
PLAYER_SPEED = 5
PLAYER_JUMP = 15

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
SKIN = (255, 200, 100)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(SKIN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.facing_right = True
        
    def update(self, platforms, enemies):
        # Движение
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        else:
            self.vel_x = 0
            
        # Прыжок
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -PLAYER_JUMP
            self.on_ground = False
        
        # Гравитация
        self.vel_y += GRAVITY
        
        # Границы экрана (слева-справа)
        self.rect.x += self.vel_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Столкновение с платформами (горизонталь)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Движемся вправо
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # Движемся влево
                    self.rect.left = platform.rect.right
        
        # Вертикальное движение
        self.rect.y += self.vel_y
        
        # Столкновение с платформами (вертикаль)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Падаем вниз
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Движемся вверх
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        # Проверка столкновения с врагами
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                return False  # Игрок мертв
        
        # Проверка падения
        if self.rect.top > SCREEN_HEIGHT:
            return False
        
        return True
    
    def draw(self, surface):
        pygame.draw.rect(surface, SKIN, self.rect)
        # Глаза
        eye_offset = 10 if self.facing_right else -10
        pygame.draw.circle(surface, BLACK, (self.rect.centerx + eye_offset, self.rect.centery - 10), 4)
        # Тело
        pygame.draw.rect(surface, BLUE, (self.rect.x + 5, self.rect.y + 25, self.width - 10, 20))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, min_x, max_x):
        super().__init__()
        self.width = 50
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 2
        self.direction = 1
    
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x <= self.min_x or self.rect.x >= self.max_x:
            self.direction *= -1
    
    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        pygame.draw.circle(surface, YELLOW, (self.rect.centerx - 10, self.rect.centery - 10), 6)
        pygame.draw.circle(surface, YELLOW, (self.rect.centerx + 10, self.rect.centery - 10), 6)

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation = 0
    
    def update(self):
        self.animation += 0.1
    
    def draw(self, surface):
        size = int(40 + 10 * pygame.math.sin(self.animation))
        pygame.draw.rect(surface, YELLOW, (self.rect.centerx - size//2, self.rect.centery - size//2, size, size))

class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = None
        self.player_start = (50, 500)
        
        self.create_level()
    
    def create_level(self):
        if self.level_num == 1:
            # Уровень 1: Простой уровень
            self.platforms.add(Platform(0, 550, SCREEN_WIDTH, 50))  # Земля
            self.platforms.add(Platform(200, 450, 200, 20))
            self.platforms.add(Platform(550, 350, 200, 20))
            self.platforms.add(Platform(800, 300, 150, 20))
            
            self.enemies.add(Enemy(250, 420, 200, 400))
            self.enemies.add(Enemy(600, 320, 550, 750))
            
            self.goal = Goal(900, 240)
            self.player_start = (50, 500)
        
        elif self.level_num == 2:
            # Уровень 2: Сложнее
            self.platforms.add(Platform(0, 550, SCREEN_WIDTH, 50))  # Земля
            self.platforms.add(Platform(100, 450, 150, 20))
            self.platforms.add(Platform(350, 380, 150, 20))
            self.platforms.add(Platform(600, 300, 150, 20))
            self.platforms.add(Platform(200, 250, 150, 20))
            self.platforms.add(Platform(750, 200, 150, 20))
            
            self.enemies.add(Enemy(150, 420, 100, 250))
            self.enemies.add(Enemy(400, 350, 350, 500))
            self.enemies.add(Enemy(650, 270, 600, 750))
            self.enemies.add(Enemy(250, 220, 200, 350))
            
            self.goal = Goal(850, 140)
            self.player_start = (50, 500)
        
        elif self.level_num == 3:
            # Уровень 3: Экстремальный
            self.platforms.add(Platform(0, 550, SCREEN_WIDTH, 50))  # Земля
            self.platforms.add(Platform(80, 480, 120, 20))
            self.platforms.add(Platform(250, 420, 100, 20))
            self.platforms.add(Platform(420, 350, 100, 20))
            self.platforms.add(Platform(150, 300, 100, 20))
            self.platforms.add(Platform(600, 280, 100, 20))
            self.platforms.add(Platform(450, 200, 100, 20))
            self.platforms.add(Platform(800, 150, 150, 20))
            
            self.enemies.add(Enemy(130, 450, 80, 200))
            self.enemies.add(Enemy(300, 390, 250, 350))
            self.enemies.add(Enemy(470, 320, 420, 520))
            self.enemies.add(Enemy(200, 270, 150, 250))
            self.enemies.add(Enemy(650, 250, 600, 700))
            self.enemies.add(Enemy(500, 170, 450, 550))
            
            self.goal = Goal(875, 90)
            self.player_start = (50, 500)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Столяров бежит от дяди Ашота!")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.state = GameState.MENU
        self.current_level = 1
        self.level = None
        self.player = None
        
    def start_level(self, level_num):
        self.current_level = level_num
        self.level = Level(level_num)
        self.player = Player(*self.level.player_start)
        self.state = GameState.PLAYING
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU and event.key == pygame.K_SPACE:
                    self.start_level(1)
                elif self.state == GameState.LEVEL_COMPLETE and event.key == pygame.K_SPACE:
                    if self.current_level < 3:
                        self.start_level(self.current_level + 1)
                    else:
                        self.state = GameState.MENU
                elif self.state == GameState.GAME_OVER and event.key == pygame.K_SPACE:
                    self.start_level(self.current_level)
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
        return True
    
    def update(self):
        if self.state == GameState.PLAYING:
            if not self.player.update(self.level.platforms, self.level.enemies):
                self.state = GameState.GAME_OVER
            
            for enemy in self.level.enemies:
                enemy.update()
            
            self.level.goal.update()
            
            if self.player.rect.colliderect(self.level.goal.rect):
                self.state = GameState.LEVEL_COMPLETE
    
    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("STOLYAROV", True, BLACK)
        subtitle = self.font_medium.render("vs Uncle Ashota", True, RED)
        start_text = self.font_small.render("Нажмите SPACE для начала", True, BLUE)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 200))
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 400))
    
    def draw_game(self):
        # Небо
        self.screen.fill((135, 206, 235))
        
        # Платформы
        for platform in self.level.platforms:
            self.screen.blit(platform.image, platform.rect)
        
        # Враги (дяди Ашоты)
        for enemy in self.level.enemies:
            enemy.draw(self.screen)
        
        # Цель
        self.level.goal.draw(self.screen)
        
        # Игрок
        self.player.draw(self.screen)
        
        # Информация на экране
        level_text = self.font_small.render(f"Уровень {self.current_level}/3", True, BLACK)
        self.screen.blit(level_text, (10, 10))
    
    def draw_level_complete(self):
        self.screen.fill(GREEN)
        
        level_text = self.font_large.render(f"Уровень {self.current_level} пройден!", True, BLACK)
        continue_text = self.font_small.render("Нажмите SPACE для продолжения", True, BLACK)
        
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 200))
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 400))
    
    def draw_game_over(self):
        self.screen.fill(RED)
        
        game_over_text = self.font_large.render("GAME OVER", True, WHITE)
        caught_text = self.font_medium.render("Дядя Ашота поймал тебя!", True, BLACK)
        retry_text = self.font_small.render("Нажмите SPACE для повтора", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 150))
        self.screen.blit(caught_text, (SCREEN_WIDTH//2 - caught_text.get_width()//2, 250))
        self.screen.blit(retry_text, (SCREEN_WIDTH//2 - retry_text.get_width()//2, 400))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()