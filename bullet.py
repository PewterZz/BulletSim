class Bullet:
    def __init__(self, bullet_id, curve_direction):
        self.bullet_id = bullet_id
        self.curve_direction = curve_direction
        self.creation_time = time.time()

    def get_id(self):
        return self.bullet_id
