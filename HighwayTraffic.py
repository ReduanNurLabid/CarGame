from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Global variables and game state
window_width = 800
window_height = 600

# Camera variables
camera_x = 0.0
camera_y = 3.0
camera_z = 10.0
look_x = 0.0
look_y = 0.0
look_z = 0.0
up_x = 0.0
up_y = 1.0
up_z = 0.0

# Car position, rotation, and movement
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

# Movement control flags
move_forward = False
move_backward = False
turn_left = False
turn_right = False

# Game state flags
first_person_view = False
game_over = False
score = 0

# Road properties
road_width = 10.0
road_segment_length = 20.0
num_road_segments = 10  # Number of road segments for infinite road illusion
terrain_size = 200.0  # Size of the green terrain

# Road segments and environment objects
road_segments = []  # Road segment positions
trees = []  # Tree positions [x, z, scale]
houses = []  # House positions [x, z, type]
house_colors = []  # House colors
num_trees = 60
num_houses = 20

# CPU cars
class CpuCar:
    def __init__(self, x, z, speed, color):
        self.x = x
        self.z = z
        self.speed = speed
        self.color = color
        self.overtaken = False

cpu_cars = []  # List of CpuCar instances
cpu_spawn_timer = 100
cpu_spawn_interval = 250  # Frames between CPU car spawns (decreased for more frequent spawns)

def init():
    """Initialize OpenGL settings"""
    glClearColor(0.5, 0.7, 1.0, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Setting up light
    light_position = [0, 20, 0, 1]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    # Material properties
    mat_ambient = [0.2, 0.2, 0.2, 1.0]
    mat_diffuse = [0.8, 0.8, 0.8, 1.0]
    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [50.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)


def generate_road_segments():
    """Generate initial road segments for the infinite road"""
    global road_segments
    road_segments = []
    
    for i in range(num_road_segments):
        z_pos = -i * road_segment_length
        road_segments.append(z_pos)


def generate_environment_objects():
    """Generate trees and houses along the road"""
    global trees, houses, house_colors
    trees = []
    houses = []
    house_colors = []
    
    # Generate trees
    for _ in range(num_trees):
        # Place trees closer to the road on either side
        side = random.choice([-1, 1])  # Left or right side of road
        x = side * (road_width/2 + 2 + random.uniform(0.5, 3))  # Closer distance from road edge
        z = random.uniform(-road_segment_length * num_road_segments, 0)  # Along the road
        scale = random.uniform(1.5, 3.0)  # Bigger tree size variation
        trees.append([x, z, scale])
    
    # Generate houses a little farther from the road
    for _ in range(num_houses):
        # Place houses on either side of the road a bit farther than before
        side = random.choice([-1, 1])  # Left or right side of road
        x = side * (road_width/2 + 10 + random.uniform(2, 7))  # Farther distance from road edge
        z = random.uniform(-road_segment_length * num_road_segments, 0)  # Along the road
        house_type = random.randint(0, 2)  # Different house styles
        houses.append([x, z, house_type])
        # Assign a random color for the house
        house_colors.append([random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0)])


def update_environment_objects():
    """Update position of trees and houses as car moves"""
    global trees, houses
    
    # Update tree positions
    for tree in trees:
        # If a tree is too far behind, move it ahead
        if tree[1] > car_z + road_segment_length * 2:
            tree[1] -= road_segment_length * num_road_segments
            # Randomize x position when recycling
            side = random.choice([-1, 1])
            tree[0] = side * (road_width/2 + 2 + random.uniform(0.5, 3))
            tree[2] = random.uniform(1.5, 3.0)  # New scale
    
    # Update house positions
    for house in houses:
        # If a house is too far behind, move it ahead
        if house[1] > car_z + road_segment_length * 2:
            house[1] -= road_segment_length * num_road_segments
            # Randomize x position when recycling
            side = random.choice([-1, 1])
            house[0] = side * (road_width/2 + 8 + random.uniform(1, 5))
            house[2] = random.randint(0, 2)  # New house type


def update_road_segments():
    """Update road segments to create infinite scrolling effect"""
    global road_segments, score
    
    # Find the furthest road segment
    furthest_segment = min(road_segments)
    
    # Check if we need to add new segments as the car moves
    if car_z < furthest_segment + (num_road_segments - 5) * road_segment_length:
        # Add a new segment at the end
        new_segment = furthest_segment - road_segment_length
        road_segments.append(new_segment)
        
        # Remove the segment furthest behind to maintain constant number of segments
        if len(road_segments) > num_road_segments:
            road_segments.remove(max(road_segments))
            
            # Increment score when passing segments
            score += 1
    
    # Update environmental objects
    update_environment_objects()


