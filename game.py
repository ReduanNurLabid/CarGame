from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math

# Window dimensions
width, height = 800, 600

# Camera parameters
camera_angle = 0.0
camera_height = 3.0
camera_distance = 7.0

# Player car parameters
player_pos = [0.0, 0.0, 0.0]
player_angle = 0.0  # Angle in degrees, 0 means facing positive z direction
player_speed = 0.0
player_acceleration = 0.02
player_max_speed = 0.1
player_friction = 0.05

# Track parameters for straight track
track_length = 100.0
track_width = 30.0
wall_height = 0.5  # Reduced wall height to avoid blocking camera view
wall_thickness = 3.0

# Race control
race_started = False

# Player start position on circular track near starting line
inner_radius = 15.0
outer_radius = 20.0
start_line_x = (inner_radius + outer_radius) / 2
start_line_z = 0.0
player_start_pos = [start_line_x, 0.0, start_line_z]
player_pos = player_start_pos.copy()
player_angle = 180.0  # Facing backward along the track
player_speed = 0.0

# AI cars parameters
ai_cars = []
num_ai_cars = 4
ai_car_speed = 0.02  # Reduced speed for AI cars

# Obstacles parameters
obstacles = [
    {'type': 'boulder', 'pos': [5.0, 0.0, 5.0], 'radius': 1.0},
    {'type': 'mud', 'pos': [-5.0, 0.0, -5.0], 'radius': 2.0},
    {'type': 'broken_car', 'pos': [0.0, 0.0, -8.0], 'radius': 1.5}
]

