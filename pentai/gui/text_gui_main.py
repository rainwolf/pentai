#!/usr/bin/python

import alpha_beta
import ab_bridge
from rules import *
from game import *
from text_gui import *
from human_player import *
from ai_player import *

""" txt_gui_main.py creates the Game, Players and contains the game turn loop """

if __name__ == "__main__":
    """
    try:
        import psyco
        psyco.full()
    except ImportError:
        log.info("(without psyco)")
    """

    rules = Rules(9, "standard")
    player1 = HumanPlayer("Bruce", P1)
    '''
    player2 = HumanPlayer("B2", P2)
    '''
    player2 = AIPlayer(2, "Deep Thunk", P2)
    game = Game(rules, player1, player2)
    player2.attach_to_game(game)

    gui = TextGui(game)

    print "Please enter moves in the form 'd4'."
    print gui.board_to_string()
    while (not game.finished()):
        print game.prompt_for_action(gui)
        try:
            action = game.get_action(gui)
            action.perform(game)
        except IllegalMoveException, e:
            print e.message
    print gui.board_to_string()
    winner = game.winner_name()
    print "Won by %s" % winner
    
