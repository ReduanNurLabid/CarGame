from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

window_width = 800
window_height = 600

#camera
camera_x = 0.0
camera_y = 3.0
camera_z = 10.0
look_x = 0.0
look_y = 0.0
look_z = 0.0
up_x = 0.0
up_y = 1.0
up_z = 0.0

# Car
car_x = 0.0
car_y = 0.0
car_z = 0.0
car_rotation = 0.0
car_speed = 0.0
max_speed = 0.5
max_reverse_speed = -0.1
acceleration = 0.001
deceleration = 0.001
turning_speed = 0.2

#movement
move_forward = False
move_backward = False
turn_left = False
turn_right = False

first_person_view = False
game_over = False
score = 0

#road
road_width = 10.0
road_segment_length = 20.0
num_road_segments = 10
terrain_size = 200.0

# Road segments and environment objects
road_segments = []
trees = []
houses = []
house_colors = []
num_trees = 60
num_houses = 20


class CpuCar:
    def __init__(self, x, z, speed, color):
        self.x = x
        self.z = z
        self.speed = speed
        self.color = color
        self.overtaken = False


cpu_cars = []
cpu_spawn_timer = 100
cpu_spawn_interval = 250


def init():
    """Initialize OpenGL settings"""
    glClearColor(0.5, 0.7, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    light_position = [0, 20, 0, 1]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    mat_ambient = [0.2, 0.2, 0.2, 1.0]
    mat_diffuse = [0.8, 0.8, 0.8, 1.0]
    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [50.0]

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)


def generate_road_segments():
    global road_segments
    road_segments = []

    for i in range(num_road_segments):
        z_pos = -i * road_segment_length
        road_segments.append(z_pos)


def generate_environment_objects():
    global trees, houses, house_colors
    trees = []
    houses = []
    house_colors = []

    for _ in range(num_trees):
        side = random.choice([-1, 1])
        x = side * (road_width / 2 + 2 + random.uniform(0.5, 3))
        z = random.uniform(-road_segment_length * num_road_segments, 0)
        scale = random.uniform(1.5, 3.0)
        trees.append([x, z, scale])

    for _ in range(num_houses):
        side = random.choice([-1, 1])
        x = side * (road_width / 2 + 10 + random.uniform(2, 7))
        z = random.uniform(-road_segment_length * num_road_segments, 0)
        house_type = random.randint(0, 2)
        houses.append([x, z, house_type])
        house_colors.append([random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0)])


def update_environment_objects():
    global trees, houses

    for tree in trees:
        if tree[1] > car_z + road_segment_length * 2:
            tree[1] -= road_segment_length * num_road_segments
            side = random.choice([-1, 1])
            tree[0] = side * (road_width / 2 + 2 + random.uniform(0.5, 3))
            tree[2] = random.uniform(1.5, 3.0)

    for house in houses:
        if house[1] > car_z + road_segment_length * 2:
            house[1] -= road_segment_length * num_road_segments
            side = random.choice([-1, 1])
            house[0] = side * (road_width / 2 + 8 + random.uniform(1, 5))
            house[2] = random.randint(0, 2)  # New house type


def update_road_segments():
    global road_segments, score

    furthest_segment = min(road_segments)
    
    if car_z < furthest_segment + (num_road_segments - 5) * road_segment_length:
        new_segment = furthest_segment - road_segment_length
        road_segments.append(new_segment)

        if len(road_segments) > num_road_segments:
            road_segments.remove(max(road_segments))

            score += 1

    update_environment_objects()


def draw_terrain():
    glPushMatrix()
    glColor3f(0.0, 0.6, 0.0)

    car_grid_x = round(car_x / terrain_size) * terrain_size

    for x_offset in [-terrain_size, 0, terrain_size]:
        for z_offset in [-terrain_size, 0, terrain_size]:
            glBegin(GL_QUADS)
            glVertex3f(car_grid_x + x_offset - terrain_size / 2, 0, car_z + z_offset - terrain_size / 2)
            glVertex3f(car_grid_x + x_offset - terrain_size / 2, 0, car_z + z_offset + terrain_size / 2)
            glVertex3f(car_grid_x + x_offset + terrain_size / 2, 0, car_z + z_offset + terrain_size / 2)
            glVertex3f(car_grid_x + x_offset + terrain_size / 2, 0, car_z + z_offset - terrain_size / 2)
            glEnd()

    glPopMatrix()


