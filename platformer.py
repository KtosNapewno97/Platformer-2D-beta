import pygame
import random

# ------------------------ CONFIG
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_POWER = 12
PLATFORM_WIDTH_MIN, PLATFORM_WIDTH_MAX = 150, 300  # większe platformy
# ------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformówka 2D - poprawiona")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

# ------------------------ CLASSES
class Particle:
    def __init__(self, pos, color, lifetime=20):
        self.pos = list(pos)
        self.vel = [random.uniform(-1,1), random.uniform(-2,0)]
        self.color = color
        self.lifetime = lifetime

    def update(self):
        self.vel[1] += 0.2
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.lifetime -=1

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.pos[0]), int(self.pos[1])), 3)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, HEIGHT-200, 40, 60)
        self.vel = [0,0]
        self.on_ground = False
        self.color = (0,200,255)

    def handle_input(self, keys):
        self.vel[0] = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel[0] = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel[0] = PLAYER_SPEED
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel[1] = -JUMP_POWER
            self.on_ground = False

    def update(self, platforms):
        prev_on_ground = self.on_ground
        self.vel[1] += GRAVITY
        self.rect.x += int(self.vel[0])
        self.collide(platforms, True)
        self.rect.y += int(self.vel[1])
        self.on_ground = False
        self.collide(platforms, False)
        return prev_on_ground

    def collide(self, platforms, horizontal):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if horizontal:
                    if self.vel[0] >0:
                        self.rect.right = plat.rect.left
                    elif self.vel[0]<0:
                        self.rect.left = plat.rect.right
                    self.vel[0]=0
                else:
                    if self.vel[1]>0:
                        self.rect.bottom = plat.rect.top
                        self.on_ground = True
                    elif self.vel[1]<0:
                        self.rect.top = plat.rect.bottom
                    self.vel[1]=0

    def draw(self, surf, offset):
        draw_rect = self.rect.move(-offset,0)
        pygame.draw.rect(surf, self.color, draw_rect)

class Platform:
    def __init__(self, x,y,w,h,color=(100,200,100)):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color

    def draw(self, surf, offset):
        draw_rect = self.rect.move(-offset,0)
        if draw_rect.right>0 and draw_rect.left<WIDTH:
            pygame.draw.rect(surf, self.color, draw_rect)

class Enemy:
    def __init__(self, x,y, plat_width):
        self.rect = pygame.Rect(x,y,40,40)
        self.vel = 2
        self.color = (255,50,50)
        self.left_bound = x
        self.right_bound = x + plat_width - self.rect.width

    def update(self):
        self.rect.x += self.vel
        if self.rect.x < self.left_bound or self.rect.x > self.right_bound:
            self.vel*=-1

    def draw(self,surf, offset):
        draw_rect = self.rect.move(-offset,0)
        if draw_rect.right>0 and draw_rect.left<WIDTH:
            pygame.draw.rect(surf, self.color, draw_rect)

class Coin:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,20,20)
        self.color = (255,255,0)

    def draw(self,surf, offset):
        draw_rect = self.rect.move(-offset,0)
        if draw_rect.right>0 and draw_rect.left<WIDTH:
            pygame.draw.ellipse(surf, self.color, draw_rect)

# ------------------------ FUNKCJA RESET
def reset_game():
    global player, platforms, enemies, coins, particles, score, last_platform_x
    player = Player()
    platforms = [Platform(0, HEIGHT-40, WIDTH, 40, (100,100,100))]
    enemies = []
    coins = []
    particles = []
    score = 0
    last_platform_x = WIDTH - 50

# ------------------------ INITIALIZATION
reset_game()

# ------------------------ GAME LOOP
running=True
while running:
    dt = clock.tick(FPS)/1000.0
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

    keys = pygame.key.get_pressed()
    prev_on_ground = player.on_ground
    player.handle_input(keys)

    # procedural world generation
    while last_platform_x < player.rect.x + WIDTH:
        plat_w = random.randint(PLATFORM_WIDTH_MIN, PLATFORM_WIDTH_MAX)
        plat_h = 20
        plat_y = random.randint(HEIGHT-160, HEIGHT-80)  # platformy minimalnie nad podłogą
        new_plat = Platform(last_platform_x, plat_y, plat_w, plat_h)
        platforms.append(new_plat)
        # spawn enemy
        if random.random()<0.3:
            enemies.append(Enemy(new_plat.rect.x, new_plat.rect.y-40, plat_w))
        # spawn coin
        if random.random()<0.5:
            coin_x = random.randint(new_plat.rect.x+5, new_plat.rect.x+plat_w-25)
            coin_y = new_plat.rect.y-25
            coins.append(Coin(coin_x, coin_y))
        last_platform_x += plat_w + random.randint(50,100)

    # update
    prev_on_ground = player.update(platforms)

    # particle pod graczem przy lądowaniu
    if not prev_on_ground and player.on_ground:
        for _ in range(10):
            particles.append(Particle((player.rect.centerx, player.rect.bottom), (255,255,0)))

    for enemy in enemies: enemy.update()
    for p in particles: p.update()
    particles = [p for p in particles if p.lifetime>0]

    # collision coins
    for coin in coins[:]:
        if player.rect.colliderect(coin.rect):
            coins.remove(coin)
            score+=1
            for _ in range(5):
                particles.append(Particle((coin.rect.centerx, coin.rect.centery),(255,255,0)))

    # collision with enemies
    dead = False
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            dead = True
            break

    # camera scrolling
    scroll_offset = player.rect.x - 200

    # draw
    screen.fill((50,150,255))  # sky
    # szara podłoga
    pygame.draw.rect(screen,(100,100,100),(0, HEIGHT-40, WIDTH, 40))

    for plat in platforms: plat.draw(screen, scroll_offset)
    for enemy in enemies: enemy.draw(screen, scroll_offset)
    for coin in coins: coin.draw(screen, scroll_offset)
    for p in particles: p.draw(screen)
    player.draw(screen, scroll_offset)

    # score
    text = font.render(f"Monety: {score}",True,(255,255,255))
    screen.blit(text,(10,10))

    pygame.display.flip()

    # jeśli gracz dotknie wroga
    if dead:
        msg = font.render("Umarłeś!", True, (255,0,0))
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        reset_game()
