'''
Pictures demo
=============

This is a basic picture viewer, using the scatter widget.
'''

import kivy
import pdb
kivy.require('1.0.6')

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
# FIXME this shouldn't be necessary
from kivy.core.window import Window
from kivy.config import Config
from kivy.logger import LoggerHistory


class Picture(Scatter):
    '''Picture is the class that will show the image with a white border and a
    shadow. They are nothing here because almost everything is inside the
    picture.kv. Check the rule named <Picture> inside the file, and you'll see
    how the Picture() is really constructed and used.

    The source property will be the filename to show.
    '''

    source = StringProperty(None)


class PicturesApp(App):

    def build(self):

        # the root is created in pictures.kv
        root = self.root

        # get any files into images directory
        curdir = dirname(__file__)
        pics = {}
        for filename in ("./images/board.png","./images/black.png"): # glob(join(curdir, 'images', '*')):
            try:
                # load the image
                picture = Picture(source=filename) #, rotation=randint(-30,30))
                fs = filename[:].strip()
                pics[fs] = picture
                print "FILENAME: '", fs, "'"

                # add to the main field
                root.add_widget(picture)
            except Exception, e:
                Logger.exception('Pictures: Unable to load <%s>' % fs)
        """
        try:
            fn = " ./images/board.png "
            root.add_widget(pics[fn])
            fn = " ./images/black.png "
            root.add_widget(pics[fn])
        except Exception, e:
            Logger.exception(e.message)
            Logger.exception('Pictures: Unable to add <%s> to root', fn)
        """


    def on_pause(self):
        return True


if __name__ == '__main__':
    Config.set('kivy', 'log_level', 'info')
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_dir', 'logs')
    Config.set('kivy', 'log_name', 'kivy_%y-%m-%d_%_.txt')
    Logger.info('Before run')
    print(LoggerHistory.history)
    print "HELLO?"
    PicturesApp().run()
    Logger.info('After run')
    print(LoggerHistory.history)

