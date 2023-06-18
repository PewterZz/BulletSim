from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from physics3d import *
from panda3d.bullet import BulletWorld, BulletSphereShape

app = Ursina()
world = BulletWorld()
world.setGravity(Vec3(0, -100, 0))
Sky()
Debugger(world, wireframe=True)

cube = Entity(model='cube', position=(0, 1, 0), visible=False)
BoxCollider(world, cube, mass=1)
ground = Entity(model='plane', texture='grass', collider='mesh', scale=(100, 0, 100), visible= False)
BoxCollider(world, ground)

projectiles = []

def input(key):
    if key == 'left mouse down':
        shoot()

def shoot():
    sphere = Entity(model='sphere', position=(0, 5, 0), scale=0.1, visible=False)
    SphereCollider(world, sphere, mass=1)
    projectile = {
        'entity': sphere,
    }
    projectiles.append(projectile)

def update():
    dt = time.dt
    world.doPhysics(dt)
    camera_control()

    for projectile in projectiles:
        projectile['entity'].position


def camera_control():
    camera.z += held_keys['w'] * 10 * time.dt
    camera.z -= held_keys['s'] * 10 * time.dt
    camera.x += held_keys['d'] * 10 * time.dt
    camera.x -= held_keys['a'] * 10 * time.dt
    camera.y += held_keys['e'] * 10 * time.dt
    camera.y -= held_keys['q'] * 10 * time.dt

app.run()
