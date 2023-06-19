import pygame
import random
import math
import numpy as np
from scipy.constants import g

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bullet Physics Demo")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

bullet_speed = 10

# Define bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, shape, drag_coefficient, spin_rate):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = math.radians(angle)
        self.speed = speed
        self.velocity = np.array([math.cos(self.angle) * self.speed, -math.sin(self.angle) * self.speed], dtype=np.float64)
        self.mass = 0.05
        self.shape = shape
        self.drag_coefficient = drag_coefficient
        self.spin_rate = spin_rate
        self.angular_velocity = self.spin_rate * self.shape / 2  # Assume constant angular velocity for simplicity

    def update(self, air_density, wind_speed, wind_direction, latitude):
        # Calculate bullet's acceleration due to air resistance, gravity, and Magnus effect
        bullet_velocity = np.linalg.norm(self.velocity)
        bullet_drag = 0.5 * air_density * bullet_velocity**2 * self.drag_coefficient * self.shape
        bullet_drag *= -1  # Opposite direction of bullet's velocity
        bullet_gravity = np.array([0.0, self.mass * g])
        bullet_coriolis = 2 * self.velocity * np.array([-math.sin(latitude), 0.0])
        bullet_wind = wind_speed * np.array([math.cos(wind_direction), -math.sin(wind_direction)])

        # Calculate Magnus effect force
        bullet_angular_velocity = self.angular_velocity * np.array([0.0, 0.0, 1.0])
        bullet_magnus = np.cross(bullet_angular_velocity, self.velocity)[:, np.newaxis] * self.mass * self.drag_coefficient * self.shape


        self.acceleration = bullet_drag + bullet_gravity + bullet_coriolis + bullet_wind + bullet_magnus

        self.velocity += self.acceleration.flatten()[:2]
        self.rect.move_ip(self.velocity)

        if self.rect.right < 0 or self.rect.left > screen_width or self.rect.bottom < 0 or self.rect.top > screen_height:
            self.kill()

# Define cube class
class Cube(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color, mass):
        super().__init__()
        self.original_image = pygame.Surface((size, size))
        self.original_image.fill(color)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.color = color
        self.size = size
        self.mass = mass
        self.velocity = np.array([0.0, 0.0])  # Change to float arrays
        self.is_broken = False

    def update(self, air_density, wind_speed, wind_direction, latitude):
        if not self.is_broken:
            self.velocity += np.array([0.0, self.mass * g])  # Use the g constant as a float
            self.rect.move_ip(self.velocity)

            # Simulate a floor
            if self.rect.bottom >= screen_height:
                self.rect.bottom = screen_height
                self.velocity[1] = 0.0

    def explode(self):
        if self.color == BLUE:  # Glass cube shatters
            self.is_broken = True

            # Generate smaller glass pieces
            num_pieces = random.randint(8, 12)
            piece_size = self.size // num_pieces
            for _ in range(num_pieces):
                piece_x = self.rect.x + random.randint(0, self.size - piece_size)
                piece_y = self.rect.y + random.randint(0, self.size - piece_size)
                piece = Cube(piece_x, piece_y, piece_size, BLUE, self.mass * 0.1)
                piece.velocity = np.array([random.uniform(-10, 10), random.uniform(-15, -10)])
                all_sprites.add(piece)
                cubes.add(piece)

            # Shrink the original cube
            self.size = self.size // 2
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
            self.rect = self.image.get_rect(center=self.rect.center)

        elif self.color == RED:  # Wooden cube breaks apart
            self.is_broken = True

            # Generate smaller wooden pieces
            num_pieces = random.randint(4, 8)
            piece_size = self.size // num_pieces
            for _ in range(num_pieces):
                piece_x = self.rect.x + random.randint(0, self.size - piece_size)
                piece_y = self.rect.y + random.randint(0, self.size - piece_size)
                piece = Cube(piece_x, piece_y, piece_size, RED, self.mass * 0.1)
                piece.velocity = np.array([random.uniform(-5, 5), random.uniform(-2, 2)])
                all_sprites.add(piece)
                cubes.add(piece)

            # Shrink the original cube
            self.size = self.size // 2
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
            self.rect = self.image.get_rect(center=self.rect.center)

        # Generate smaller pieces within the original cube
        num_inner_pieces = random.randint(4, 8)
        inner_piece_size = self.size // num_inner_pieces
        for _ in range(num_inner_pieces):
            inner_piece_x = self.rect.x + random.randint(0, self.size - inner_piece_size)
            inner_piece_y = self.rect.y + random.randint(0, self.size - inner_piece_size)
            inner_piece = Cube(inner_piece_x, inner_piece_y, inner_piece_size, self.color, self.mass * 0.1)
            inner_piece.velocity = np.array([random.uniform(-5, 5), random.uniform(-5, 5)])
            all_sprites.add(inner_piece)
            cubes.add(inner_piece)

