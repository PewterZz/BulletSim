
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutSolidSphere 
import pybullet as p
import pybullet_data
import numpy as np

def draw_floor():
    glColor3f(0.5, 0.5, 0.5)  # Set the floor color to black

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

def draw_bullet(position):
    glColor3f(1.0, 0.0, 0.0)  # Set the bullet color to red

    glPushMatrix()
    glTranslate(*position)
    quadric = gluNewQuadric()
    gluSphere(quadric, 0.1, 8, 8)  # Draw a sphere with radius 0.1
    glPopMatrix()

def draw_target():
    glColor3f(0.0, 0.0, 1.0)  # Set the target color to blue

    glPushMatrix()
    glTranslate(0, 1, -10)  # Position the target

    # Draw the target cube
    size = 1.0  # Size of the cube
    half_size = size / 2.0

    glBegin(GL_QUADS)

    # Front face
    glVertex3f(-half_size, -half_size, half_size)
    glVertex3f(half_size, -half_size, half_size)
    glVertex3f(half_size, half_size, half_size)
    glVertex3f(-half_size, half_size, half_size)

    # Back face
    glVertex3f(-half_size, -half_size, -half_size)
    glVertex3f(half_size, -half_size, -half_size)
    glVertex3f(half_size, half_size, -half_size)
    glVertex3f(-half_size, half_size, -half_size)

    # Left face
    glVertex3f(-half_size, -half_size, -half_size)
    glVertex3f(-half_size, -half_size, half_size)
    glVertex3f(-half_size, half_size, half_size)
    glVertex3f(-half_size, half_size, -half_size)

    # Right face
    glVertex3f(half_size, -half_size, -half_size)
    glVertex3f(half_size, -half_size, half_size)
    glVertex3f(half_size, half_size, half_size)
    glVertex3f(half_size, half_size, -half_size)

    # Top face
    glVertex3f(-half_size, half_size, -half_size)
    glVertex3f(half_size, half_size, -half_size)
    glVertex3f(half_size, half_size, half_size)
    glVertex3f(-half_size, half_size, half_size)

    # Bottom face
    glVertex3f(-half_size, -half_size, -half_size)
    glVertex3f(half_size, -half_size, -half_size)
    glVertex3f(half_size, -half_size, half_size)
    glVertex3f(-half_size, -half_size, half_size)

    glEnd()

    glPopMatrix()