def draw_terrain():
    """Draw the green terrain that moves with the car"""
    glPushMatrix()
    glColor3f(0.0, 0.6, 0.0)  # Dark green color
    
    # Draw terrain centered around the car's x position
    car_grid_x = round(car_x / terrain_size) * terrain_size
    
    # Draw multiple terrain tiles to create an infinite effect
    for x_offset in [-terrain_size, 0, terrain_size]:
        for z_offset in [-terrain_size, 0, terrain_size]:
            glBegin(GL_QUADS)
            glVertex3f(car_grid_x + x_offset - terrain_size/2, 0, car_z + z_offset - terrain_size/2)
            glVertex3f(car_grid_x + x_offset - terrain_size/2, 0, car_z + z_offset + terrain_size/2)
            glVertex3f(car_grid_x + x_offset + terrain_size/2, 0, car_z + z_offset + terrain_size/2)
            glVertex3f(car_grid_x + x_offset + terrain_size/2, 0, car_z + z_offset - terrain_size/2)
            glEnd()
    
    glPopMatrix()


def draw_road():
    """Draw the infinite road"""
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)  # Dark gray for the road
    
    # Draw each road segment
    for i in range(len(road_segments)):
        segment_z = road_segments[i]
        next_segment_z = road_segments[i+1] if i+1 < len(road_segments) else segment_z + road_segment_length
        
        # Main road segment
        glBegin(GL_QUADS)
        glVertex3f(-road_width/2, 0.01, segment_z)  # Slightly above ground to avoid z-fighting
        glVertex3f(-road_width/2, 0.01, segment_z + road_segment_length)
        glVertex3f(road_width/2, 0.01, segment_z + road_segment_length)
        glVertex3f(road_width/2, 0.01, segment_z)
        glEnd()
        
        # Road border - left side wall (continuous)
        glColor3f(0.5, 0.5, 0.5)  # Light gray for borders
        glBegin(GL_QUADS)
        glVertex3f(-road_width/2 - 0.5, 0.0, segment_z)
        glVertex3f(-road_width/2 - 0.5, 0.5, segment_z)
        glVertex3f(-road_width/2 - 0.5, 0.5, next_segment_z)
        glVertex3f(-road_width/2 - 0.5, 0.0, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(-road_width/2 - 0.5, 0.5, segment_z)
        glVertex3f(-road_width/2, 0.5, segment_z)
        glVertex3f(-road_width/2, 0.5, next_segment_z)
        glVertex3f(-road_width/2 - 0.5, 0.5, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(-road_width/2, 0.5, segment_z)
        glVertex3f(-road_width/2, 0.0, segment_z)
        glVertex3f(-road_width/2, 0.0, next_segment_z)
        glVertex3f(-road_width/2, 0.5, next_segment_z)
        glEnd()
        
        # Road border - right side wall (continuous)
        glBegin(GL_QUADS)
        glVertex3f(road_width/2 + 0.5, 0.0, segment_z)
        glVertex3f(road_width/2 + 0.5, 0.5, segment_z)
        glVertex3f(road_width/2 + 0.5, 0.5, next_segment_z)
        glVertex3f(road_width/2 + 0.5, 0.0, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(road_width/2 + 0.5, 0.5, segment_z)
        glVertex3f(road_width/2, 0.5, segment_z)
        glVertex3f(road_width/2, 0.5, next_segment_z)
        glVertex3f(road_width/2 + 0.5, 0.5, next_segment_z)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(road_width/2, 0.5, segment_z)
        glVertex3f(road_width/2, 0.0, segment_z)
        glVertex3f(road_width/2, 0.0, next_segment_z)
        glVertex3f(road_width/2, 0.5, next_segment_z)
        glEnd()
        
        # Reset to road color for next segment
        glColor3f(0.2, 0.2, 0.2)
    
    # Draw road markings
    glColor3f(1.0, 1.0, 1.0)  # White for the markings
    stripe_length = 3.0
    gap_length = 3.0
    stripe_width = 0.3
    
    # Calculate how many stripes we need based on road segments
    start_z = min(road_segments)
    end_z = max(road_segments) + road_segment_length
    
    # Draw stripes with gaps
    current_z = start_z
    while current_z < end_z:
        # Only draw if we're in a stripe section (not a gap)
        if int((current_z - start_z) / (stripe_length + gap_length)) % 2 == 0:
            actual_length = min(stripe_length, end_z - current_z)
            glBegin(GL_QUADS)
            glVertex3f(-stripe_width/2, 0.02, current_z)
            glVertex3f(-stripe_width/2, 0.02, current_z + actual_length)
            glVertex3f(stripe_width/2, 0.02, current_z + actual_length)
            glVertex3f(stripe_width/2, 0.02, current_z)
            glEnd()
        
        current_z += stripe_length if int((current_z - start_z) / (stripe_length + gap_length)) % 2 == 0 else gap_length
    
    glPopMatrix()


def draw_tree(x, z, scale):
    """Draw a simple tree at the given position with the given scale"""
    glPushMatrix()
    
    # Position the tree
    glTranslatef(x, 0, z)
    glScalef(scale, scale, scale)
    
    # Trunk (vertical cylinder)
    glColor3f(0.4, 0.2, 0.1)  # Brown trunk
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # Rotate cylinder to stand upright
    glutSolidCylinder(0.3, 3.0, 10, 2)  # Radius 0.3, height 3.0
    glPopMatrix()

    # Leaves (sphere on top)
    glColor3f(0.1, 0.7, 0.2)  # Green leaves
    glPushMatrix()
    glTranslatef(0, 3.0, 0)  # Move to top of trunk
    glutSolidSphere(1.5, 10, 10)
    glPopMatrix()
    
    glPopMatrix()


def draw_house(x, z, house_type, color):
    """Draw a simple house at the given position with the given type and color"""
    glPushMatrix()
    
    # Position the house
    glTranslatef(x, 0, z)
    if x < 0:
        glRotatef(90, 0, 1, 0)  # Rotate house 90 degrees clockwise around Y axis for left side houses
    else:
        glRotatef(-90, 0, 1, 0)  # Rotate house -90 degrees for right side houses
    
    # Updated house style - front faces positive Z
    scale_factor = 2.0  # Increased scale factor for bigger houses
    house_width = 2.5 * scale_factor * 2.0  # 2x wider
    house_height = 2.0 * scale_factor * 1.5  # 1.5x taller
    house_depth = 2.5 * scale_factor
    
    # Main building with color
    glColor3f(color[0], color[1], color[2])  # Use random color for house walls
    glPushMatrix()
    glTranslatef(0, house_height / 2, 0)
    glScalef(house_width, house_height, house_depth)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Roof
    glColor3f(0.6, 0.2, 0.1)  # Brownish roof
    glPushMatrix()
    glTranslatef(0, house_height, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(house_width / 2 * 1.7, 1.5 * scale_factor, 16, 16)
    glPopMatrix()
    
    # Door (front side)
    door_color = [random.uniform(0.2, 0.5), random.uniform(0.1, 0.3), random.uniform(0.0, 0.1)]
    glColor3f(door_color[0], door_color[1], door_color[2])  # Random door color
    glPushMatrix()
    glTranslatef(0, 0.5 * scale_factor, house_depth / 2 + 0.01)
    glScalef(0.6 * scale_factor, 1.2 * scale_factor, 0.1)  # Wider and taller door
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Windows (front side)
    window_color = [random.uniform(0.4, 0.8), random.uniform(0.6, 0.9), random.uniform(0.7, 1.0)]
    glColor3f(window_color[0], window_color[1], window_color[2])  # Random window color
    window_positions = [
        (-0.8 * scale_factor, 1.2 * scale_factor), (0.8 * scale_factor, 1.2 * scale_factor),
        (-0.8 * scale_factor, 0.8 * scale_factor), (0.8 * scale_factor, 0.8 * scale_factor)
    ]
    for x_pos, y_pos in window_positions:
        glPushMatrix()
        glTranslatef(x_pos, y_pos, house_depth / 2 + 0.01)
        glScalef(0.6 * scale_factor, 0.5 * scale_factor, 0.1)  # Wider windows
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()


def draw_environment():
    """Draw environment objects (trees, houses)"""
    # Draw all trees
    for tree in trees:
        draw_tree(tree[0], tree[1], tree[2])
    
    # Draw all houses with colors
    for i, house in enumerate(houses):
        draw_house(house[0], house[1], house[2], house_colors[i])



def draw_wheel():
    """Draw a single wheel at the current position"""
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    glutSolidTorus(0.1, 0.2, 8, 16)
    glPopMatrix()

def draw_cpu_car(x, z, direction="forward", color=(0.0, 0.0, 1.0)):
    """Draw a CPU car with the same model as player car but different color"""
    glPushMatrix()
    glTranslatef(x, 0.5, z)
    
    if direction == "incoming":
        glRotatef(180, 0, 1, 0)

    # Car body
    glColor3f(color[0], color[1], color[2])  # CPU car color
    glPushMatrix()
    glScalef(1.0, 0.5, 2.0)
    glutSolidCube(0.9)
    glPopMatrix()

    # Car top
    glColor3f(min(color[0]+0.6,1.0), min(color[1]+0.6,1.0), min(color[2]+0.6,1.0))
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.0)
    glScalef(0.8, 0.4, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Wheels
    glColor3f(0.2, 0.2, 0.1)  # Black wheels
    
    # Front-left wheel
    glPushMatrix()
    glTranslatef(-0.6, -0.2, 0.7)
    draw_wheel()
    glPopMatrix()
    
    # Front-right wheel
    glPushMatrix()
    glTranslatef(0.6, -0.2, 0.7)
    draw_wheel()
    glPopMatrix()
    
    # Rear-left wheel
    glPushMatrix()
    glTranslatef(-0.6, -0.2, -0.7)
    draw_wheel()
    glPopMatrix()
    
    # Rear-right wheel
    glPushMatrix()
    glTranslatef(0.6, -0.2, -0.7)
    draw_wheel()
    glPopMatrix()
    
    glPopMatrix()

def draw_car():
    """Draw a simple car model"""
    glPushMatrix()
    
    # Position and rotate the car
    glTranslatef(car_x, car_y + 0.5, car_z)  # +0.5 to place it on the ground
    glRotatef(car_rotation, 0, 1, 0)
    
    # Car body (main block)
    glColor3f(1.0, 0.0, 0.0)  # Red car
    glPushMatrix()
    glScalef(1.0, 0.5, 2.0)
    glutSolidCube(0.9)
    glPopMatrix()
    
    # Car top (cabin)
    glColor3f(0.8, 0.8, 1.0)  # Light blue windows
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.0)
    glScalef(0.8, 0.4, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Wheels
    glColor3f(0.2, 0.2, 0.1)  # Black wheels
    
    # Front-left wheel
    glPushMatrix()
    glTranslatef(-0.6, -0.2, 0.7)
    draw_wheel()
    glPopMatrix()
    
    # Front-right wheel
    glPushMatrix()
    glTranslatef(0.6, -0.2, 0.7)
    draw_wheel()
    glPopMatrix()
    
    # Rear-left wheel
    glPushMatrix()
    glTranslatef(-0.6, -0.2, -0.7)
    draw_wheel()
    glPopMatrix()
    
    # Rear-right wheel
    glPushMatrix()
    glTranslatef(0.6, -0.2, -0.7)
    draw_wheel()
    glPopMatrix()
    
    glPopMatrix()


def update_camera():
    """Update camera position based on the car and view mode"""
    global camera_x, camera_y, camera_z, look_x, look_y, look_z
    
    if first_person_view:
        # First person view from the car
        # Calculate position slightly above and behind the car's front
        angle_rad = math.radians(car_rotation)
        camera_x = car_x
        # Use global camera_y for height control
        # camera_y = car_y + 1.5  # Higher than the car
        camera_z = car_z
        
        # Look in the direction the car is facing
        look_x = car_x + math.sin(angle_rad)
        # Use camera_y - 0.5 for look_y to look slightly down
        look_y = camera_y - 0.5
        look_z = car_z - math.cos(angle_rad)
    else:
        # Third person view
        # Position the camera behind and above the car
        angle_rad = math.radians(car_rotation)
        camera_x = car_x - 5.0 * math.sin(angle_rad)
        # Use global camera_y for height control
        # camera_y = car_y + 3.0
        camera_z = car_z + 5.0 * math.cos(angle_rad)
        
        # Look at the car
        look_x = car_x
        look_y = car_y + 0.5
        look_z = car_z


def update_car():
    update_cpu_cars()
    """Update car position and rotation"""
    global car_x, car_z, car_speed, car_rotation, game_over
    
    if not game_over:
        # Process car movement
        angle_rad = math.radians(car_rotation)
        
        # Handle acceleration and deceleration
        if move_forward:
            car_speed += acceleration
            if car_speed > max_speed:
                car_speed = max_speed
        elif move_backward:
            car_speed -= acceleration
            if car_speed < max_reverse_speed:
                car_speed = max_reverse_speed
        else:
            # Apply friction (deceleration when no keys are pressed)
            if car_speed > 0:
                car_speed -= deceleration
                if car_speed < 0:
                    car_speed = 0
            elif car_speed < 0:
                car_speed += deceleration
                if car_speed > 0:
                    car_speed = 0
        
        # Limit car rotation to prevent looking back
        max_turn_angle = 90.0
        
        # Handle turning - only turn when moving forward or backward
        if abs(car_speed) > 0.05:
            if turn_left:
                car_rotation += turning_speed * (abs(car_speed) / max_speed)
                if car_rotation > max_turn_angle:
                    car_rotation = max_turn_angle
            if turn_right:
                car_rotation -= turning_speed * (abs(car_speed) / max_speed)
                if car_rotation < -max_turn_angle:
                    car_rotation = -max_turn_angle
        
        # Apply movement based on current rotation and speed
        if car_speed != 0:
            car_x += car_speed * math.sin(-angle_rad)
            car_z -= car_speed * math.cos(-angle_rad)
        
        # Check collision with road borders and crash if speed > 0.35
        if abs(car_x) > road_width/2:
            if abs(car_speed) > 0.35:
                game_over = True
            else:
                # Push car back onto road and reduce speed as penalty
                car_x = road_width/2 * (1 if car_x > 0 else -1)
                car_speed *= 0.8
        
        # Update road segments for infinite effect
        update_road_segments()


def display():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up the camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width/window_height, 0.1, 1000.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    update_camera()
    gluLookAt(camera_x, camera_y, camera_z,
              look_x, look_y, look_z,
              up_x, up_y, up_z)
    
    # Draw scene components
    draw_terrain()
    draw_road()
    draw_environment()  # Draw trees and houses
    draw_car()
    for car in cpu_cars:
        draw_cpu_car(car.x, car.z, direction='forward', color=car.color)
    
    # Draw score
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(10, window_height - 20)
    score_text = f"Score: {score}"
    for character in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    
    # Draw speed meter
    glRasterPos2f(10, window_height - 40)
    speed_text = f"Speed: {car_speed:.2f}"
    for character in speed_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    
    # If game over, display message
    if game_over:
        glColor3f(1.0, 0.0, 0.0)  # Red color for game over message
        glRasterPos2f(window_width / 2 - 50, window_height / 2)
        game_over_text = "Game Over! Press 'r' to restart."
        for character in game_over_text:
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
    
    if game_over and key == b'r':  # Restart game with 'r' key
        restart_game()
        return
    
    if not game_over:
        # Set movement flags
        if key == b'w':
            move_forward = True
        elif key == b's':
            move_backward = True
        elif key == b'a':
            turn_left = True
        elif key == b'd':
            turn_right = True
        elif key == b'v':  # Toggle view mode
            first_person_view = not first_person_view
    
    glutPostRedisplay()


def keyboard_up(key, x, y):
    """Handle keyboard key release"""
    global move_forward, move_backward, turn_left, turn_right
    
    # Clear movement flags on key release
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
    
    # Force redisplay after updating camera height
    glutPostRedisplay()


def mouse(button, state, x, y):
    """Handle mouse input"""
    global first_person_view
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_view = not first_person_view
        glutPostRedisplay()



def update_cpu_cars():
    global cpu_cars, score, game_over, cpu_spawn_timer
    
    global cpu_spawn_timer
    cpu_spawn_timer += 1
    if cpu_spawn_timer >= cpu_spawn_interval:
        cpu_spawn_timer = 0
        # Deterministic number of cars to spawn (1 or 2)
        num_cars = random.randint(1, 2)
        lanes = [-road_width / 4, road_width / 4]  # Left and right lanes
        for _ in range(num_cars):
            spawn_x = random.choice(lanes) + random.uniform(-1.0, 1.0)
            spawn_z = car_z - 80  # Spawn CPU cars 80 units ahead of the player
            speed = 0.2  # Fixed speed
            color = (random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
            cpu_cars.append(CpuCar(spawn_x, spawn_z, speed, color))
    
    # Move CPU cars forward (decrease z to go toward player)
    for car in cpu_cars:
        car.z -= car.speed  # Move forward at fixed speed
        
        # Check overtake
        if car.z < car_z and not car.overtaken:
            score += 100
            car.overtaken = True
        
        # Check collision only if car is in front and close
        if car.z < car_z and abs(car.x - car_x) < 1.0 and abs(car.z - car_z) < 2.0:
            game_over = True

    # Remove cars that are too far behind (increase limit to 100)
    cpu_cars = [c for c in cpu_cars if c.z > car_z - 150]

def idle():
    """Idle function for continuous updates"""
    update_car()
    update_cpu_cars()
    glutPostRedisplay()


def restart_game():
    """Reset the game state"""
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

    # Reset movement flags
    move_forward = False
    move_backward = False
    turn_left = False
    turn_right = False
    
    # Regenerate road segments and environment
    generate_road_segments()
    generate_environment_objects()


def main():
    """Main function"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"3D Car Racing Game - Infinite Road")
    
    # Register callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)  # Added for handling key releases
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
