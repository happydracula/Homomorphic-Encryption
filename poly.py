import math
import random


class Polynomial():
    def __init__(self, arr):
        self.poly = {}
        self.degree = 0
        for i in range(len(arr)):
            if (arr[i] != 0):
                self.poly[i] = arr[i]
                self.degree = i

    def __add__(self, other):
        if (isinstance(other, Polynomial)):
            for deg in other.poly:
                coeff = other.poly[deg]
                if (deg in self.poly):
                    self.poly[deg] += coeff
                    if (self.poly[deg] == 0):
                        del self.poly[deg]
                else:
                    if deg > self.degree:
                        self.degree = deg
                    self.poly[deg] = coeff
            return self
        else:
            if (0 in self.poly):
                self.poly[0] += other
                if (self.poly[0] == 0):
                    del self.poly[0]
            else:
                self.poly[0] = other
            return self

    def __sub__(self, other):
        if (isinstance(other, Polynomial)):
            for deg in other.poly:

                coeff = other.poly[deg]
                if (deg in self.poly):
                    self.poly[deg] -= coeff
                    if (self.poly[deg] == 0):
                        del self.poly[deg]
                else:
                    if deg > self.degree:
                        self.degree = deg
                    self.poly[deg] = - coeff
            return self
        else:
            if (0 in self.poly):
                self.poly[0] -= other
                if (self.poly[0] == 0):
                    del self.poly[0]
            else:
                self.poly[0] = -other
            return self

    def __getitem__(self, key):
        return self.poly[key]

    def __mod__(self, other):
        if (isinstance(other, Polynomial)):
            while (self.degree >= other.degree):
                mult = self.poly[self.degree]
                if (self.degree-other.degree in self.poly):
                    self.poly[self.degree-other.degree] -= mult
                    if (self.poly[self.degree-other.degree] == 0):
                        del self.poly[self.degree-other.degree]
                else:
                    self.poly[self.degree-other.degree] = -mult

                del self.poly[self.degree]
                i = self.degree-1
                while i not in self.poly:
                    i -= 1
                self.degree = i
            return self
        else:
            for key in self.poly:
                self.poly[key] %= other
            return self

    def __floordiv__(self, other):
        if not isinstance(other, int):
            raise Exception('Invalid Type')
        else:
            res = Polynomial([])
            for key in self.poly:
                res.poly[key] = (self.poly[key] // other)
            return res

    def __truediv__(self, other):
        if not isinstance(other, int):
            raise Exception('Invalid Type')
        else:
            for key in self.poly:
                self.poly[key] = (self.poly[key] / other)
            return self

    def __neg__(self):
        for key in self.poly:
            self.poly[key] = -self.poly[key]
        return self

    def __mul__(self, other):
        if (not isinstance(other, Polynomial)):
            for key in self.poly:
                self.poly[key] *= other
            return self
        else:
            res = Polynomial([])
            for a in self.poly:
                for b in other.poly:
                    coeff = self.poly[a]*other.poly[b]
                    power = a+b
                    if (power in res.poly):
                        res.poly[power] += coeff
                    else:
                        res.degree = max(res.degree, power)
                        res.poly[power] = coeff
            return res

    def __rmul__(self, other):
        return self*other

    def __radd__(self, other):
        return self+other

    def poly_floor(self):
        for key in self.poly:
            self.poly[key] = int(math.floor(self.poly[key]))
        return self

    def poly_round(self):
        for key in self.poly:
            self.poly[key] = int(round(self.poly[key]))
        return self

    def __str__(self):
        res = ''
        for key in sorted(self.poly):
            if (key) == 0:
                res += str(self.poly[key])+' + '
            else:
                res += str(self.poly[key])+' x^'+str(key)+' + '
        return res[:-2]
