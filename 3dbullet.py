import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import tkinter as tk
from tkinter import ttk

bullet_speed = 30
distance = 0
force = 0


class Bullet:
    def __init__(self, position, direction, radius, mass):
        self.position = position
        self.direction = direction
        self.initial_position = position.copy()
        self.velocity = direction * bullet_speed
        self.mass = mass
        self.radius = radius


class Cube:
    def __init__(self, position, size, velocity, rotation, material_color, mass, is_wooden):
        self.position = position
        self.size = size
        self.velocity = velocity
        self.rotation = rotation
        self.material_color = material_color
        self.mass = mass
        self.is_wooden = is_wooden


def draw_object(position, size, shape, material_color):
    glColor3fv(material_color)  # Set the object color based on the material color

    glPushMatrix()
    glTranslate(*position)
    if shape == "cube":
        draw_cube(*size)
    elif shape == "sphere":
        draw_sphere(size)
    glPopMatrix()


def draw_cube(width, height, depth):
    half_width = width / 2.0
    half_height = height / 2.0
    half_depth = depth / 2.0
    vertices = [
        [-half_width, -half_height, half_depth],
        [half_width, -half_height, half_depth],
        [half_width, half_height, half_depth],
        [-half_width, half_height, half_depth],
        [-half_width, -half_height, -half_depth],
        [half_width, -half_height, -half_depth],
        [half_width, half_height, -half_depth],
        [-half_width, half_height, -half_depth]
    ]
    faces = [
        [0, 1, 2, 3],  # Front
        [1, 5, 6, 2],  # Right
        [5, 4, 7, 6],  # Back
        [4, 0, 3, 7],  # Left
        [3, 2, 6, 7],  # Top
        [4, 5, 1, 0]   # Bottom
    ]

    glBegin(GL_QUADS)
    for face in faces:
        for vertex_index in face:
            glVertex3fv(vertices[vertex_index])
    glEnd()


def draw_sphere(radius):
    quad = gluNewQuadric()
    gluSphere(quad, float(radius), 8, 8)


def draw_floor():
    glColor3f(0.5, 0.5, 0.5)  # Set the floor color to gray

    vertices = [
        [-50, -1, 50],
        [50, -1, 50],
        [50, -1, -50],
        [-50, -1, -50]
    ]

    glBegin(GL_QUADS)
    for vertex in vertices:
        glVertex3fv(vertex)
    glEnd()


def check_collision(position1, size1, position2, size2):
    x_collision = abs(position1[0] - position2[0]) <= (size1[0] + size2[0]) / 2
    y_collision = abs(position1[1] - position2[1]) <= (size1[1] + size2[1]) / 2
    z_collision = abs(position1[2] - position2[2]) <= (size1[2] + size2[2]) / 2
    return x_collision and y_collision and z_collision


def apply_gravity(object, dt, gravity):
    object.velocity[1] += gravity * dt
    object.position += object.velocity * dt

    # Stop the object from going below the floor
    if object.position[1] - object.size[1] / 2 < -1:
        object.position[1] = -1 + object.size[1] / 2
        object.velocity[1] = 0


def update_physics(object, dt):
    object.momentum = object.velocity * object.mass
    object.position += object.velocity * dt


def calculate_distance(position1, position2):
    return np.linalg.norm(position1 - position2)


def print_physics_info(object):
    print(f"Velocity: {bullet_speed} m/s")
    print(f"Mass: {object.mass} KG")
    print("--------")


