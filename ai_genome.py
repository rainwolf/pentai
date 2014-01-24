
class AIGenomeException(Exception):
    pass

class AIGenome(object):
    def __init__(self, name):
        defaults = {
            "name": name,
            "key": None,
            "use_openings_book": True,
            # Search params
            "max_depth": 6,
            "max_depth_boost": 0,
            "mmpdl": 9,
            "narrowing": 0,
            "chokes": [(4,5)],
            "filter2": False,
            # Utility function
            "calc_mode": 1,
            "capture_score_base": 300,
            "take_score_base": 100,
            "threat_score_base": 20,
            "use_net_captures": True,
            "captures_scale": [1, 1, 1, 1, 1, 1],
            "length_factor": 27,
            "move_factor": 30,
            "blindness": 0,
            "scale_pob": False,
        }
        super(AIGenome, self).__setattr__("__dict__", defaults)

    def __setattr__(self, attr_name, val):
        if not hasattr(self, attr_name):
            raise AIGenomeException("Cannot set attribute %s" % attr_name)
        super(AIGenome, self).__setattr__(attr_name, val)

