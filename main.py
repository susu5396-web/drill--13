import game_framework
from pico2d import *
import logo_mode
import play_mode


open_canvas()
game_framework.run(play_mode)#테스트 리드타임을 기다리기위해 테스트할때는 바로 넘겨버림
close_canvas()
