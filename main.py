# Remaking Jetpack Joyride in Python!
import math
import random
import pygame

pygame.init()
pygame.mixer.init()  # Initialize the mixer module
pygame.mixer.music.load('background_music.mp3')  # Load the background music file
pygame.mixer.music.set_volume(0.5)  # Set the volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music in a loop (-1 means infinite loop)
intense_music = 'intense_music.mp3'
player_standing = pygame.image.load('player_standing.png')
player_running = pygame.image.load('player_running.png')
player_boosting = pygame.image.load('player_boosting.png')

player_images = [player_standing, player_running]

# Add background
backgrounds = [
    pygame.image.load('background1.png'),  # Replace with your background image files
    pygame.image.load('background2.png'),
    pygame.image.load('background3.png')
]

background_width = backgrounds[0].get_width()  # Assuming all backgrounds have the same width
current_background_index = 0  # Start with the first background
distance_threshold = 3000  # Distance required to switch backgrounds
laser_horizontal_image = pygame.image.load('laser_horizontal.png')  # Replace with your horizontal laser image
laser_vertical_image = pygame.image.load('laser_vertical.png')  # Replace with your vertical laser image
laser_horizontal_image = pygame.transform.scale(laser_horizontal_image, (300, 30))  # Resize horizontal laser image
laser_vertical_image = pygame.transform.scale(laser_vertical_image, (50, 300))  # Resize vertical laser image

# Initialize parallax variables
bg_x1 = 0
bg_x2 = background_width
parallax_speed = 2  # Adjust this for the scrolling speed

WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) #setup a transparent screen that can draw (PAUSE Screen)
pygame.display.set_caption('Jetpack Joyride Remake in Python!')
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)
bg_color = (128, 128, 128)
lines = [0, WIDTH / 4, 2 * WIDTH / 4, 3 * WIDTH / 4]
game_speed = 3
pause = False
init_y = HEIGHT - 130
player_y = init_y
booster = False
counter = 0
y_velocity = 0
gravity = 0.4
new_laser = True
laser = []
distance = 0
restart_cmd = False
new_bg = 0
intense_music_playing = False

# Initializing the fuel variable
fuel = 100  # Maximum fuel (in percentage, 100 means full)
fuel_depletion_rate = 0.5  # Rate at which fuel depletes when boosting
fuel_regeneration_rate = 0.2   # Rate at which fuel regenerates when not boosting


# rocket variables
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

# blade variables
blades = []
new_blade = True
blade_speed = 5
blade_rotation_angle = 0

# Function to generate a new spinning blade
def generate_blade():
    blade_y = random.randint(100, HEIGHT - 150)  # Random height for the blade
    blade_x = WIDTH + random.randint(50, 300)  # Position blade off-screen to the right
    return [blade_x, blade_y]  # Starting position of the blade

def handle_input():
    global booster

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and fuel > 0:  # Only boost if fuel is not empty
        booster = True
    else:
        booster = False

def update_fuel():
    global fuel

    if booster:  # When the player is boosting
        fuel -= fuel_depletion_rate
        if fuel < 0:
            fuel = 0  # Prevent fuel from going below 0
    else:  # When the player is not boosting
        fuel += fuel_regeneration_rate
        if fuel > 100:
            fuel = 100  # Prevent fuel from exceeding 100%

# load in player info in beginning
file = open('player_info.txt', 'r')
read = file.readlines()
high_score = int(read[0])
lifetime = int(read[1])
file.close()

def draw_screen(line_list, lase):
    pygame.draw.rect(surface, (bg_color[0], bg_color[1], bg_color[2], 50), [0, 0, WIDTH, HEIGHT])
    screen.blit(surface, (0, 0))

    top = pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 50])
    bot = pygame.draw.rect(screen, 'gray', [0, HEIGHT - 50, WIDTH, 50])

    for i in range(len(line_list)):
        pygame.draw.line(screen, 'black', (line_list[i], 0), (line_list[i], 50), 3)
        pygame.draw.line(screen, 'black', (line_list[i], HEIGHT - 50), (line_list[i], HEIGHT), 3)
        if not pause:
            line_list[i] -= game_speed
            lase[0][0] -= game_speed
            lase[1][0] -= game_speed
        if line_list[i] < 0:
            line_list[i] = WIDTH

    # Check if laser image size is correct
    print("Horizontal laser image size:", laser_horizontal_image.get_width(), laser_horizontal_image.get_height())
    print("Vertical laser image size:", laser_vertical_image.get_width(), laser_vertical_image.get_height())

    # Check if laser coordinates are valid
    print("Laser coordinates:", lase)

    # Draw laser based on direction
    if lase[0][1] == lase[1][1]:  # Horizontal laser
        laser_rect = laser_horizontal_image.get_rect(topleft=(lase[0][0], lase[0][1]))
        print(f"Horizontal laser rect: {laser_rect}")
        screen.blit(laser_horizontal_image, laser_rect)
    elif lase[0][0] == lase[1][0]:  # Vertical laser
        laser_rect = laser_vertical_image.get_rect(topleft=(lase[0][0], lase[0][1]))
        print(f"Vertical laser rect: {laser_rect}")
        screen.blit(laser_vertical_image, laser_rect)

    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 70))

    # Return laser line (if needed) along with other values
    laser_line = pygame.draw.line(screen, 'yellow', (lase[0][0], lase[0][1]), (lase[1][0], lase[1][1]), 1)
    return line_list, top, bot, lase, laser_line, laser_rect


