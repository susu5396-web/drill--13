import unittest
from unittest.mock import patch
from types import SimpleNamespace

import ball as ball_module
import boy as boy_module
import grass as grass_module
import game_world
import play_mode
from ball import Ball
from sdl2 import (SDL_KEYDOWN, SDLK_0, SDLK_1, SDLK_2, SDLK_i,
                  SDLK_p, SDLK_RIGHT, SDLK_SPACE)


class FakeImage:
    def __init__(self, filename):
        self.filename = filename
        self.draw_calls = []

    def draw(self, x, y):
        self.draw_calls.append((x, y))

    def clip_draw(self, *args):
        pass

    def clip_composite_draw(self, *args):
        pass


class ItemModeTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.images = {}

        def load_image(filename):
            image = FakeImage(filename)
            self.images[filename] = image
            return image

        self.patches = [
            patch.object(play_mode, 'get_time', return_value=0.0),
            patch.object(boy_module, 'get_time', return_value=0.0),
            patch.object(boy_module, 'get_canvas_width', return_value=800),
            patch.object(play_mode, 'get_events',
                         side_effect=lambda: self.events),
            patch.object(play_mode, 'clear_canvas'),
            patch.object(play_mode, 'update_canvas'),
            patch.object(play_mode, 'load_image', side_effect=load_image),
            patch.object(boy_module, 'load_image', side_effect=load_image),
            patch.object(grass_module, 'load_image', side_effect=load_image),
            patch.object(ball_module, 'load_image', side_effect=load_image),
        ]
        for patcher in self.patches:
            patcher.start()

        Ball.images.clear()
        play_mode.init()

    def tearDown(self):
        play_mode.finish()
        for patcher in reversed(self.patches):
            patcher.stop()

    def send(self, key, event_type=SDL_KEYDOWN, repeat=0):
        self.events = [SimpleNamespace(type=event_type, key=key,
                                       repeat=repeat)]
        play_mode.handle_events()

    def balls(self):
        return [obj for layer in game_world.world for obj in layer
                if isinstance(obj, Ball)]

    def test_item_overlay_keeps_game_running_and_draws(self):
        self.send(SDLK_i)
        self.assertTrue(play_mode.item_mode)
        self.assertFalse(play_mode.paused)

        play_mode.render()
        self.assertEqual(self.images['item_select.png'].draw_calls, [(400, 300)])

        self.send(SDLK_RIGHT)
        play_mode.update()
        self.assertEqual(play_mode.boy.x, 405)

    def test_item_keys_select_expected_projectile(self):
        for key, filename, selected in (
                (SDLK_0, None, 0),
                (SDLK_1, 'ball21x21.png', 1),
                (SDLK_2, 'ball41x41.png', 2)):
            with self.subTest(key=key):
                play_mode.finish()
                play_mode.init()
                Ball.images.clear()
                self.send(SDLK_i)
                self.send(key)
                self.assertEqual(play_mode.selected_item, selected)
                self.assertEqual(play_mode.item_mode, key == SDLK_0)
                shots = self.balls()
                self.assertEqual(len(shots), 0 if filename is None else 1)
                if filename is not None:
                    self.assertEqual(shots[0].image.filename, filename)

    def test_zero_selection_persists_until_item_is_selected(self):
        self.send(SDLK_i)
        self.send(SDLK_0)
        self.assertTrue(play_mode.item_mode)
        self.assertEqual(play_mode.selected_item, 0)

        self.send(SDLK_2)
        self.assertEqual(play_mode.selected_item, 2)
        self.assertEqual(len(self.balls()), 1)

    def test_pause_and_space_fire_remain_available(self):
        self.send(SDLK_SPACE)
        self.assertEqual(len(self.balls()), 1)
        self.assertEqual(self.balls()[0].image.filename, 'ball21x21.png')

        self.send(SDLK_p)
        self.assertTrue(play_mode.paused)
        x = play_mode.boy.x
        play_mode.update()
        self.assertEqual(play_mode.boy.x, x)

        self.send(SDLK_p)
        self.assertFalse(play_mode.paused)

    def test_finish_resets_item_state(self):
        self.send(SDLK_i)
        play_mode.selected_item = 2
        play_mode.finish()

        self.assertFalse(play_mode.item_mode)
        self.assertEqual(play_mode.selected_item, 0)
        self.assertIsNone(play_mode.item_select_image)


if __name__ == '__main__':
    unittest.main()
