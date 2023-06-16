import pygame
import pygame.draw
import pygame.opengl

def gun_bullet_simulation():
    # Initialize Pygame and OpenGL
    pygame.init()
    pygame.display.set_mode((640, 480))
    pygame.opengl.init()

    # Create a gun and a bullet
    gun = pygame.Rect((100, 100), (50, 50))
    bullet = pygame.Rect((100, 150), (10, 10))

    # Create a loop to simulate the gun firing and the bullet flying
    while True:
        # Update the gun and bullet positions
        gun.x += 10
        bullet.y += 10

        # Draw the gun and bullet
        pygame.draw.rect(screen, (0, 0, 0), gun)
        pygame.draw.rect(screen, (255, 0, 0), bullet)

        # Check for collisions
        if bullet.y > 480:
            break

        # Update the display
        pygame.display.update()

# Run the gun bullet simulation
gun_bullet_simulation()