def calculate_collision_force(mass, dt):
    acceleration = bullet_speed / dt  # Calculate acceleration using velocity change and time
    force = mass * acceleration  # Calculate force using mass and acceleration
    return force


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Object Properties")
        self.window.geometry("300x300")

        self.bullet_radius = tk.StringVar()
        self.bullet_speed = tk.StringVar()
        self.bullet_mass = tk.StringVar()
        self.cube_mass = tk.StringVar()
        self.other_object_mass = tk.StringVar()

        self.bullet_radius_label = ttk.Label(self.window, text="Bullet Size:")
        self.bullet_radius_label.pack()
        self.bullet_radius_entry = ttk.Entry(self.window, textvariable=self.bullet_radius)
        self.bullet_radius_entry.pack()

        self.bullet_speed_label = ttk.Label(self.window, text="Bullet Speed:")
        self.bullet_speed_label.pack()
        self.bullet_speed_entry = ttk.Entry(self.window, textvariable=self.bullet_speed)
        self.bullet_speed_entry.pack()

        self.bullet_mass_label = ttk.Label(self.window, text="Bullet Mass:")
        self.bullet_mass_label.pack()
        self.bullet_mass_entry = ttk.Entry(self.window, textvariable=self.bullet_mass)
        self.bullet_mass_entry.pack()

        self.cube_mass_label = ttk.Label(self.window, text="Cube Mass:")
        self.cube_mass_label.pack()
        self.cube_mass_entry = ttk.Entry(self.window, textvariable=self.cube_mass)
        self.cube_mass_entry.pack()

        self.other_object_mass_label = ttk.Label(self.window, text="Other Object Mass:")
        self.other_object_mass_label.pack()
        self.other_object_mass_entry = ttk.Entry(self.window, textvariable=self.other_object_mass)
        self.other_object_mass_entry.pack()

        self.start_button = ttk.Button(self.window, text="Start", command=self.start)
        self.start_button.pack()

        self.physics_window = tk.Toplevel(self.window)
        self.physics_window.title("Physics Information")
        self.physics_window.geometry("300x300")

        self.physics_text = tk.Text(self.physics_window)
        self.physics_text.pack()

        self.force_label = ttk.Label(self.physics_window, text="Force: N/A")
        self.force_label.pack()

        self.velocity_label = ttk.Label(self.physics_window, text="Velocity: N/A")
        self.velocity_label.pack()

        self.mass_label = ttk.Label(self.physics_window, text="Mass: N/A")
        self.mass_label.pack()

        self.distance_label = ttk.Label(self.physics_window, text="Distance: N/A")
        self.distance_label.pack()

        self.physics_window.after(100, self.update_physics_info_periodically)  # Start updating physics information

        self.physics_window.mainloop()
        self.window.mainloop()

    def update_physics_info(self, force, velocity, mass, distance):
        self.physics_text.delete(1.0, tk.END)
        self.physics_text.insert(tk.END, f"Force: {force} N\n")
        self.physics_text.insert(tk.END, f"Velocity: {velocity} m/s\n")
        self.physics_text.insert(tk.END, f"Mass: {mass} KG\n")
        self.physics_text.insert(tk.END, f"Distance: {distance}\n")
        self.physics_window.update_idletasks() 

    def update_physics_info_periodically(self):
        bullet = self.bullets[0]  # Assuming only one bullet is fired at a time
        distance = calculate_distance(bullet.initial_position, self.cube.position)
        self.update_physics_info(force, bullet_speed, bullet.mass, distance)
        self.window.after(100, self.update_physics_info_periodically)


    def start(self):
        bullet_radius = float(self.bullet_radius.get())
        bullet_speed = float(self.bullet_speed.get())
        bullet_mass = float(self.bullet_mass.get())
        cube_mass = float(self.cube_mass.get())
        other_object_mass = float(self.other_object_mass.get())
        # self.window.destroy()

        self.window.withdraw() 

        self.run_scene(bullet_radius, bullet_speed, cube_mass, other_object_mass, bullet_mass)
        self.update_physics_info_periodically()

    def run_scene(self, bullet_radius, speed, cube_mass, other_object_mass, bullet_mass):
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 24)

        global bullet_speed
        global distance
        global force

        bullet_speed = speed

        distance_text = font.render("Distance: {:.2f}".format(distance), True, (0, 0, 0))
        velocity_text = font.render("Velocity: {:.2f} m/s".format(bullet_speed), True, (0, 0, 0))
        mass_text = font.render("Mass: {:.2f} KG".format(bullet_mass), True, (0, 0, 0))
        force_text = font.render("Force: {:.2f} N".format(force), True, (0, 0, 0))

        # Set the position to display the text
        text_position = (10, 50)

        pygame.init()
        display = (800, 600)
        surface = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.set_pos(display[0] // 2, display[1] // 2)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)  # Set the background color to white

        camera_pos = np.array([0, 0, 5], dtype='float64')
        camera_front = np.array([0, 0, -1], dtype='float64')
        camera_up = np.array([0, 1, 0], dtype='float64')

        yaw, pitch = 0, 0
        move_speed = 0.1
        jump_speed = 0.5
        is_jumping = False

        gravity = -9.81  # m/s^2

        clock = pygame.time.Clock()

        cube = Cube(np.array([0, 1, -5], dtype='float64'), np.array([0.5, 0.5, 0.5]), np.zeros(3), np.zeros(3),
                    (0.6, 0.3, 0.0), cube_mass, True)
        other_object = Cube(np.array([3, 1, -5], dtype='float64'), np.array([0.8, 0.8, 0.8]), np.zeros(3), np.zeros(3),
                            (0.0, 0.0, 1.0), other_object_mass, False)

        bullets = []  # List to store bullets

        cube_pieces = []  # List to store smaller cube pieces
        glass_pieces = []  # List to store shattered glass pieces

        font = pygame.font.Font(None, 36)  # Create a font object for the UI text
        speed_options = {
            K_1: 30,
            K_2: 60,
            K_3: 90
        }  # Mapping of key codes to bullet speeds

        while True:
            dt = clock.tick(60) / 1000.0
            collision_detected = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Add a bullet with the current camera position and direction
                    bullet_pos = np.copy(camera_pos)
                    bullet_direction = np.copy(camera_front)
                    bullets.append(Bullet(bullet_pos, bullet_direction, bullet_radius, bullet_mass))

                if event.type == pygame.KEYDOWN:
                    if event.key in speed_options:
                        bullet_speed = speed_options[event.key]  # Update the bullet speed
                        pygame.display.set_caption("Bullet Speed: " + str(bullet_speed))  # Update the window caption

            keys = pygame.key.get_pressed()
            if keys[K_w]:
                camera_pos += move_speed * camera_front
            if keys[K_s]:
                camera_pos -= move_speed * camera_front
            if keys[K_a]:
                camera_pos -= np.cross(camera_front, camera_up) * move_speed
            if keys[K_d]:
                camera_pos += np.cross(camera_front, camera_up) * move_speed
            if keys[K_SPACE] and not is_jumping:
                camera_pos += jump_speed * camera_up
                is_jumping = True

            # Collision detection with the floor
            if camera_pos[1] < -1 + 0.5:  # Assume user's height as 1.0 and floor level at -1.0
                camera_pos[1] = -1 + 0.5  # Restrict camera's y-position to the floor level
                is_jumping = False

            mouse_rel = pygame.mouse.get_rel()
            x_offset, y_offset = mouse_rel
            sensitivity = 0.1
            yaw += x_offset * sensitivity
            pitch -= y_offset * sensitivity

            pitch = np.clip(pitch, -89.0, 89.0)

            front = np.array([
                np.cos(np.radians(yaw)) * np.cos(np.radians(pitch)),
                np.sin(np.radians(pitch)),
                np.sin(np.radians(yaw)) * np.cos(np.radians(pitch))
            ])
            camera_front = front / np.linalg.norm(front)

            glLoadIdentity()
            gluLookAt(*camera_pos, *(camera_pos + camera_front), *camera_up)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            apply_gravity(cube, dt, gravity)
            apply_gravity(other_object, dt, gravity)

            draw_object(cube.position, cube.size, "cube", cube.material_color)
            draw_object(other_object.position, other_object.size, "cube", other_object.material_color)
            draw_floor()

            bullets_to_keep = []
            for bullet in bullets:
                bullet_pos = bullet.position  # Get the position attribute

                # Apply gravity to the bullet
                bullet.velocity[1] += gravity * dt
                bullet.position += bullet.velocity * dt

                # Apply air resistance to the bullet
                air_resistance = 0.05  # Adjust the air resistance factor as desired
                bullet.velocity *= (1 - air_resistance)
                draw_object(bullet.position, bullet.radius, "sphere", (1.0, 0.0, 0.0))

                bullets_to_keep.append(bullet)  # Add the bullet to bullets_to_keep

                # Check collision between the bullet and the cube
                if check_collision(bullet_pos, (bullet.radius, bullet.radius, bullet.radius), cube.position, cube.size):
                    print("Collision with cube detected!")
                    collision_detected = True
                    bullets_to_keep.append(bullet)

                    # Calculate collision force
                    force = calculate_collision_force(bullet.mass, dt)
                    print("Force applied to cube:", str(force) + " N")

                    # Break the cube into smaller pieces
                    num_pieces = 10  # Number of smaller cubes to create
                    piece_size = cube.size / np.sqrt(num_pieces)  # Size of each smaller cube

                    distance = calculate_distance(bullet.initial_position, cube.position)
                    self.update_physics_info(force, bullet_speed, bullet_mass, distance)

                    # Adjust the impact effect based on the distance
                    impact_factor = max(0, 1 - distance / 100)  # Adjust the divisor to control the drop-off rate
                    piece_size = cube.size / np.sqrt(num_pieces) * impact_factor
                    print("distance", distance)

                    for _ in range(num_pieces):
                        # Calculate position, velocity, and rotation for each smaller cube
                        piece_position = cube.position + np.random.uniform(-0.5, 0.5, size=3) * cube.size * 0.25

                        # Calculate velocity direction away from the collision point
                        velocity_direction = np.random.uniform(-1, 1, size=3)
                        collision_direction = bullet.direction
                        if np.dot(velocity_direction, collision_direction) > 0:
                            velocity_direction = -velocity_direction
                        piece_velocity = velocity_direction * np.linalg.norm(cube.size) * 5 * impact_factor * (
                                bullet_speed / 10)

                        piece_rotation = np.random.uniform(-180, 180, size=3)

                        # Create a new Cube instance and add it to the list
                        piece_mass = cube_mass / num_pieces  # Distribute the mass equally among the smaller pieces
                        piece = Cube(piece_position, piece_size, piece_velocity, piece_rotation, cube.material_color,
                                     piece_mass, True)
                        cube_pieces.append(piece)

                        piece_size *= impact_factor

                    # Reset the cube position and size
                    cube.position = np.array([0, 1, -5], dtype='float64')  # Initial cube position
                    cube.size = np.array([0.5, 0.5, 0.5])  # Size of the cube

                # Check collision between the bullet and the other object
                if check_collision(bullet_pos, (bullet.radius, bullet.radius, bullet.radius), other_object.position,
                                   other_object.size):
                    print("Collision with other object detected!")
                    collision_detected = True
                    bullets_to_keep.append(bullet)

                    # Calculate collision force
                    force = calculate_collision_force(bullet.mass, dt)
                    print("Force applied to other object:", force)

                    # Break the other object into smaller pieces
                    num_pieces = 24  # Number of smaller cubes to create
                    piece_size = other_object.size / np.sqrt(num_pieces)  # Size of each smaller cube

                    distance = calculate_distance(bullet.initial_position, other_object.position)
                    self.update_physics_info(force, bullet_speed, bullet_mass, distance)

                    # Adjust the impact effect based on the distance
                    impact_factor = max(0, 1 - distance / 100)  # Adjust the divisor to control the drop-off rate
                    piece_size = cube.size / np.sqrt(num_pieces) * impact_factor

                    for _ in range(num_pieces):
                        # Calculate position, velocity, and rotation for each smaller cube
                        piece_position = other_object.position + np.random.uniform(-0.5, 0.5, size=3) * other_object.size * 0.25

                        # Calculate velocity direction away from the collision point
                        velocity_direction = np.random.uniform(-1, 1, size=3)
                        collision_direction = bullet.direction
                        if np.dot(velocity_direction, collision_direction) > 0:
                            velocity_direction = -velocity_direction
                        piece_velocity = velocity_direction * np.linalg.norm(other_object.size) * 5 * impact_factor * (
                                bullet_speed / 15)

                        piece_rotation = np.random.uniform(-180, 180, size=3)

                        # Create a new Cube instance and add it to the list
                        piece_mass = other_object_mass / num_pieces  # Distribute the mass equally among the smaller pieces
                        piece = Cube(piece_position, piece_size, piece_velocity, piece_rotation, other_object.material_color,
                                     piece_mass, False)
                        cube_pieces.append(piece)

                        piece_size *= impact_factor

                    # Reset the other object position and size
                    other_object.position = np.array([3, 1, -5], dtype='float64')  # Initial other object position
                    other_object.size = np.array([0.8, 0.8, 0.8])  # Size of the other object

                if collision_detected:
                    print("Bullet Physics Info:")
                    print_physics_info(
                        Cube(bullet_pos, np.zeros(3), np.zeros(3), np.zeros(3), (0.0, 0.0, 0.0), bullet.mass, True))
                    print("--------")
                    collision_detected = False

            bullets = bullets_to_keep

            for piece in cube_pieces:
                update_physics(piece, dt)
                draw_object(piece.position, piece.size, "cube", piece.material_color)

            for piece in glass_pieces:
                update_physics(piece, dt)
                draw_object(piece.position, piece.size, "cube", (0.0, 0.0, 1.0))  # Set the shattered glass color to blue

            cube_pieces = [piece for piece in cube_pieces if piece.position[1] - piece.size[1] / 2 > -1]
            glass_pieces = [piece for piece in glass_pieces if piece.position[1] - piece.size[1] / 2 > -1]

            surface.blit(distance_text, (10, 50))
            surface.blit(velocity_text, (10, 80))
            surface.blit(mass_text, (10, 110))
            surface.blit(force_text, (10, 140))

            pygame.display.flip()

if __name__ == "__main__":
    gui = GUI()
