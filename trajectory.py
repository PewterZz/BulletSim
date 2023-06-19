import math
import matplotlib.pyplot as plt

# Constants
G = 9.81  # Acceleration due to gravity (m/s^2)
RHO = 1.225  # Air density (kg/m^3)
C_D = 0.5  # Drag coefficient
A = math.pi * (0.01 ** 2)  # Cross-sectional area of the bullet (m^2)
MASS = 0.01  # Mass of the bullet (kg)
INITIAL_VELOCITY = 100  # Initial velocity of the bullet (m/s)
LAUNCH_ANGLE = math.radians(45)  # Launch angle of the bullet (radians)
TIME_STEP = 0.01  # Time step for numerical integration (s)

# Lists to store the trajectory data
time_values = []
x_values = []
y_values = []

# Initial conditions
time = 0
x = 0
y = 0
vx = INITIAL_VELOCITY * math.cos(LAUNCH_ANGLE)
vy = INITIAL_VELOCITY * math.sin(LAUNCH_ANGLE)

# Numerical integration loop
while y >= 0:
    time_values.append(time)
    x_values.append(x)
    y_values.append(y)

    # Calculate the acceleration components
    ax = -((0.5 * RHO * C_D * A * vx ** 2) / MASS)
    ay = -G - ((0.5 * RHO * C_D * A * vy ** 2) / MASS)

    # Update the velocity components
    vx += ax * TIME_STEP
    vy += ay * TIME_STEP

    # Update the position components
    x += vx * TIME_STEP
    y += vy * TIME_STEP

    # Update time
    time += TIME_STEP

# Plot the trajectory
plt.plot(x_values, y_values)
plt.xlabel('Horizontal distance (m)')
plt.ylabel('Vertical distance (m)')
plt.title('Bullet Trajectory')
plt.grid(True)
plt.show()
