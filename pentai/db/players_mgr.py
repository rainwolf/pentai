import pentai.ai.ai_genome as aig_m
import ai_factory
import misc_db as m_m
import mru_cache as mru_m

from pentai.base.defines import *
import pentai.base.logger as log
import zodb_dict as z_m

import os

def misc():
    return m_m.get_instance()

# TODO: Move these into player classes
HUMAN_TYPE = 0
AI_TYPE = 1

def player_type_to_int(pt):
    pt = pt.lower()
    if pt == "human":
        return HUMAN_TYPE
    if pt == "ai" or pt == "computer":
        return AI_TYPE

class PlayersMgr():
    # TODO: Borg pattern?
    def __init__(self, *args, **kwargs):
        self.factory = ai_factory.AIFactory()
        section = "players"
        self.players_by_p_key = z_m.get_section(section)
        section = "p_keys_by_name"
        self.p_keys_by_name = z_m.get_section(section)
        if not self.p_keys_by_name.has_key(HUMAN_TYPE):
            self.p_keys_by_name[HUMAN_TYPE] = z_m.ZM()
            self.p_keys_by_name[AI_TYPE] = z_m.ZM()

    def ensure_has_key(self, player):
        assert not player is None
        if not hasattr(player, "p_key") or player.p_key is None:
            p_key = self.next_id()
            player.p_key = p_key

        return player.p_key

    def get_rpks(self, player_type):
        if player_type == "AI" or player_type == "Computer": # Computer is temp
            key = "recent_ai_player_ids"
        else:
            key = "recent_human_ids"
        rpks = misc().setdefault(key, mru_m.MRUCache(30))
        return rpks

    def mark_recent_player(self, player):
        #log.debug("in mark_recent_player")
        try:
            p_key = player.get_key()
        except AttributeError:
            p_key = player

        player = self.convert_to_player(p_key)
        p_type = player.get_type()
        rpks = self.get_rpks(p_type)
        rpks.add(p_key)
        z_m.sync()

    def get_recent_player_names(self, player_type, number):
        # TODO: use "number" for # returned players
        rps = self.get_recent_players(player_type, number)
        rpns = []
        seen = set()
        for rp in rps:
            rpn = rp.get_name()
            if not rpn in seen:
                rpns.append(rpn)
                seen.add(rpn)
        return rpns

    def get_ai_player_names(self):
        return self.get_recent_player_names("AI", 30)

    def get_human_player_names(self):
        return self.get_recent_player_names("Human", 30)

    def get_recent_players(self, player_type, number):
        rpks = self.get_rpks(player_type).top(number)
        rps = []
        for rp in rpks:
            p = self.convert_to_player(rp)

            if p:
                rps.append(p)
        return rps

    def remove(self, pid):
        try:
            player = self.players_by_p_key[pid]
        except KeyError:
            return

        player_type = player.get_type()
        pti = player_type_to_int(player_type)
        player_name = player.get_name()
        del self.players_by_p_key[pid]

        pkbn = self.p_keys_by_name[pti]
        del pkbn[player_name]

        rpks = self.get_rpks(player_type)
        rpks.delete(pid)

    def save(self, player, update_cache=True):
        if player.__class__ is type(0):
            player = self.find(player)

        p_key = self.ensure_has_key(player)

        try:
            player = player.genome
            # update the genome as well
            player.set_override(True)
            player.p_key = p_key
            player.set_override(False)
        except AttributeError:
            # We're already dealing with a genome
            pass

        self.players_by_p_key[p_key] = player

        player_type = player.get_type()
        player_name = player.get_name()

        pti = player_type_to_int(player_type)
        pbkn = self.p_keys_by_name[pti]
        pbkn[player_name] = p_key

        if update_cache:
            self.mark_recent_player(p_key)
        z_m.sync()

    def find_by_name(self, name, player_type=None, update_cache=True):
        genome = self.find_genome_by_name(name, player_type, update_cache)
        if genome:
            return self.convert_to_player(genome)

    def find_genome_by_name(self, name, player_type=None, update_cache=True):
        if player_type:
            return self.find_genome_by_name_inner(name, player_type, update_cache)

        for pt in ("Human", "AI"):
            gbn = self.find_genome_by_name_inner(name, pt, update_cache)
            if gbn:
                return gbn

    def find_genome_by_name_inner(self, name, player_type, update_cache=True):
        try:
            pti = player_type_to_int(player_type)
            pkbn = self.p_keys_by_name[pti]
            p_key = pkbn[name]
            return self.players_by_p_key[p_key]    

        except KeyError:
            return None

    def find(self, p_key, update_cache=True):
        try:
            p = self.players_by_p_key[p_key]
        except KeyError:
            return None
        if update_cache:
            self.mark_recent_player(p_key)
        return self.convert_to_player(p)

    def get_player_name(self, p_key):
        try:
            p = self.players_by_p_key[p_key]
        except KeyError:
            return None
        return p.get_name()

    def convert_to_player(self, player):
        if type(player) == type(0):
            try:
                player = self.players_by_p_key[player]
            except KeyError:
                return None

        if player.__class__ is aig_m.AIGenome:
            player = self.factory.create_player(player)
        else:
            # HumanPlayers are stored directly
            pass
        return player

    def get_max_id(self):
        return misc().setdefault("max_id", 0)

    def next_id(self):
        curr_id = self.get_max_id() + 1
        misc()["max_id"] = curr_id
        z_m.sync()
        return curr_id