def draw_road():
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)

    for i in range(len(road_segments)):
        segment_z = road_segments[i]
        next_segment_z = road_segments[i + 1] if i + 1 < len(road_segments) else segment_z + road_segment_length

        #road segment
        glBegin(GL_QUADS)
        glVertex3f(-road_width / 2, 0.01, segment_z)
        glVertex3f(-road_width / 2, 0.01, segment_z + road_segment_length)
        glVertex3f(road_width / 2, 0.01, segment_z + road_segment_length)
        glVertex3f(road_width / 2, 0.01, segment_z)
        glEnd()

        #left-border
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glVertex3f(-road_width / 2 - 0.5, 0.0, segment_z)
        glVertex3f(-road_width / 2 - 0.5, 0.5, segment_z)
        glVertex3f(-road_width / 2 - 0.5, 0.5, next_segment_z)
        glVertex3f(-road_width / 2 - 0.5, 0.0, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(-road_width / 2 - 0.5, 0.5, segment_z)
        glVertex3f(-road_width / 2, 0.5, segment_z)
        glVertex3f(-road_width / 2, 0.5, next_segment_z)
        glVertex3f(-road_width / 2 - 0.5, 0.5, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(-road_width / 2, 0.5, segment_z)
        glVertex3f(-road_width / 2, 0.0, segment_z)
        glVertex3f(-road_width / 2, 0.0, next_segment_z)
        glVertex3f(-road_width / 2, 0.5, next_segment_z)
        glEnd()

        #right-border
        glBegin(GL_QUADS)
        glVertex3f(road_width / 2 + 0.5, 0.0, segment_z)
        glVertex3f(road_width / 2 + 0.5, 0.5, segment_z)
        glVertex3f(road_width / 2 + 0.5, 0.5, next_segment_z)
        glVertex3f(road_width / 2 + 0.5, 0.0, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(road_width / 2 + 0.5, 0.5, segment_z)
        glVertex3f(road_width / 2, 0.5, segment_z)
        glVertex3f(road_width / 2, 0.5, next_segment_z)
        glVertex3f(road_width / 2 + 0.5, 0.5, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(road_width / 2, 0.5, segment_z)
        glVertex3f(road_width / 2, 0.0, segment_z)
        glVertex3f(road_width / 2, 0.0, next_segment_z)
        glVertex3f(road_width / 2, 0.5, next_segment_z)
        glEnd()

        glColor3f(0.2, 0.2, 0.2)

    #road striping
    glColor3f(1.0, 1.0, 1.0)
    stripe_length = 3.0
    gap_length = 3.0
    stripe_width = 0.3

    start_z = min(road_segments)
    end_z = max(road_segments) + road_segment_length

    current_z = start_z
    while current_z < end_z:
        if int((current_z - start_z) / (stripe_length + gap_length)) % 2 == 0:
            actual_length = min(stripe_length, end_z - current_z)
            glBegin(GL_QUADS)
            glVertex3f(-stripe_width / 2, 0.02, current_z)
            glVertex3f(-stripe_width / 2, 0.02, current_z + actual_length)
            glVertex3f(stripe_width / 2, 0.02, current_z + actual_length)
            glVertex3f(stripe_width / 2, 0.02, current_z)
            glEnd()

        current_z += stripe_length if int((current_z - start_z) / (stripe_length + gap_length)) % 2 == 0 else gap_length

    glPopMatrix()


def draw_tree(x, z, scale):
    glPushMatrix()

    #tree position
    glTranslatef(x, 0, z)
    glScalef(scale, scale, scale)

    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.3, 3.0, 10, 2)
    glPopMatrix()

    #leaves
    glColor3f(0.1, 0.7, 0.2)
    glPushMatrix()
    glTranslatef(0, 3.0, 0)
    glutSolidSphere(1.5, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_house(x, z, house_type, color):
    glPushMatrix()

    glTranslatef(x, 0, z)
    if x < 0:
        glRotatef(90, 0, 1, 0)
    else:
        glRotatef(-90, 0, 1, 0)

    scale_factor = 2.0
    house_width = 2.5 * scale_factor * 2.0
    house_height = 2.0 * scale_factor * 1.5
    house_depth = 2.5 * scale_factor

    glColor3f(color[0], color[1], color[2])
    glPushMatrix()
    glTranslatef(0, house_height / 2, 0)
    glScalef(house_width, house_height, house_depth)
    glutSolidCube(1.0)
    glPopMatrix()

    # Roof
    glColor3f(0.6, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(0, house_height, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(house_width / 2 * 1.7, 1.5 * scale_factor, 16, 16)
    glPopMatrix()

    #door
    door_color = [random.uniform(0.2, 0.5), random.uniform(0.1, 0.3), random.uniform(0.0, 0.1)]
    glColor3f(door_color[0], door_color[1], door_color[2])
    glPushMatrix()
    glTranslatef(0, 0.5 * scale_factor, house_depth / 2 + 0.01)
    glScalef(0.6 * scale_factor, 1.2 * scale_factor, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    #windows
    window_color = [random.uniform(0.4, 0.8), random.uniform(0.6, 0.9), random.uniform(0.7, 1.0)]
    glColor3f(window_color[0], window_color[1], window_color[2])
    window_positions = [
        (-0.8 * scale_factor, 1.2 * scale_factor), (0.8 * scale_factor, 1.2 * scale_factor),
        (-0.8 * scale_factor, 0.8 * scale_factor), (0.8 * scale_factor, 0.8 * scale_factor)
    ]
    for x_pos, y_pos in window_positions:
        glPushMatrix()
        glTranslatef(x_pos, y_pos, house_depth / 2 + 0.01)
        glScalef(0.6 * scale_factor, 0.5 * scale_factor, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()


def draw_environment():
    for tree in trees:
        draw_tree(tree[0], tree[1], tree[2])

    for i, house in enumerate(houses):
        draw_house(house[0], house[1], house[2], house_colors[i])


def draw_wheel():
    glPushMatrix()

    glRotatef(90, 0, 1, 0)

    #wheel rim
    glColor3f(0.2, 0.2, 0.1)
    glPushMatrix()
    glutSolidCylinder(0.2, 0.1, 16, 8)
    glPopMatrix()

    #wheel tire
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.05)
    glutSolidSphere(0.08, 16, 8)
    glPopMatrix()

    glPopMatrix()





def draw_cpu_car(x, z, direction="forward", color=(0.0, 0.0, 1.0)):
    glPushMatrix()
    glTranslatef(x, 0.5, z)

    if direction == "incoming":
        glRotatef(180, 0, 1, 0)

    #bottombody
    glColor3f(color[0], color[1], color[2])
    glPushMatrix()
    glScalef(1.0, 0.5, 2.0)
    glutSolidCube(0.9)
    glPopMatrix()

    #topbody
    glColor3f(min(color[0] + 0.6, 1.0), min(color[1] + 0.6, 1.0), min(color[2] + 0.6, 1.0))
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.0)
    glScalef(0.8, 0.4, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()

    # Wheels
    wheel_offset = 0.6
    wheel_height = -0.3

    right_wheel_offset = wheel_offset - 0.1

    # Front-left wheel
    glPushMatrix()
    glTranslatef(-wheel_offset, wheel_height, 0.7)
    draw_wheel()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(right_wheel_offset, wheel_height, 0.7)
    draw_wheel()
    glPopMatrix()

    # Rear-left wheel
    glPushMatrix()
    glTranslatef(-wheel_offset, wheel_height, -0.7)
    draw_wheel()
    glPopMatrix()

    # Rear-right wheel
    glPushMatrix()
    glTranslatef(right_wheel_offset, wheel_height, -0.7)
    draw_wheel()
    glPopMatrix()

    glPopMatrix()



def draw_car():
    glPushMatrix()

    #car position and rotation
    glTranslatef(car_x, car_y + 0.5, car_z)
    glRotatef(car_rotation, 0, 1, 0)

    #topbody
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glScalef(1.0, 0.5, 2.0)
    glutSolidCube(0.9)
    glPopMatrix()

    #bottombody
    glColor3f(0.8, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.0)
    glScalef(0.8, 0.4, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()

    #wheels
    wheel_offset = 0.6
    wheel_height = -0.3

    right_wheel_offset = wheel_offset - 0.1

    #front-left wheel
    glPushMatrix()
    glTranslatef(-wheel_offset, wheel_height, 0.7)  # Position left front wheel
    draw_wheel()
    glPopMatrix()

    #front-right wheel
    glPushMatrix()
    glTranslatef(right_wheel_offset, wheel_height, 0.7)
    draw_wheel()
    glPopMatrix()

    #rear-left wheel
    glPushMatrix()
    glTranslatef(-wheel_offset, wheel_height, -0.7)
    draw_wheel()
    glPopMatrix()

    #rear-right wheel
    glPushMatrix()
    glTranslatef(right_wheel_offset, wheel_height, -0.7)
    draw_wheel()
    glPopMatrix()

    glPopMatrix()



def update_camera():
    global camera_x, camera_y, camera_z, look_x, look_y, look_z

    if first_person_view:
        angle_rad = math.radians(car_rotation)
        camera_x = car_x
        camera_z = car_z

        look_x = car_x + math.sin(angle_rad)
        look_y = camera_y - 0.5
        look_z = car_z - math.cos(angle_rad)
    else:
        angle_rad = math.radians(car_rotation)
        camera_x = car_x - 5.0 * math.sin(angle_rad)
        camera_z = car_z + 5.0 * math.cos(angle_rad)

        look_x = car_x
        look_y = car_y + 0.5
        look_z = car_z


def update_car():
    update_cpu_cars()
    global car_x, car_z, car_speed, car_rotation, game_over

    if not game_over:
        angle_rad = math.radians(car_rotation)

        #car movement logics
        if move_forward:
            car_speed += acceleration
            if car_speed > max_speed:
                car_speed = max_speed
        elif move_backward:
            if car_speed > 0:
                car_speed -= acceleration
                if car_speed < 0:
                    car_speed = 0
        else:
            if car_speed > 0:
                car_speed -= deceleration
                if car_speed < 0:
                    car_speed = 0
            elif car_speed < 0:
                car_speed = 0

        max_turn_angle = 90.0

        if abs(car_speed) > 0.05:
            if turn_left:
                car_rotation += turning_speed * (abs(car_speed) / max_speed)
                if car_rotation > max_turn_angle:
                    car_rotation = max_turn_angle
            if turn_right:
                car_rotation -= turning_speed * (abs(car_speed) / max_speed)
                if car_rotation < -max_turn_angle:
                    car_rotation = -max_turn_angle

        #carmovement
        if car_speed != 0:
            car_x += car_speed * math.sin(-angle_rad)
            car_z -= car_speed * math.cos(-angle_rad)

        wheel_offset = 0.6
        if abs(car_x - wheel_offset) > road_width / 2 or abs(car_x + wheel_offset) > road_width / 2:
            game_over = True

        #collision check
        for car in cpu_cars:
            if (abs(car.x - car_x) < 1.0 and abs(car.z - car_z) < 1.0):
                player_left_wheel = car_x - wheel_offset
                player_right_wheel = car_x + wheel_offset

                cpu_left_wheel = car.x - wheel_offset
                cpu_right_wheel = car.x + wheel_offset

                #left wheel collision
                if abs(player_left_wheel - cpu_left_wheel) < 0.2 and abs(car.z - car_z) < 1.0:
                    game_over = True

                #right wheel collision
                if abs(player_right_wheel - cpu_right_wheel) < 0.2 and abs(car.z - car_z) < 1.0:
                    game_over = True
 
        update_road_segments()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width / window_height, 0.1, 1000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    update_camera()
    gluLookAt(camera_x, camera_y, camera_z,
              look_x, look_y, look_z,
              up_x, up_y, up_z)

    #scene components
    draw_terrain()
    draw_road()
    draw_environment()
    draw_car()
    for car in cpu_cars:
        draw_cpu_car(car.x, car.z, direction='forward', color=car.color)

    #score and speed
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    #display score
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(10, window_height - 20)
    score_text = f"Score: {score}"
    for character in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

    #display speed
    glRasterPos2f(10, window_height - 40)
    speed_text = f"Speed: {car_speed:.2f}"
    for character in speed_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

    #game over message
    if game_over:
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(window_width / 2 - 50, window_height / 2 + 20)
        game_over_text = "Game Over!"
        for character in game_over_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

        #displayscore
        glRasterPos2f(window_width / 2 - 50, window_height / 2)
        score_message = f"You Scored {score}!"
        for character in score_message:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

        #display restart
        glRasterPos2f(window_width / 2 - 50, window_height / 2 - 20)
        restart_message = "Press 'r' to restart"
        for character in restart_message:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

    # Display controls
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(10, 20)
    controls_text = "Controls: W/S - Accelerate/Brake, A/D - Turn, V - Change View, Arrow Keys - Adjust Camera"
    for character in controls_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()



def reshape(width, height):
    """Handle window resizing"""
    global window_width, window_height
    window_width = width
    window_height = height
    glViewport(0, 0, width, height)


def keyboard(key, x, y):
    """Handle keyboard input"""
    global car_rotation, car_speed, first_person_view, game_over, score
    global move_forward, move_backward, turn_left, turn_right

    if game_over and key == b'r':
        restart_game()
        return

    if not game_over:
        if key == b'w':
            move_forward = True
        elif key == b's':
            move_backward = True
        elif key == b'a':
            turn_left = True
        elif key == b'd':
            turn_right = True
        elif key == b'v':
            first_person_view = not first_person_view

    glutPostRedisplay()


def keyboard_up(key, x, y):
    global move_forward, move_backward, turn_left, turn_right

    if key == b'w':
        move_forward = False
    elif key == b's':
        move_backward = False
    elif key == b'a':
        turn_left = False
    elif key == b'd':
        turn_right = False


def special_keys(key, x, y):
    """Handle special key inputs (arrow keys)"""
    global camera_y

    if key == GLUT_KEY_UP:
        camera_y += 0.5
    elif key == GLUT_KEY_DOWN:
        camera_y -= 0.5
        if camera_y < 1.0:
            camera_y = 1.0

    glutPostRedisplay()


def mouse(button, state, x, y):
    """Handle mouse input"""
    global first_person_view

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_view = not first_person_view
        glutPostRedisplay()


def update_cpu_cars():
    global cpu_cars, score, game_over, cpu_spawn_timer, num_cars, cpu_spawn_interval

    # Adjust CPU car spawn interval based on the score
    if score < 5000:
        cpu_spawn_interval = 350
    elif score < 10000:
        cpu_spawn_interval = 300
    elif score < 15000:
        cpu_spawn_interval = 250
    else:
        cpu_spawn_interval = 180

    # Start with fewer CPU cars and increment slower
    if score < 10000:
        num_cars = 1 + (score // 5000)
        if num_cars > 2:
            num_cars = 2
    else:
        num_cars = 2

    cpu_spawn_timer += 1
    if cpu_spawn_timer >= cpu_spawn_interval:
        cpu_spawn_timer = 0

        lanes = [-road_width / 4, 0, road_width / 4]

        for _ in range(num_cars):
            car_spawned = False
            while not car_spawned:
                spawn_x = random.choice(lanes) + random.uniform(-1.0, 1.0)
                spawn_z = car_z - 80
                speed = 0.2 
                color = (random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))

                min_distance = 1.5
                overlap = False
                for car in cpu_cars:
                    distance = math.sqrt((spawn_x - car.x) ** 2 + (spawn_z - car.z) ** 2)
                    if distance < min_distance:
                        overlap = True
                        break

                if not overlap:
                    cpu_cars.append(CpuCar(spawn_x, spawn_z, speed, color))
                    car_spawned = True

    for car in cpu_cars:
        car.z -= car.speed

        if car.z > car_z and not car.overtaken:
            score += 100
            car.overtaken = True

        if car.z < car_z and abs(car.x - car_x) < 1.0 and abs(car.z - car_z) < 2.0:
            game_over = True

    cpu_cars = [c for c in cpu_cars if c.z > car_z - 150]


def idle():
    update_car()
    update_cpu_cars()
    glutPostRedisplay()


def restart_game():
    global car_x, car_y, car_z, car_rotation, car_speed, game_over, score
    global move_forward, move_backward, turn_left, turn_right
    global cpu_spawn_timer

    car_x = 0.0
    car_y = 0.0
    car_z = 0.0
    car_rotation = 0.0
    car_speed = 0.0
    game_over = False
    score = 0

    cpu_spawn_timer = 0

    #resetting movements
    move_forward = False
    move_backward = False
    turn_left = False
    turn_right = False

    #road environment
    generate_road_segments()
    generate_environment_objects()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"3D Car Racing Game - Infinite Road")

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)

    init()
    generate_road_segments()
    generate_environment_objects()
    restart_game()

    glutMainLoop()


if __name__ == "__main__":
    main()