# Create groups for sprites
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
cubes = pygame.sprite.Group()

# Create a wooden cube
wooden_cube = Cube(screen_width // 2 - 100, screen_height // 2, 100, RED, 1.0)
all_sprites.add(wooden_cube)
cubes.add(wooden_cube)

# Create a glass cube
glass_cube = Cube(screen_width // 2 + 100, screen_height // 2, 100, BLUE, 0.5)
all_sprites.add(glass_cube)
cubes.add(glass_cube)

# Set up the clock
clock = pygame.time.Clock()

# Game loop
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                bullet_speed += 2
            elif event.key == pygame.K_DOWN:
                bullet_speed -= 2
                if bullet_speed < 0:
                    bullet_speed = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                bullet_angle = random.uniform(-5, 5)
                bullet_shape = 0.01  # Example shape (can be adjusted)
                bullet_drag_coefficient = 0.3  # Example drag coefficient (can be adjusted)
                bullet_spin_rate = 100.0  # Example spin rate (can be adjusted)
                bullet = Bullet(*mouse_pos, bullet_angle, bullet_speed, bullet_shape, bullet_drag_coefficient, bullet_spin_rate)
                all_sprites.add(bullet)
                bullets.add(bullet)

    # Update
    air_density = 1.2  # Example air density (can be adjusted)
    wind_speed = 1.0  # Example wind speed (can be adjusted)
    wind_direction = math.radians(0)  # Example wind direction (can be adjusted)
    latitude = math.radians(0)  # Example latitude (can be adjusted)

    all_sprites.update(air_density, wind_speed, wind_direction, latitude)

    # Check for bullet-cube collision
    for bullet in bullets:
        for cube in cubes:
            if bullet.rect.colliderect(cube.rect):
                bullet_mass = bullet.mass
                bullet_velocity = np.linalg.norm(bullet.velocity)
                cube_mass = cube.mass

                # Calculate initial momentum of the bullet and the cube
                bullet_momentum = bullet_mass * bullet_velocity
                cube_momentum = cube_mass * np.linalg.norm(cube.velocity)

                # Calculate the conservation of momentum
                total_momentum = bullet_momentum + cube_momentum
                bullet_velocity_after = total_momentum / bullet_mass

                # Calculate the kinetic energy of the bullet before and after the collision
                bullet_kinetic_energy_before = 0.5 * bullet_mass * bullet_velocity**2
                bullet_kinetic_energy_after = 0.5 * bullet_mass * bullet_velocity_after**2

                # Calculate the energy absorbed by the cube
                energy_absorbed = bullet_kinetic_energy_before - bullet_kinetic_energy_after

                # Apply the velocity change to the bullet
                bullet.velocity = np.array([math.cos(bullet.angle) * bullet_velocity_after, -math.sin(bullet.angle) * bullet_velocity_after])

                cube.explode()
                bullet.kill()

                print("Bullet Mass:", bullet_mass, "kg")
                print("Bullet Velocity Before:", bullet_velocity, "m/s")
                print("Bullet Velocity After:", round(bullet_velocity_after, 2), "m/s")
                print("Cube Mass:", cube_mass, "kg")
                print("Energy Absorbed by Cube:", round(energy_absorbed, 2), "J")
                print("")

    # Draw
    screen.fill(BLACK)
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