def create_target_pieces():
    # Create individual target pieces
    piece_size = 0.5
    piece_mass = 1.0
    piece_collision_shapes = []
    piece_collision_ids = []
    positions = [
        [0.25, 0.25, -10],
        [-0.25, 0.25, -10],
        [0.25, -0.25, -10],
        [-0.25, -0.25, -10]
    ]

    for position in positions:
        collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[piece_size, piece_size, piece_size])
        piece_collision_shapes.append(collision_shape)
        visual_shape = -1  # No visual representation, only collision shape
        collision_id = p.createMultiBody(
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex= visual_shape,
            baseMass=piece_mass,
            basePosition=position
        )
        piece_collision_ids.append(collision_id)

    return piece_collision_shapes, piece_collision_ids


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    pygame.mouse.set_visible(False)  # Make the mouse cursor invisible
    pygame.event.set_grab(True)      # Lock the mouse cursor to the program window
    pygame.mouse.set_pos(display[0] // 2, display[1] // 2)  # Reset the mouse position to the center of the screen
    pygame.mouse.set_pos(display[0] // 2, display[1] // 2)  # Reset the mouse position to the center of the screen


    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Set the background color to white

    camera_pos = np.array([0, 0, 5], dtype='float64')
    camera_front = np.array([0, 0, -1], dtype='float64')
    camera_up = np.array([0, 1, 0], dtype='float64')

    yaw, pitch = 0, 0

    # Define variables for gravity
    gravity = -9.81  # m/s^2
    velocity = np.array([0.0, 0.0, 0.0], dtype='float64')
    jump_speed = 5.0

    clock = pygame.time.Clock()

    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())

    # Create a bullet object in PyBullet
    bullet_collision_shape = p.createCollisionShape(p.GEOM_SPHERE, radius=0.1)
    bullet_visual_shape = -1  # No visual representation, only collision shape
    bullet_mass = 1.0
    bullet_collision_id = p.createMultiBody(
        baseCollisionShapeIndex=bullet_collision_shape,
        baseVisualShapeIndex=bullet_visual_shape,
        baseMass=bullet_mass
    )

    target_collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[1, 1, 1])
    target_visual_shape = -1  # No visual representation, only collision shape
    target_mass = 0  # Static target, mass set to 0
    target_collision_id = p.createMultiBody(
        baseCollisionShapeIndex=target_collision_shape,
        baseVisualShapeIndex=target_visual_shape,
        baseMass=target_mass,
        basePosition=[0, 1, -10]  # Position the target
    )

    target_piece_collision_shapes, target_piece_collision_ids = create_target_pieces()

    bullets = []
    bullet_speed = 200.0

    while True:
        dt = clock.tick(60) / 1000.0  # Get time since last frame in seconds

        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Left mouse button pressed, shoot a bullet
                bullet_pos = camera_pos + camera_front * 0.5  # Initial position of the bullet
                bullet_vel = camera_front * bullet_speed  # Initial velocity of the bullet
                bullets.append((bullet_pos, bullet_vel))  

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEMOTION:
                x_offset, y_offset = event.rel
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Jump if space is pressed
                    if abs(camera_pos[1]) < 0.001:
                        velocity[1] = jump_speed

        keys = pygame.key.get_pressed()
        speed = 5.0 * dt

        # Apply gravity to the camera's vertical position
        velocity[1] += gravity * dt
        camera_pos += velocity * dt

        # Keep the camera above the floor
        if camera_pos[1] < 1.0:
            camera_pos[1] = 1.0
            velocity[1] = 0.0

        if keys[pygame.K_w]:
            camera_pos += speed * camera_front
        if keys[pygame.K_s]:
            camera_pos -= speed * camera_front
        if keys[pygame.K_a]:
            camera_pos -= np.cross(camera_front, camera_up) * speed
        if keys[pygame.K_d]:
            camera_pos += np.cross(camera_front, camera_up) * speed

        glLoadIdentity()
        gluLookAt(*(camera_pos.tolist() + (camera_pos + camera_front).tolist() + camera_up.tolist()))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        p.stepSimulation()

        bullets_to_remove = []  # List to store bullets that need to be removed

        for bullet_pos, bullet_vel in bullets:
            bullet_pos += bullet_vel * dt  # Move the bullet based on its velocity
            bullet_vel += np.array([0.0, gravity, 0.0]) * dt  # Apply gravity to the bullet velocity
            draw_bullet(bullet_pos)

            # Update the bullet position and velocity in PyBullet
            p.resetBasePositionAndOrientation(
                bullet_collision_id,
                [bullet_pos[0], bullet_pos[1], bullet_pos[2]],
                [0, 0, 0, 1]  # Bullet orientation (identity quaternion)
            )
            p.resetBaseVelocity(bullet_collision_id, [bullet_vel[0], bullet_vel[1], bullet_vel[2]])

            # Check for collision with the target pieces in PyBullet
            for collision_id in target_piece_collision_ids:
                contact_points = p.getContactPoints(bullet_collision_id, collision_id)
                if contact_points:
                    # Bullet collided with a target piece
                    print("Bullet hit a target piece!")
                    # Remove the collided target piece from the simulation
                    p.removeBody(collision_id)
                    target_piece_collision_ids.remove(collision_id)
                    # Step the simulation again to update the target state
                    p.stepSimulation()

                    # Add the bullet to the removal list
                    bullets_to_remove.append((bullet_pos, bullet_vel))

        # Remove bullets that are out of bounds or have hit a target piece
        for bullet in bullets_to_remove:
            bullets.remove(bullet)


        draw_target()

        draw_floor() 
        pygame.display.flip()



if __name__ == "__main__":
    main()

