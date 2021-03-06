
from kivy.clock import Clock

import time
import audio as a_m
from pentai.base.defines import *
import pentai.base.logger as log

class GuiClock(object):
    def __init__(self, colour, widget, game):
        self.colour = colour
        self.player = game.get_player(colour)
        self.widget = widget
        self.game = game
        self.total_time_s = game.get_total_time_s()
        self.show_remaining()
        self.ticking = False
        self.last_tick_time = None

    def start_ticking(self):
        log.debug("start_ticking %s" % id(self))
        if not self.ticking:
            self.tick_audio(0, self.colour)
            self.tick_video(0)
            self.ticking = True

    def stop_ticking(self):
        # Stop both timers
        log.debug("stop_ticking %s" % id(self))
        Clock.unschedule(self.tick_audio)
        Clock.unschedule(self.tick_video)
        self.ticking = False
        self.last_tick_time = None

    def made_move(self):
        if self.last_tick_time:
            elapsed = time.time() - self.last_tick_time 
            # In case of leap seconds, time changes etc.
            if elapsed > 0:
                self.game.tick(self.colour, elapsed)
        self.stop_ticking()

    def tick_audio(self, dt, colour=None):
        if colour is None:
            colour = self.last_colour
        else:
            self.last_colour = colour
        if dt > 0:
            # Make tick sound
            a_m.instance.tick(colour)

        # tt should be in seconds
        tt = self.total_time_s

        # Remaining seconds
        rem = self.game.remaining_time(self.colour)

        if rem > 0:
            interval = (.5 * (1 + (rem / tt))) ** 2
            Clock.schedule_once(self.tick_audio, interval)

    def tick_video(self, dt):
        rem = self.game.tick(self.colour, dt)
        next_tick_diff = rem % 1.0

        self.last_tick_time = time.time()

        self.show_remaining()

        if rem > 0:
            Clock.schedule_once(self.tick_video, next_tick_diff)
        else:
            other_colour = opposite_colour(self.game.to_move_colour())

    def refresh(self):
        self.show_remaining()

    def show_remaining(self):
        rem = round(self.game.remaining_time(self.colour))
        self.widget.text = "%2d:%02d" % (rem/60, rem%60)