def init():
    glClearColor(0.5, 0.8, 1.0, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

def reshape(w, h):
    global width, height
    width, height = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_track():
    # Draw circular track base
    glColor3f(0.2, 0.2, 0.2)  # Dark gray track
    num_segments = 100
    inner_radius = 15.0
    outer_radius = 20.0
    glBegin(GL_QUAD_STRIP)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * i / num_segments
        x_inner = inner_radius * math.cos(theta)
        z_inner = inner_radius * math.sin(theta)
        x_outer = outer_radius * math.cos(theta)
        z_outer = outer_radius * math.sin(theta)
        glVertex3f(x_outer, 0.0, z_outer)
        glVertex3f(x_inner, 0.0, z_inner)
    glEnd()

    # Draw starting line
    glColor3f(1.0, 1.0, 1.0)  # White starting line
    glLineWidth(5.0)
    glBegin(GL_LINES)
    glVertex3f(inner_radius, 0.01, 0.0)
    glVertex3f(outer_radius, 0.01, 0.0)
    glEnd()

def draw_walls():
    # Draw circular walls around the track
    glColor3f(0.7, 0.7, 0.7)  # Light gray walls
    num_segments = 100
    inner_radius = 15.0
    outer_radius = 20.0

    # Outer wall
    glBegin(GL_QUAD_STRIP)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * i / num_segments
        x_outer = outer_radius * math.cos(theta)
        z_outer = outer_radius * math.sin(theta)
        glVertex3f(x_outer, 0.0, z_outer)
        glVertex3f(x_outer, wall_height, z_outer)
    glEnd()

    # Inner wall
    glBegin(GL_QUAD_STRIP)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * i / num_segments
        x_inner = inner_radius * math.cos(theta)
        z_inner = inner_radius * math.sin(theta)
        glVertex3f(x_inner, 0.0, z_inner)
        glVertex3f(x_inner, wall_height, z_inner)
    glEnd()

def draw_wheel():
    glColor3f(0, 0, 0)  # Black wheel
    glutSolidTorus(0.025, 0.07, 6, 25)

def draw_body():
    glColor3f(0.1, 0.1, 0.5)  # Blue body color
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(0.2, 0.4, 0.6)
    glVertex3f(0.6, 0.5, 0.6)
    glVertex3f(0.6, 0.5, 0.2)
    glVertex3f(0.2, 0.4, 0.2)
    # Front side
    glVertex3f(0.2, 0.2, 0.6)
    glVertex3f(0.2, 0.4, 0.6)
    glVertex3f(0.2, 0.4, 0.2)
    glVertex3f(0.2, 0.2, 0.2)
    # Back side
    glVertex3f(0.6, 0.2, 0.6)
    glVertex3f(0.6, 0.5, 0.6)
    glVertex3f(0.6, 0.5, 0.2)
    glVertex3f(0.6, 0.2, 0.2)
    # Left side
    glVertex3f(0.2, 0.2, 0.6)
    glVertex3f(0.6, 0.2, 0.6)
    glVertex3f(0.6, 0.5, 0.6)
    glVertex3f(0.2, 0.4, 0.6)
    # Right side
    glVertex3f(0.2, 0.2, 0.2)
    glVertex3f(0.6, 0.2, 0.2)
    glVertex3f(0.6, 0.5, 0.2)
    glVertex3f(0.2, 0.4, 0.2)
    # Cover top
    glVertex3f(0.7, 0.65, 0.6)
    glVertex3f(0.7, 0.65, 0.2)
    glVertex3f(1.7, 0.65, 0.2)
    glVertex3f(1.7, 0.65, 0.6)
    # Back top
    glVertex3f(1.8, 0.5, 0.6)
    glVertex3f(1.8, 0.5, 0.2)
    glVertex3f(2.1, 0.4, 0.2)
    glVertex3f(2.1, 0.4, 0.6)
    # Back side
    glVertex3f(2.1, 0.4, 0.6)
    glVertex3f(2.1, 0.4, 0.2)
    glVertex3f(2.1, 0.2, 0.2)
    glVertex3f(2.1, 0.2, 0.6)
    # Left back side
    glVertex3f(1.8, 0.2, 0.2)
    glVertex3f(1.8, 0.5, 0.2)
    glVertex3f(2.1, 0.4, 0.2)
    glVertex3f(2.1, 0.2, 0.2)
    # Right back side
    glVertex3f(1.8, 0.2, 0.6)
    glVertex3f(1.8, 0.5, 0.6)
    glVertex3f(2.1, 0.4, 0.6)
    glVertex3f(2.1, 0.2, 0.6)
    # Middle front
    glVertex3f(0.6, 0.5, 0.6)
    glVertex3f(0.6, 0.2, 0.6)
    glVertex3f(1.8, 0.2, 0.6)
    glVertex3f(1.8, 0.5, 0.6)
    # Bottom
    glVertex3f(0.6, 0.2, 0.6)
    glVertex3f(0.6, 0.2, 0.2)
    glVertex3f(1.8, 0.2, 0.2)
    glVertex3f(1.8, 0.2, 0.6)
    # Bottom back
    glVertex3f(0.6, 0.5, 0.2)
    glVertex3f(0.6, 0.2, 0.2)
    glVertex3f(1.8, 0.2, 0.2)
    glVertex3f(1.8, 0.5, 0.2)
    glEnd()

def draw_windows():
    glColor3f(0.3, 0.3, 0.3)  # Window color
    glBegin(GL_QUADS)
    # Front windows
    glVertex3f(0.77, 0.63, 0.2)
    glVertex3f(0.75, 0.5, 0.2)
    glVertex3f(1.2, 0.5, 0.2)
    glVertex3f(1.22, 0.63, 0.2)
    # Back windows
    glVertex3f(1.27, 0.63, 0.2)
    glVertex3f(1.25, 0.5, 0.2)
    glVertex3f(1.65, 0.5, 0.2)
    glVertex3f(1.67, 0.63, 0.2)
    # Front windows (other side)
    glVertex3f(0.77, 0.63, 0.6)
    glVertex3f(0.75, 0.5, 0.6)
    glVertex3f(1.2, 0.5, 0.6)
    glVertex3f(1.22, 0.63, 0.6)
    # Back windows (other side)
    glVertex3f(1.27, 0.63, 0.6)
    glVertex3f(1.25, 0.5, 0.6)
    glVertex3f(1.65, 0.5, 0.6)
    glVertex3f(1.67, 0.63, 0.6)
    glEnd()

def draw_car_model():
    glPushMatrix()
    # Draw body
    draw_body()
    # Draw windows
    draw_windows()
    # Draw wheels
    glPushMatrix()
    glTranslatef(0.6, 0.2, 0.6)
    draw_wheel()
    glTranslatef(0, 0, -0.4)
    draw_wheel()
    glTranslatef(1.1, 0, 0)
    draw_wheel()
    glTranslatef(0, 0, 0.4)
    draw_wheel()
    glPopMatrix()
    glPopMatrix()

def draw_car():
    glPushMatrix()
    # Adjust translation to center car model on position
    glTranslatef(player_pos[0], 0.0, player_pos[2] - 0.75)
    # Rotate by player_angle minus 90 degrees to face forward
    glRotatef(player_angle - 90, 0, 1, 0)
    # Remove scaling to avoid offset issues
    # glScalef(1.0, 1.0, 1.5)  # Scale car lengthwise
    glColor3f(1.0, 0.0, 0.0)  # Red color for player car
    draw_car_model()
    glPopMatrix()

def draw_ai_cars():
    glColor3f(0.0, 0.0, 1.0)  # Blue AI cars
    for car in ai_cars:
        glPushMatrix()
        # Adjust translation to center car model on position
        glTranslatef(car['pos'][0], 0.0, car['pos'][2] - 0.75)
        # Rotate by angle minus 90 degrees to face forward
        glRotatef(car['angle'] - 90, 0, 1, 0)
        # Remove scaling to avoid offset issues
        # glScalef(1.0, 1.0, 1.5)
        draw_car_model()
        glPopMatrix()

def draw_obstacles():
    for obs in obstacles:
        glPushMatrix()
        glTranslatef(obs['pos'][0], 0.0, obs['pos'][2])
        if obs['type'] == 'boulder':
            glColor3f(0.4, 0.3, 0.2)  # Brown boulder
            glutSolidSphere(obs['radius'], 20, 20)
        elif obs['type'] == 'mud':
            glColor3f(0.3, 0.2, 0.1)  # Dark brown mud patch (flat)
            glBegin(GL_QUADS)
            size = obs['radius']
            glVertex3f(-size + obs['pos'][0], 0.01, -size + obs['pos'][2])
            glVertex3f(size + obs['pos'][0], 0.01, -size + obs['pos'][2])
            glVertex3f(size + obs['pos'][0], 0.01, size + obs['pos'][2])
            glVertex3f(-size + obs['pos'][0], 0.01, size + obs['pos'][2])
            glEnd()
        elif obs['type'] == 'broken_car':
            glColor3f(0.5, 0.5, 0.5)  # Gray broken car as cube
            glutSolidCube(obs['radius'] * 1.5)
        glPopMatrix()

def update_camera():
    # Camera behind the player car
    eye_x = player_pos[0] - camera_distance * math.sin(math.radians(player_angle))
    eye_y = camera_height
    eye_z = player_pos[2] - camera_distance * math.cos(math.radians(player_angle))
    center_x = player_pos[0]
    center_y = 0.0
    center_z = player_pos[2]
    up_x, up_y, up_z = 0.0, 1.0, 0.0
    glLoadIdentity()
    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    update_camera()
    draw_track()
    draw_walls()
    draw_car()
    draw_ai_cars()
    draw_obstacles()
    glutSwapBuffers()

# Track keys currently pressed
keys_down = set()

# Additional variables for smooth control
accel = 0.0
heading = 0.0
yrot = 0.0
out = False

def keyboard(key, x, y):
    global keys_down
    key_str = key.decode("utf-8")
    keys_down.add(key_str)
    if key_str == 'r':
        global race_started
        race_started = True
    elif key_str == '\x1b':  # ESC
        sys.exit()

def keyboard_up(key, x, y):
    global keys_down
    key_str = key.decode("utf-8")
    if key_str in keys_down:
        keys_down.remove(key_str)

def idle():
    global player_pos, player_speed, player_angle, ai_cars, race_started, keys_down
    global accel, heading, yrot, out

    if not race_started:
        glutPostRedisplay()
        return

    # Handle acceleration and friction similar to C++ example
    if 'w' in keys_down:
        accel -= 0.01  # Reverse direction: pressing 'w' moves forward (negative accel)
    if 's' in keys_down:
        accel += 0.01  # Pressing 's' moves backward (positive accel)

    # Clamp accel to max speed limits
    if accel < -player_max_speed:
        accel = -player_max_speed
    if accel > player_max_speed:
        accel = player_max_speed

    # Apply friction to gradually reduce accel when no input
    if 'w' not in keys_down and 's' not in keys_down:
        if accel < 0:
            accel += player_friction
            if accel > 0:
                accel = 0
        elif accel > 0:
            accel -= player_friction
            if accel < 0:
                accel = 0

    if 'd' in keys_down:
        heading -= 2.0
        yrot = heading
        if accel < 0:
            accel += 0.005
        else:
            accel -= 0.005

    if 'a' in keys_down:
        heading += 2.0
        yrot = heading
        if accel < 0:
            accel += 0.005
        else:
            accel -= 0.005

    # Update player position based on heading and accel
    player_angle = heading
    player_speed = accel

    rad = math.radians(player_angle)
    new_x = player_pos[0] - math.sin(rad) * accel
    new_z = player_pos[2] - math.cos(rad) * accel

    # Collision detection with circular track boundaries
    track_center_x = 0.0
    track_center_z = 0.0
    inner_radius = 15.0
    outer_radius = 20.0

    dist_from_center = math.sqrt((new_x - track_center_x) ** 2 + (new_z - track_center_z) ** 2)
    if dist_from_center < inner_radius or dist_from_center > outer_radius:
        out = True
        # Instead of stopping immediately, reduce speed gradually
        if accel < 0:
            accel += 0.005  # Slow down forward speed
            if accel > 0:
                accel = 0
        elif accel > 0:
            accel -= 0.005  # Slow down backward speed
            if accel < 0:
                accel = 0
    else:
        if out:
            if 'w' in keys_down:
                accel -= 0.1
            if 's' in keys_down:
                accel += 0.1
            out = False
        player_pos[0] = new_x
        player_pos[2] = new_z

    # Update AI cars positions - move forward along circular track
    for car in ai_cars:
        # Update car angle to follow circular track (increment angle)
        car['angle'] += 1.0  # degrees per frame, adjust speed here
        if car['angle'] >= 360.0:
            car['angle'] -= 360.0

        # Calculate new position based on updated angle
        angle_rad = math.radians(car['angle'])
        radius = (inner_radius + outer_radius) / 2
        car['pos'][0] = radius * math.cos(angle_rad)
        car['pos'][2] = radius * math.sin(angle_rad)

    glutPostRedisplay()

def main():
    global ai_cars
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"3D Car Racing Game")
    init()

    # Initialize AI cars evenly spaced along the width at start line
    start_z = -track_length / 2 + 10.0
    spacing = track_width / (num_ai_cars + 1)
    for i in range(num_ai_cars):
        pos_x = -track_width / 2 + (i + 1) * spacing
        ai_cars.append({'pos': [pos_x, 0.0, start_z], 'angle': 0.0})

    # Initialize AI cars evenly spaced along the circular track near starting line
    angle_spacing = 10.0  # degrees between AI cars
    base_angle = 180.0  # Facing backward along the track
    radius = (inner_radius + outer_radius) / 2
    for i in range(num_ai_cars):
        angle_deg = base_angle + (i - num_ai_cars // 2) * angle_spacing
        angle_rad = math.radians(angle_deg)
        pos_x = radius * math.cos(angle_rad)
        pos_z = radius * math.sin(angle_rad)
        ai_cars.append({'pos': [pos_x, 0.0, pos_z], 'angle': angle_deg})

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
