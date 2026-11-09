from pico2d import get_canvas_width, load_image

import game_world


class Ball:
    images = {}

    def __init__(self, x, y, velocity, image_file='ball21x21.png'):
        if image_file not in Ball.images:
            Ball.images[image_file] = load_image(image_file)
        self.image = Ball.images[image_file]
        self.x, self.y = x, y
        self.velocity = velocity

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > get_canvas_width():
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)
