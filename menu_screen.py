from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

import webbrowser

from scrollable_label import *

class MenuScreen(Screen):
    """ This is more of a travel agency or a directory than a menu """
    about_text = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(MenuScreen, self).__init__(*args, **kwargs)
        self.ids.about_id.ids.label_id.bind(on_ref_press=self.follow_link)
        self.about_text = \
"""PentAI by Bruce Cropley\n
Pente is a strategy board game for two or more players, created in 1977 by Gary Gabrel. It is now owned by Hasbro, and the board game can be bought from [ref=ww][color=00ffff]Winning Ways[/color][/ref]. Or not...
The rules of the game are very simple: The first player to get 5 stones in a straight line wins. Pairs of stones can be captured by placing a stone at each end of the pair. Capturing 5 pairs first also wins. Click "Demo" below!

PentAI is a computer program to play Pente. It can be configured to play in a wide range of ability levels, from a complete beginner to a strong amateur player. For more information about how PentAI works, see my [ref=bc][color=00ffff]website[/color][/ref].

If you get a sore brain, you can create a game between a couple of Artificial Intelligence (AI) players and watch what they do. Human versus Human games are also possible, though you are much better off playing with a real set.

Games are automatically saved, and can be resumed if they were left unfinished.

There are a few settings that you might like to change, for things such as move confirmation style, sound volume and so on.

Thanks go to:

- Alan Morris for the wonderful voiceover
- Mark Cole for playing many games against "Deep Thunk"
- Marion and Noel Lodge for their constant support and feedback
- Thad for his expert Pente insights
- Annette Campbell for inspiring me to write this in the first place
- Sascha and Jespah for their comments on "The Sod"
- Lots of other people for their support and feedback

Enjoy,
Bruce












"""
    def follow_link(self, inst, ref):
        print "User clicked on: %s" % ref
        if ref == "ww":
            link = "http://winning-moves.com/product/Pente.asp"
        elif ref == "bc":
            link = "http://www.bruce-cropley.com/pente"
        print link
        #webbrowser.open_new_tab(link)

