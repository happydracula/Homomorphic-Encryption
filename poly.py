import math
import random


class Polynomial():
    def __init__(self, arr):

        self.poly = {}

        for i in range(len(arr)):
            if (arr[i] != 0):
                self.poly[i] = arr[i]

    def __add__(self, other):

        res = Polynomial([])
        del_list = []
        if (isinstance(other, Polynomial)):
            for deg in other.poly:
                coeff = other.poly[deg]
                if (deg in self.poly):
                    self.poly[deg] += coeff
                    if (self.poly[deg] == 0):
                        del_list.append(deg)
                else:
                    self.poly[deg] = coeff
            for del_key in del_list:
                del self.poly[del_key]
            return self

        else:
            if (0 in self.poly):
                self.poly[0] += other
                if (self.poly[0] == 0):
                    del self.poly[0]
            else:
                self.poly[0] = other
            return self

    def convert_to_list(self):
        res = []
        next_deg = 0
        temp = sorted(self.poly.keys())
        i = 0
        while i < len(temp):
            if (temp[i] == next_deg):
                res.append(self.poly[next_deg])
                i += 1
            else:
                res.append(0)
            next_deg += 1
        return res

    def __sub__(self, other):
        if (isinstance(other, Polynomial)):
            del_list = []
            for deg in other.poly:
                coeff = other.poly[deg]
                if (deg in self.poly):
                    self.poly[deg] -= coeff
                    if (self.poly[deg] == 0):
                        del_list.append(deg)
                else:
                    self.poly[deg] = - coeff
            for key in del_list:
                del self.poly[key]
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
            self.degree = 0
            for key in self.poly:
                if key > self.degree:
                    self.degree = key
            other.degree = 0
            for key in other.poly:
                if key > other.degree:
                    other.degree = key
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
            del_list = []
            for key in self.poly:
                self.poly[key] %= other
                if (self.poly[key] == 0):
                    del_list.append(key)
            for key in del_list:
                del self.poly[key]
            return self

    def __floordiv__(self, other):
        if not isinstance(other, int):
            raise Exception('Invalid Type')
        else:
            res = Polynomial([])
            for key in self.poly:
                t = (self.poly[key] // other)
                if (t != 0):
                    res.poly[key] = t

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
            res = Polynomial([])
            if other == 0:
                return res
            for key in self.poly:
                res.poly[key] = self.poly[key] * other

            return res
        else:
            res = Polynomial([])
            for a in self.poly:
                for b in other.poly:
                    coeff = self.poly[a]*other.poly[b]
                    power = a+b
                    if (power in res.poly):
                        res.poly[power] += coeff
                    else:
                        res.poly[power] = coeff
            return res

    def __rmul__(self, other):
        return self*other

    def __radd__(self, other):
        return self+other

    def poly_floor(self):
        del_list = []
        for key in self.poly:
            t = int(math.floor(self.poly[key]))
            if (t != 0):
                self.poly[key] = t
            else:
                del_list.append(key)
        for key in del_list:
            del self.poly[key]
        return self

    def poly_round(self):
        del_list = []
        for key in self.poly:
            t = int(round(self.poly[key]))
            if (t != 0):
                self.poly[key] = t
            else:
                del_list.append(key)
        for key in del_list:
            del self.poly[key]
        return self

    def __str__(self):
        res = ''
        for key in sorted(self.poly):
            if (key) == 0:
                res += str(self.poly[key])+' + '
            else:
                res += str(self.poly[key])+' x^'+str(key)+' + '
        return res[:-2]