def draw_parallax_background():
    global bg_x1, bg_x2

    # Draw the current background
    screen.blit(backgrounds[current_background_index], (bg_x1, 0))
    screen.blit(backgrounds[current_background_index], (bg_x2, 0))

    if not pause:
        # Move the background images to the left
        bg_x1 -= parallax_speed
        bg_x2 -= parallax_speed

        # Reset positions when an image goes off-screen
        if bg_x1 <= -background_width:
            bg_x1 = bg_x2 + background_width
        if bg_x2 <= -background_width:
            bg_x2 = bg_x1 + background_width

# draw player including animated states
def draw_player():
    global player_y, counter
    play = pygame.rect.Rect((120, player_y + 10), (player_standing.get_width(), player_standing.get_height()))

    # Determine which animation to display
    if booster:  # Boosting animation
        screen.blit(player_boosting, (100, player_y))
    else:  # Running animation
        if counter < 20:  # Adjust the speed of animation by changing this threshold
            screen.blit(player_images[0], (100, player_y))  # Standing image
        else:
            screen.blit(player_images[1], (100, player_y))  # Running image

    return play
if counter < 40:  # Total duration for one full cycle (standing + running)
    counter += 1
else:
    counter = 0

def check_colliding():
    coll = [False, False]
    rstrt = False
    if player.colliderect(bot_plat):
        coll[0] = True
    elif player.colliderect(top_plat):
        coll[1] = True
    if laser_line.colliderect(player):
        rstrt = True
    if rocket_active:
        if rocket.colliderect(player):
            rstrt = True
    if player.colliderect(laser_rect):
        rstrt = True  # Trigger restart if player collides with laser
    return coll, rstrt

def generate_laser():
    laser_type = random.randint(0, 1)
    offset = random.randint(10, 300)
    match laser_type:
        case 0:  # Horizontal laser
            laser_width = random.randint(100, 300)
            laser_y = random.randint(100, HEIGHT - 100)
            new_lase = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_width, laser_y]]
        case 1:  # Vertical laser
            laser_height = random.randint(100, 300)
            laser_y = random.randint(100, HEIGHT - 400)
            new_lase = [[WIDTH + offset, laser_y], [WIDTH + offset, laser_y + laser_height]]
    return new_lase

def draw_rocket(coords, mode):
    if mode == 0:
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1] - 20))
        if not pause:
            if coords[1] > player_y + 10:
                coords[1] -= 3
            else:
                coords[1] += 3
    else:
        rock = pygame.draw.rect(screen, 'red', [coords[0], coords[1] - 10, 50, 20], 0, 5)
        pygame.draw.ellipse(screen, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7)
        if not pause:
            coords[0] -= 10 + game_speed

    return coords, rock


# Function to draw the spinning blade
def draw_blade(blade_position):
    global blade_rotation_angle
    blade_x, blade_y = blade_position
    blade_radius = 50  # Radius of the spinning blade

    # Calculate rotating blade lines
    blade_angle = blade_rotation_angle % 360
    for angle_offset in [0, 90, 180, 270]:  # Four lines to form a "spinning" blade
        end_x = blade_x + blade_radius * math.cos(math.radians(blade_angle + angle_offset))
        end_y = blade_y + blade_radius * math.sin(math.radians(blade_angle + angle_offset))
        pygame.draw.line(screen, 'red', (blade_x, blade_y), (end_x, end_y), 5)

    # Rotate the blade each frame
    if not pause:
        blade_rotation_angle += 5  # Rotation speed

    return pygame.Rect(blade_x - blade_radius, blade_y - blade_radius, blade_radius * 2, blade_radius * 2)

def draw_fuel_bar():
    # Calculate the x position for the top-right corner
    fuel_bar_x = WIDTH - 220  # Assuming the fuel bar is 200px wide and a 20px margin
    fuel_bar_y = 20  # Fixed y position for top

    # Draw the fuel bar background
    pygame.draw.rect(screen, (0, 0, 0), [fuel_bar_x, fuel_bar_y, 200, 20])  # Black background for the fuel bar
    # Draw the fuel bar (green for remaining fuel)
    pygame.draw.rect(screen, (0, 255, 0), [fuel_bar_x, fuel_bar_y, 200 * (fuel / 100), 20])  # Green fuel bar
    # Add text for fuel percentage
    screen.blit(font.render(f'Fuel: {int(fuel)}%', True, 'white'), (fuel_bar_x + 210, fuel_bar_y))

