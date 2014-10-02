from kivy.uix.screenmanager import *

from pentai.gui.intro_screen import *
from pentai.gui.intro_help_screen import *
from pentai.base.defines import *
from pentai.gui.guide import *
import pentai.base.logger as log

import random

class PScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        self.demo = None
        super(PScreenManager, self).__init__(*args, **kwargs)
        self.transition = SlideTransition()
        self.random_transition()
        self.previous = []
        # self.guide = Guide() # TODO: Persistent -> misc_db

    def push_demo(self, d):
        self.previous.append(self.current)
        self.set_demo(d)

    def set_demo(self, d):
        if self.demo:
            self.demo.clean_up()
        self.demo = d 

    def push_current(self, screen_name):
        if self.current == screen_name:
            return
        log.debug("Pushing %s to %s, change to %s" % (self.current, self.previous, screen_name))
        self.previous.append(self.current)
        self.set_current(screen_name)
        if len(self.previous) > 20:
            self.previous[:1] = []

    def get_size(self):
        return self.current_screen.size

    def resize(self, *args):
        if self.current == "Pente":
            self.current_screen.resize(args[1:])

    def set_current(self, screen_name):
        if self.current != screen_name:
            self.leave()
            self.random_transition()
            self.current = screen_name
            if not self.in_demo_mode():
                self.guide.on_enter(screen_name)

    def pop_screen(self):
        log.debug("Popping to %s" % (self.previous))
        if len(self.previous) < 1:
            return False

        self.set_current(self.previous[-1])
        del self.previous[-1]
        return True

    def clear_hist(self):
        self.previous[:] = []

    def random_transition(self):
        trans = self.transition

        dirs = ['right','up','down','left']
        try:
            dirs.remove(self.last_choice)
        except: pass
        dc = random.choice(dirs)
        self.last_choice = dc
        trans.direction = dc

    def in_demo_mode(self):
        return self.demo != None

    def on_touch_down(self, *args, **kwargs):
        if self.in_demo_mode():
            self.demo.interrupt()
        else:
            return super(PScreenManager, self).on_touch_down(*args, **kwargs)
    
    def on_touch_move(self, *args, **kwargs):
        if self.in_demo_mode():
            pass
        else:
            return super(PScreenManager, self).on_touch_move(*args, **kwargs)
    
    def on_touch_up(self, *args, **kwargs):
        if self.in_demo_mode():
            pass
        else:
            return super(PScreenManager, self).on_touch_up(*args, **kwargs)

    def leave(self):
        self.guide.on_leave()
    
    def get_all_screens(self):
        import menu_screen as ms_m
        import ai_player_screen as aips_m
        import ai_help_screen as aihs_m
        import human_player_screen as hps_m
        import human_help_screen as hhs_m
        import setup_screen as sts_m
        import setup_help_screen as shs_m
        import settings_screen as ses_m
        import settings_help_screen as sehs_m
        import games_screen as gs_m
        import load_help_screen as lhs_m
        import pente_help_screen as phs_m

        screens = [(ms_m.MenuScreen, "Menu"),
                   (ses_m.SettingsScreen, "Settings"),
                   (sehs_m.SettingsHelpScreen, "SettingsHelp"),
                   (sts_m.SetupScreen, "Setup"),
                   (shs_m.SetupHelpScreen, "GameSetupHelp"),
                   (gs_m.GamesScreen, "Load"),
                   (lhs_m.LoadHelpScreen, "LoadHelp"),
                   (aips_m.AIPlayerScreen, "AI"), (aihs_m.AIHelpScreen, "AIHelp"),
                   (hps_m.HumanPlayerScreen, "Human"), (hhs_m.HumanHelpScreen, "HumanHelp"),
                   (phs_m.PenteHelpScreen, "PenteHelp"),
                   ]
        return screens
