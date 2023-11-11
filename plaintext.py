import copy


class Plaintext:
    def __init__(self, poly, scale):
        self.poly = poly
        self.scale = scale

    def __neg__(self):
        res = copy.deepcopy(self)
        res.poly = -self.poly
        return res