def draw_pause():
    pygame.draw.rect(surface, (128, 128, 128, 150), [0, 0, WIDTH, HEIGHT])
    pygame.draw.rect(surface, 'dark gray', [200, 150, 600, 50], 0, 10)
    surface.blit(font.render('Game Paused. Escape Btn Resumes', True, 'black'), (220, 160))
    restart_btn = pygame.draw.rect(surface, 'white', [200, 220, 280, 50], 0, 10)
    surface.blit(font.render('Restart', True, 'black'), (220, 230))
    quit_btn = pygame.draw.rect(surface, 'white', [520, 220, 280, 50], 0, 10)
    surface.blit(font.render('Quit', True, 'black'), (540, 230))
    pygame.draw.rect(surface, 'dark gray', [200, 300, 600, 50], 0, 10)
    surface.blit(font.render(f'Lifetime Distance Ran: {int(lifetime)}', True, 'black'), (220, 310))
    screen.blit(surface, (0, 0))
    return restart_btn, quit_btn

def modify_player_info():
    global high_score, lifetime
    if distance > high_score:
        high_score = distance
    lifetime += distance
    file = open('player_info.txt', 'w')
    file.write(str(int(high_score)) + '\n')
    file.write(str(int(lifetime)))
    file.close()


run = True
next_background_distance = distance_threshold
while run:
    timer.tick(fps)
    handle_input()
    update_fuel()
    if counter < 40:
        counter += 1
    else:
        counter = 0
    if new_laser:
        laser = generate_laser()
        new_laser = False

    draw_parallax_background()  # Parallax scrolling background
    lines, top_plat, bot_plat, laser, laser_line, laser_rect = draw_screen(lines, laser)
    draw_player()
    draw_fuel_bar()
    # Blade generation
    if new_blade:
        blades.append(generate_blade())
        new_blade = False
    # Draw and move blades
    blade_rects = []
    for blade in blades:
        blade_rect = draw_blade(blade)
        if not pause:
            blade[0] -= blade_speed + game_speed  # Move blade to the left only if the game is not paused
        blade_rects.append(blade_rect)

    # Remove blades that have moved off-screen
    blades = [blade for blade in blades if blade[0] > -50]
    # Reset blade generation when the previous blade is off-screen
    if all(blade[0] < 0 for blade in blades):
        new_blade = True

    if pause:
        restart, quits = draw_pause()

    if not rocket_active and not pause:
        rocket_counter += 1
    if rocket_counter > 180:
        rocket_counter = 0
        rocket_active = True
        rocket_delay = 0
        rocket_coords = [WIDTH, HEIGHT/2]
    if rocket_active:
        if rocket_delay < 90:
            if not pause:
                rocket_delay += 1
            rocket_coords, rocket = draw_rocket(rocket_coords, 0)
        else:
            rocket_coords, rocket = draw_rocket(rocket_coords, 1)
        if rocket_coords[0] < -50:
            rocket_active = False

    player = draw_player()
    colliding, restart_cmd = check_colliding()

    # Check for collisions with blades
    for blade_rect in blade_rects:
        if player.colliderect(blade_rect):
            restart_cmd = True


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            modify_player_info()
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if pause:
                    pause = False
                else:
                    pause = True
            if event.key == pygame.K_SPACE and not pause:
                booster = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                booster = False
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            if restart.collidepoint(event.pos):
                restart_cmd = True
            if quits.collidepoint(event.pos):
                modify_player_info()
                run = False

    if not pause:
        distance += game_speed

        # Background switching logic
        if distance >= next_background_distance:
            current_background_index += 1
            if current_background_index >= len(backgrounds):  # Loop back to the first background
                current_background_index = 0
            next_background_distance += distance_threshold  # Set the next threshold
            bg_x1 = 0
            bg_x2 = background_width

        if booster:
            y_velocity -= gravity
        else:
            y_velocity += gravity
        if (colliding[0] and y_velocity > 0) or (colliding[1] and y_velocity < 0):
            y_velocity = 0
        player_y += y_velocity
    # Music switching logic for high score/intense moments
    if distance > high_score and not intense_music_playing:
        pygame.mixer.music.stop()  # Stop the current music
        pygame.mixer.music.load(intense_music)  # Load intense music
        pygame.mixer.music.play(-1)  # Play intense music in a loop
        intense_music_playing = True
    elif distance <= high_score and intense_music_playing:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('background_music.mp3')
        pygame.mixer.music.play(-1)
        intense_music_playing = False

    # progressive speed increases
    if distance < 50000:
        game_speed = 1 + (distance // 500) / 10
    else:
        game_speed = 11

    if laser[0][0] < 0 and laser[1][0] < 0:
        new_laser = True

    if distance - new_bg > 500:
        new_bg = distance
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    if restart_cmd:
        modify_player_info()
        pygame.mixer.music.stop()  # Stop any currently playing music
        pygame.mixer.music.load('background_music.mp3')  # Load the background music
        pygame.mixer.music.play(-1)  # Play it in a loop
        distance = 0
        rocket_active = False
        rocket_counter = 0
        pause = False
        player_y = init_y
        y_velocity = 0
        restart_cmd = 0
        new_laser = True
        blades = []
        fuel = 100

    if distance > high_score:
        high_score = int(distance)

    pygame.display.flip()
pygame.quit()
