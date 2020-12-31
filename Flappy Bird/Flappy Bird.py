import pygame , sys, random

pygame.init()

# Variables
screen_width = 576
screen_height = 1024
fps=120
floor_x_pos = 0
floor_y_pos = 900
floor_width = 336*2
floor_velocity = 1
bird_x_pos = 100
gravity = 0.25
bird_velocity = 0
jump = -11
pipe_gap = 300
game_active = True
score = 0
high_score = 0
can_score = True

# Objects
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf',40)

bg_surface = pygame.image.load("sprites/background-day.png").convert()
bg_surface = pygame.transform.scale2x(bg_surface)

floor_surface = pygame.image.load('sprites/base.png').convert()
floor_surface = pygame.transform.scale2x(floor_surface)

bird_downflap = pygame.transform.scale2x(pygame.image.load('sprites/yellowbird-downflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('sprites/yellowbird-midflap.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('sprites/yellowbird-upflap.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (bird_x_pos, screen_height/2))

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP,200)

pipe_surface = pygame.image.load('sprites/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE,1200)
pipe_heights = [400,500,600,700,800]

game_over_surface = pygame.transform.scale2x(pygame.image.load('sprites/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center = (screen_width/2,screen_height/2))

flap_sound = pygame.mixer.Sound('audio/wing.wav')

# Functions
def draw_floor():
    screen.blit(floor_surface,(floor_x_pos,floor_y_pos))
    screen.blit(floor_surface,(floor_x_pos + floor_width,floor_y_pos))

def create_pipe():
    rand_pipe_height = random.choice(pipe_heights)
    bottom_pipe = pipe_surface.get_rect(midtop = (screen_width+pipe_surface.get_width(),rand_pipe_height))
    top_pipe = pipe_surface.get_rect(midbottom = (screen_width+pipe_surface.get_width(),rand_pipe_height - pipe_gap))
    return bottom_pipe,top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5

    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface,pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface,False,True)
            screen.blit(flip_pipe,pipe)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            can_score = True
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= floor_y_pos:
        can_score = True
        return False

    return True

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird,-bird_velocity*3,1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (bird_x_pos,bird_rect.centery))
    return new_bird,new_bird_rect

def score_display(game_state):
    global high_score
    if game_state == 'main_game':
        score_surface = game_font.render(f'Score: {int(score)}',True,(255,255,255))
        score_rect = score_surface.get_rect(center = (288,100))
        screen.blit(score_surface,score_rect)
    elif game_state == 'game_over':
        if score > high_score:
            high_score = score
        high_score_surface = game_font.render(f'High Score: {int(high_score)}',True,(255,255,255))
        high_score_rect = high_score_surface.get_rect(center = (288,100))
        screen.blit(high_score_surface,high_score_rect)

def pipe_score_check():
    global score, can_score
    if pipe_list:
        for pipe in pipe_list:
            if bird_x_pos-5 < pipe.centerx < bird_x_pos + 5 and can_score:
                score += 1
                #score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True
 
# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE and game_active:
                bird_velocity = jump
                flap_sound.play()
            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (bird_x_pos, screen_height/2)
                bird_velocity = jump
                flap_sound.play()
                score = 0

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird_surface,bird_rect = bird_animation()

    # Background 
    screen.blit(bg_surface, (0,0))

    if game_active:
        # Bird Update
        bird_velocity += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_velocity
        screen.blit(rotated_bird,bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes Update
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        pipe_score_check()
        score_display('main_game')
    else:
        screen.blit(game_over_surface,game_over_rect)
        score_display('game_over')

    # Floor Updade
    draw_floor()
    if floor_x_pos <= -floor_width:
        floor_x_pos = 0
    floor_x_pos -= floor_velocity

    
    pygame.display.update()
    clock.tick(fps)