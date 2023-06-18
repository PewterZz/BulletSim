from vpython import *
scene = canvas(title='Gunfire Simulation', width=800, height=600, center=vector(0, 0, 0), background=color.white)
ground = box(pos=vector(0, -0.1, 0), size=vector(20, 0.1, 20), color=color.green)
bullet = sphere(pos=vector(-9, 1, 0), radius=0.2, color=color.red, make_trail = True)
target = box(pos=vector(9, 1, 0), size=vector(0.2, 2, 2), color=color.blue)

bullet_mass = 0.01 
bullet_velocity = 500  
target_mass = 10  

bullet_kinetic_energy = 0.5 * bullet_mass * bullet_velocity**2

energy_label = label(pos=vector(0, 5, 0), text='Kinetic Energy: {} J'.format(bullet_kinetic_energy), height=15, box=False)

t = 0 
dt = 0.01  

scene.autoscale = False  
running = True
while running:
    ev = scene.waitfor('mousedown mouseup')
    if ev.event == 'mousedown':
        while bullet.pos.x < target.pos.x:
            rate(1000)  

            bullet.pos.x += bullet_velocity * dt

            t += dt

            if bullet.pos.x >= target.pos.x:
                final_velocity = 0 
                final_kinetic_energy = 0.5 * bullet_mass * final_velocity**2

                energy_change = bullet_kinetic_energy - final_kinetic_energy

                energy_label.text = 'Kinetic Energy: {} J'.format(final_kinetic_energy)

                print('Bullet impact!')
                print('Final Kinetic Energy: {} J'.format(final_kinetic_energy))
                print('Energy transferred to the target: {} J'.format(energy_change))

                running = False
                break
