import os

from pentai.base.defines import *
from pentai.base.pente_exceptions import *
import pentai.base.game as g_m
import pentai.db.zodb_dict as z_m
import pentai.ai.standardise as st_m
import pentai.db.preserved_game as pg_m

ZM = z_m.ZM
ZL = z_m.ZL

instance = None

OPENINGS_DEPTH = 8

class OpeningsBook(object):
    def __init__(self, games_mgr):
        self.games_mgr = games_mgr
        self.positions_dbs = z_m.get_section("openings")

        global instance
        instance = self

    def get_filename(self, g):
        return "move%s" % g.get_move_number()

    def get_db(self, g):
        if g is None:
            return None
        fn = self.get_filename(g)
        try:
            f = self.positions_dbs[fn]
        except KeyError:
            f = self.positions_dbs[fn] = z_m.get_section(fn)
        return f

    def add_game(self, g, update_cache=True, sync=True):
        # Save the game first, before it is manipulated
        self.games_mgr.save(g, update_cache=update_cache)

        # Copy the game instance as this process munges the game.
        pm = self.games_mgr.players_mgr
        g = pg_m.PreservedGame(g).restore(pm)

        if not g.finished():
            # Only add finished games to the openings book
            return

        # Set the game as unfinished to game_state from raising exceptions
        # when we try to replay the game?! (TODO: Why is this special?)
        g.current_state._won_by = EMPTY

        max_moves = min(OPENINGS_DEPTH, len(g.move_history))
        for mn in range(1, 1+max_moves):
            # TODO: Limit the number of moves into the game.
            self.add_position(g, mn)
        if sync:
            z_m.sync()

    def add_position(self, game, move_number, sync=False):
        game.go_to_move(move_number)

        std_state, fwd, rev = st_m.standardise(game.current_state)
        position_key = std_state

        # Get the appropriate section for positions of this rule type and size
        db = self.get_db(game)
        print "Placing in %s" % (position_key,)
        pos_slot = db.setdefault(position_key, ZM())
        next_move = game.move_history[move_number-1]
        standardised_move = fwd(*next_move)
        if standardised_move[0] < 0 or standardised_move[1] < 0:
            # Off the board - it's probably one of those suicide moves
            # to finish the game sooner
            return
        arr = pos_slot.setdefault(standardised_move, ZL())
        if move_number == 1:
            # Should only be in there once per id
            if game.game_id in arr:
                raise OpeningsBookDuplicateException()
        arr.append(game.game_id)

        if sync:
            self.games_mgr.save(game)
            z_m.sync()
        return db

    def safe_move(self, pos, candidate_game, our_game):
        x, y = pos

        if candidate_game.get_size() <= our_game.size():
            return True

        safe_min_size = 4
        safe_max_size = our_game.size() - 5

        # Suggested move may be too near an edge
        return (x >= safe_min_size and y >= safe_min_size and \
                x <= safe_max_size and y <= safe_max_size)

    def get_move_games(self, game):
        std_state, fwd, rev = st_m.standardise(game.current_state)
        #print "Get: %s" % (std_state,)

        position_key = std_state

        db = self.get_db(game)

        options = {}
        try:
            print "looking in %s" % (position_key,)
            pos_slot = db[position_key]
            safe_min_size = 5
            safe_max_size = game.size() - 5

            option_count = 0

            for pos, gids in pos_slot.iteritems():
                move = rev(*pos)

                games = []

                # Convert the game_ids to games
                for gid in gids:
                    g = self.games_mgr.get_preserved_game(gid, update_cache=False)
                    if g:
                        if not self.safe_move(move, g, game):
                            # Suggested move is too near an edge
                            continue

                        # options.setdefault((x,y),[]).append(g)
                        games.append(g)
                        if len(games) > 10:
                            # That'll do
                            break

                if len(games):
                    yield move, games
                    option_count += 1
                    if option_count > 6:
                        print "Enough options"
                        return

        except KeyError, e:
            #print "KeyError: %s" % e.message
            return

    def after_game_won(self, game, colour):
        # Add the game to the openings library if req.
        # (i.e. we're subscribed)
        self.add_game(game)

