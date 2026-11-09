from pico2d import *
from sdl2 import (SDL_KEYDOWN, SDLK_0, SDLK_1, SDLK_2, SDLK_i)
import game_framework
import game_world
from boy import Boy
from grass import Grass

paused = False
pause_started_at = 0.0
released_keys = []
item_mode = False
selected_item = 0
item_select_image = None


def toggle_pause():
    global paused, pause_started_at

    if not paused:
        paused = True
        pause_started_at = get_time()
        released_keys.clear()
    else:
        # Exclude paused time from the character's idle timer.
        boy.idle_started_at += get_time() - pause_started_at
        paused = False
        # Apply releases received while paused to avoid stuck movement.
        for event in released_keys:
            boy.handle_event(event)
        released_keys.clear()


def handle_events():
    global item_mode, selected_item

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.pop_mode()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', 0):
                toggle_pause()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            if not getattr(event, 'repeat', 0):
                item_mode = not item_mode
        elif (item_mode and event.type == SDL_KEYDOWN and
              event.key in (SDLK_0, SDLK_1, SDLK_2)):
            if not getattr(event, 'repeat', 0):
                if event.key == SDLK_0:
                    selected_item = 0
                elif event.key == SDLK_1:
                    selected_item = 1
                    boy.fire_ball()
            continue
        elif paused:
            if event.type == SDL_KEYUP:
                released_keys.append(event)
        else:
            boy.handle_event(event)



def init(): #초기화
    global boy, paused, pause_started_at
    global item_mode, selected_item, item_select_image

    paused = False
    pause_started_at = 0.0
    item_mode = False
    selected_item = 0
    item_select_image = load_image('item_select.png')
    released_keys.clear()

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)



def update():
    if paused:
        return
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    if item_mode:
        item_select_image.draw(400, 300)
    update_canvas()

def finish():
    game_world.clear()
    released_keys.clear()
