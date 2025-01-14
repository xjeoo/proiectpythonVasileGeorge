import pygame
from pygame import mixer
from button import Button
import os
import random
import csv

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 900
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Joc')


#set framerate

clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
SCROLL_THRESHOLD = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVEL = len(os.listdir(f'levels'))
screen_scroll = 0
bg_scroll = 0
Level = 1
start_game = False
start_intro = False

#define player action variables
moving_left = False
moving_right = False
shouldJump = False

shooting = False
grenade = False
grenade_thrown = False

#load sounds
shoot_sound = pygame.mixer.Sound('External/audio/shot.wav')
shoot_sound.set_volume(0.2)
jump_sound = pygame.mixer.Sound('External/audio/jump.wav')
jump_sound.set_volume(0.1)
grenade_sound = pygame.mixer.Sound('External/audio/grenade.wav')
grenade_sound.set_volume(0.2)


#load images
#buttons
start_button_img = pygame.image.load('External/img/start_btn.png').convert_alpha()
restart_button_img = pygame.image.load('External/img/restart_btn.png').convert_alpha()
exit_button_img = pygame.image.load('External/img/exit_btn.png').convert_alpha()


#background
pine1_img = pygame.image.load('External/img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('External/img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('External/img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('External/img/background/sky_cloud.png').convert_alpha()


bullet_img = pygame.image.load('External/img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('External/img/icons/grenade.png').convert_alpha()

health_box_img = pygame.image.load('External/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('External/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('External/img/icons/grenade_box.png').convert_alpha()

#store tiles in list
img_list = []
for i in range(TILE_TYPES):
    img = pygame.image.load(f'External/img/Tile/{i}.png')
    img = pygame.transform.scale(img, (TILE_SIZE,TILE_SIZE))
    img_list.append(img)


item_boxes = { 
    'health' :health_box_img ,
    'ammo' :ammo_box_img,
    'grenade' :grenade_box_img
    }

#define font
font = pygame.font.Font('External/fonts/Pixel Game.otf', 27)

# font = pygame.font.SysFont('Futura', 30)

#define colors
BG = (144,201, 120)
RED = (175, 0 ,0 )
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)



def drawText(x, y, text, font, text_color):
    img = font.render(text, True, text_color)
    window.blit(img, (x,y))

def drawBG():
    window.fill(BG)
    width = sky_img.get_width()
    for i in range(5):
        window.blit(sky_img, ( i*width - bg_scroll * 0.2 - 66,0))
        window.blit(mountain_img, ( i*width - bg_scroll * 0.3 - 66, SCREEN_HEIGHT-mountain_img.get_height()-300))
        window.blit(pine1_img, ( i*width - bg_scroll * 0.5 - 66, SCREEN_HEIGHT-pine1_img.get_height()-150))
        window.blit(pine2_img, ( i*width - bg_scroll * 0.66 - 66, SCREEN_HEIGHT-pine2_img.get_height()))

def restart_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

        #create tile list
    data = []
    for rows in range (ROWS):
        r = [-1] * COLS
        data.append(r)

    return data
    



class Soldier(pygame.sprite.Sprite):
    def __init__(self,charType, x, y, scale, speed, ammo, health, grenades ):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.charType = charType
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenades
        self.max_grenades = grenades
        self.shoot_cooldown = 0
        self.health = health
        self.maxHealth = health
        self.velY = 0
        self.direction = 1
        self.shouldJump = False
        self.jump = 2
        self.flip = False
        self.animationList = []
        self.frameIndex = 0
        self.action = 0
        self.updateTime = pygame.time.get_ticks()
        # AI Specific Variables 
        self.vision = pygame.Rect(0, 0, 250, 20)
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
       
        
        #load all images for the players
        animationTypes = ['Idle', 'Run', 'Jump','Death']
        for animation in animationTypes:
            #reset temporary list of images
            tempList = []
            #count files in folder
            num_of_frames = len(os.listdir(f'External/img/{self.charType}/{animation}'))
            for i in range (num_of_frames):
                img= pygame.image.load(f'External/img/{self.charType}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                tempList.append(img)
            self.animationList.append(tempList)
           
        
        
        self.image = self.animationList[self.action][self.frameIndex]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.updateAnimation()
        self.checkAlive()
        #update cooldown
        if self.shoot_cooldown >0:
            self.shoot_cooldown -= 1
       
            
        


    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0 
        dy = 0
        local_screen_scroll = 0
        #assign movement variables if moving
        if moving_left:
            dx = -self.speed
            self.flip = True
            self. direction = -1

        if moving_right:
            dx = +self.speed
            self.flip = False
            self. direction = 1

        if  self.shouldJump and self.jump>0:
            self.shouldJump = False
            self.velY = -10
            self.jump -= 1

        #apply gravity
        self.velY += GRAVITY
        if self.velY >9:
            self.velY = 9
        dy += self.velY

        #check colisions 
        for tile in world.obstacle_list:
            # check collision on x direction
            if tile[1].colliderect(self.rect.x +dx, self.rect.y,self.width, self.height - 1):
                dx = 0
                if self.charType == 'enemy':
                    self.direction *= -1
            # check collision on y direction
            if tile[1].colliderect(self.rect.x, self.rect.y+dy,self.width, self.height):
                #check if hit head
                if self.velY <= 0:
                    self.velY = 0
                    dy = tile[1].bottom - self.rect.top
                #check if hit floor
                elif self.velY > 0:
                    self.velY = 0
                    self.jump = 2
                    dy = tile[1].top - self.rect.bottom
        
        #check collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        if self.rect.top > SCREEN_HEIGHT  :
            self.health = 0

        #check if at level's end
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #check if going off-screen
        if(self.charType == 'player'):
            if(self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH):
                dx = 0
                self.updateAction(0)
        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll
        if(self.charType == 'player'):
            if((self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD 
                and bg_scroll< (world.level_length * TILE_SIZE) - SCREEN_WIDTH )
               or (self.rect.left<SCROLL_THRESHOLD and bg_scroll > abs(dx)) ):
                self.rect.x -= dx
                local_screen_scroll = -dx
        return local_screen_scroll, level_complete                


    def updateAction(self, new_action):
        #check if new action diff from previous
        if(new_action != self.action):
            self.action = new_action
            self.frameIndex = 0
            self.updateTime = pygame.time.get_ticks()

    
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 10
            bullet = Bullet(self.rect.centerx + self.rect.size[0]*0.675 * self.direction, self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shoot_sound.play()
    
    def AI(self):
        if self.alive :
            if self.idling == False and random.randint(1,200) == 1:
                self.idling = True
                self.updateAction(0)
                self.idling_counter = random.randint(50,150)

            if( self.vision.colliderect(player.rect)) and player.alive:
                self.updateAction(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.updateAction(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + self.vision.width/2 *self.direction,self.rect.centery)
                    # pygame.draw.rect(window, RED, self.vision)

                
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                        #update ai vision
                        
                        
                
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = 0
        #scroll
        if player.alive:
            self.rect.x += screen_scroll
            


    def updateAnimation(self):
        #update animation
        ANIMATION_COOLDOWN = 150
        #update image
        self.image = self.animationList[self.action][self.frameIndex]
        #check if enought time passed since update
        if pygame.time.get_ticks() - self.updateTime >ANIMATION_COOLDOWN:
            self.updateTime = pygame.time.get_ticks()
            self.frameIndex += 1
        if self.frameIndex >= len(self.animationList[self.action]):
            if self.action == 3:
                self.frameIndex=len(self.animationList[self.action]) - 1
            else:
                self.frameIndex = 0

    def checkAlive(self):
        if self.health <= 0 :
            self.health = 0
            self.speed = 0
            self.alive = False
            self.updateAction(3)

            return False
        else:
            return True
            
            

    def draw(self):
        window.blit(pygame.transform.flip(self.image,self.flip, False),self.rect)
    
class World():
    def __init__(self):
        self.obstacle_list = []
    
    def processData(self, data):
        #iterate through each value in data level file
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE
                    img_rect.y = y*TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >=0 and tile<= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile>=9 and tile <= 10:
                        water = Water(x*TILE_SIZE, y*TILE_SIZE, img )
                        water_group.add(water)
                    elif tile>= 11 and tile <= 14:
                        decoration = Decoration(x*TILE_SIZE, y*TILE_SIZE, img )
                        decoration_group.add(decoration)
                    elif tile == 15:#create player  
                        player = Soldier('player', x*TILE_SIZE, y*TILE_SIZE, 2, 5, 200, 100, 7)
                        health_bar = HealthBar(10, 10, player.health, player.maxHealth)
                    elif tile == 16: #create enemy
                        enemy = Soldier('enemy',x*TILE_SIZE, y*TILE_SIZE, 2, 2, 100, 100, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: #create ammo box
                        item_box = itemPickup(x*TILE_SIZE, y*TILE_SIZE,'ammo')
                        item_box_group.add(item_box)
                    elif tile == 18: #create grenade box
                        item_box = itemPickup(x*TILE_SIZE, y*TILE_SIZE,'grenade')
                        item_box_group.add(item_box)
                    elif tile == 19: #create health box
                        item_box = itemPickup(x*TILE_SIZE, y*TILE_SIZE,'health')
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit
                        exit = Exit(x*TILE_SIZE, y*TILE_SIZE, img )
                        exit_group.add(exit)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            if player.alive:
                tile[1][0] += screen_scroll
            window.blit(tile[0], tile[1])


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, image ):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        if player.alive:
                self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, image ):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()*0.8))
    
    def update(self):
        if player.alive:
                self.rect.x += screen_scroll

class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, image ):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        if player.alive:
            self.rect.x += screen_scroll



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction ):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.velY = -11
        self.speed = 10
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center =  (x,y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    
    def update(self):
        self.velY += GRAVITY
        dx = self.direction * self.speed 
        dy = self.velY
        

        #check collisions
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self. height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self. height):
                self.speed = 0
                if self.velY < 0:
                    self.velY = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.velY > 0:
                    self.velY = 0
                    dy = tile[1].top - self.rect.bottom


        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if(self.timer <= 0):
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 1)
            explosion_group.add(explosion)
            grenade_sound.play()
            #do damage in radius
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 3 and\
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 3:
                player.health -= 40
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 3 and\
                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 3:
                    enemy.health -= 50 
            

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range (1,6):
            img = pygame.image.load(f'External/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale),int (img.get_height() * scale)))
            self.images.append(img)
        self.frameIndex = 0
        self.image = self.images[self.frameIndex]
        self.rect = self.image.get_rect()
        self.rect.center =  (x,y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        #update frame
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frameIndex += 1

            # if animation done delete explosion
            if self.frameIndex >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frameIndex]
        if player.alive:
            self.rect.x += screen_scroll

class screenTransition():
    def __init__(self, direction,color,speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.counter = 0

    
    def fade(self):
        fade_complete = False
        self.counter += self.speed
        
        if self.direction == 1:
            pygame.draw.rect(window, self.color, (0 - self.counter, 0,
                                                SCREEN_WIDTH//2 , SCREEN_HEIGHT))
            pygame.draw.rect(window, self.color, (0 +SCREEN_WIDTH//2+ self.counter, 0,
                                                SCREEN_WIDTH//2 , SCREEN_HEIGHT))
            pygame.draw.rect(window, self.color, (0 , 0- self.counter,
                                                SCREEN_WIDTH , SCREEN_HEIGHT//2))
            pygame.draw.rect(window, self.color, (0 , 0 + SCREEN_HEIGHT//2 + self.counter,
                                                SCREEN_WIDTH , SCREEN_HEIGHT//2))
        
            
        elif self.direction == 2 :
            pygame.draw.rect(window, self.color, (0, 0, SCREEN_WIDTH, 0 + self.counter))
            if self.counter >= SCREEN_HEIGHT:
                fade_complete = True
        
            pass
            

        return fade_complete
             

class itemPickup(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type ):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop =  (x + TILE_SIZE//2 , y +(TILE_SIZE -self.image.get_height()))

    def update(self):
        #check if player picked box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'health':
                if player.health <80: 
                    player.health += 20
                    self.kill()
                elif player.health != 100:
                        player.health += 100-player.health
                        self.kill()
            elif self.item_type == 'ammo':
                player.ammo += 20
                self.kill()
            elif self.item_type == 'grenade':
                if player.grenades < player.max_grenades-3:
                    player.grenades += 3
                    self.kill()
                elif player.grenades != player.max_grenades:
                        player.grenades += player.max_grenades - player.grenades
                        self.kill()
        if player.alive:
            self.rect.x += screen_scroll

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self. max_health = max_health

    def draw (self, health):
        #update with new health
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(window, BLACK, (self.x, self.y, 150, 20))
        pygame.draw.rect(window, GRAY, (self.x + 2, self.y + 2, 146, 16))
        pygame.draw.rect(window, RED, (self.x + 2, self.y +2, 150 * ratio -4, 16))
        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction ):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 15
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center =  (x,y)
        self.direction = direction
    
    def update(self):
        #move bullet
        self.rect.x += self.speed * self.direction + screen_scroll
        #check if bullet is off-screen
        if self.rect.right <0 or self.rect.left > SCREEN_WIDTH :
            self.kill()
        for tile in world.obstacle_list:
            # check collision on x direction
            if tile[1].colliderect(self.rect):
                self.kill()
        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health-=5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health-=20
                    self.kill()
        

#create buttons
start_button = Button( SCREEN_WIDTH//2-start_button_img.get_width()/2, SCREEN_HEIGHT//2-100 - start_button_img.get_height()/2, start_button_img, 1 )
restart_button = Button( SCREEN_WIDTH//2-restart_button_img.get_width()*1.25, SCREEN_HEIGHT//2 - restart_button_img.get_height()/2, restart_button_img, 2.5 )
exit_button = Button( SCREEN_WIDTH//2-exit_button_img.get_width()/2, SCREEN_HEIGHT//2 + 150, exit_button_img, 1 )

#create transitions
intro_transition = screenTransition ( 1, BLACK, 12 )
death_transition = screenTransition ( 2, RED, 12 )


#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()




    




#create tile list
world_data = []
for rows in range (ROWS):
    r = [-1] * COLS
    world_data.append(r)
#Load Data
with open(f'levels/level{Level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, healthbar = world.processData(world_data)

running = True
drawBG()
while running:
    clock.tick(FPS)

    if(start_game == False): #main menu
        # window.fill(BG)
        if start_button.draw(window):
            start_game = True
            start_intro = True
        if exit_button.draw(window):
            running = 0
    

    else: 
        #update background
        drawBG()
        #draw world map
        world.draw()
        
        
        

        item_box_group.update()
        item_box_group.draw(window)
    

        #update and draw groups
        bullet_group.update()
        bullet_group.draw(window)

        grenade_group.update()
        grenade_group.draw(window)

        
        decoration_group.update()
        decoration_group.draw(window)    

        exit_group.update()
        exit_group.draw(window)
        
        player.update()
        player.draw()
        

        explosion_group.update()
        explosion_group.draw(window)

        water_group.update()
        water_group.draw(window)

        

        #kill info
        dead_enemies = 0

        for enemy in enemy_group:
            enemy.update()
            if enemy.checkAlive() == False:
                dead_enemies += 1
            enemy.AI()
            enemy.draw()
        
        healthbar.draw(player.health)
        drawText(9, 34, f'Ammo: {player.ammo} Grenades: {player.grenades}', font, BLACK)
        drawText(10, 35, f'Ammo: {player.ammo} Grenades: {player.grenades}', font, WHITE)
        
        drawText(SCREEN_WIDTH - 121, 34, f'Kills: {dead_enemies}', font, BLACK)
        drawText(SCREEN_WIDTH - 120, 35, f'Kills: {dead_enemies}', font, WHITE)

        if start_intro:
            if(intro_transition.fade()):
                start_intro = False
                intro_transition.counter = 0

        if player.alive:
            if shooting:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades>0:
                grenade = Grenade(player.rect.centerx + 0.2*player.rect.size[0] * player.direction \
                                , player.rect.centery, player.direction)
                player.grenades -=1
                grenade_group.add(grenade)
                grenade_thrown = True
                print(player.grenades)
            if player.jump<2:
                player.updateAction(2)
            elif moving_left or moving_right:
                player.updateAction(1)
            else:
                player.updateAction(0)
            screen_scroll, level_complete = player.move(moving_left,moving_right)
            bg_scroll -= screen_scroll 
            #check if level is completed
            if level_complete:
                if Level != MAX_LEVEL:
                    Level += 1
                bg_scroll = 0
                world_data = restart_level()
                if Level <= MAX_LEVEL:
                    #Load Data
                    with open(f'levels/level{Level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, healthbar = world.processData(world_data)
                    start_intro = True
                    if start_intro:
                        intro_transition.counter = 0 
                        if(intro_transition.fade()):
                            start_intro = False
                            intro_transition.counter = 0 
        
        else:
            screen_scroll = 0
            if death_transition.fade():
                if restart_button.draw(window):
                    bg_scroll = 0
                    death_transition.counter = 0
                    start_intro = True
                    if start_intro:
                        intro_transition.counter = 0 
                        if(intro_transition.fade()):
                            start_intro = False
                            intro_transition.counter = 0 
                    world_data = restart_level()
                    #Load Data
                    with open(f'levels/level{Level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, healthbar = world.processData(world_data)


        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:#quit gane
            running = False
        if event.type == pygame.KEYDOWN:  #keyboard presses
            if(event.key == pygame.K_a):
                moving_left = True
            if(event.key == pygame.K_d):
                moving_right = True
            if(event.key == pygame.K_SPACE):
                shooting = True
            if(event.key == pygame.K_w and (player.alive and player.jump>0)):
                player.shouldJump = True
                jump_sound.play()
            if(event.key == pygame.K_ESCAPE):
                start_game = not start_game
            if(event.key == pygame.K_LCTRL):
                grenade = True

        if event.type == pygame.KEYUP:  #keyboard button released
            if(event.key == pygame.K_a):
                moving_left = False
            if(event.key == pygame.K_d):
                moving_right = False
            if(event.key == pygame.K_SPACE):
                shooting = False
            if(event.key == pygame.K_LCTRL):
                grenade = False
                grenade_thrown = False

    
    pygame.display.update()

pygame.quit()
