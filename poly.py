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
                self.poly[0] += coeff
                if (self.poly[deg] == 0):
                    del self.poly[deg]
            else:
                self.poly[0] = coeff
            return self

    def __sub__(self, other):
        if (isinstance(other, Polynomial)):
            for deg in other.poly:

                coeff = other.poly(deg)
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
                self.poly[0] -= coeff
                if (self.poly[deg] == 0):
                    del self.poly[deg]
            else:
                self.poly[0] = -coeff
            return self

    def __mod__(self, other):
        if (isinstance(other, Polynomial)):
            while (self.degree >= other.degree):
                mult = self.poly[self.degree]
                self.poly[self.degree-other.degree] -= mult
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

    def __str__(self):
        res = ''
        for key in sorted(self.poly):
            if (key) == 0:
                res += str(self.poly[key])+' + '
            else:
                res += str(self.poly[key])+' x^'+str(key)+' + '
        return res[:-2]


N = 8000
a = [1, 2, 0, 1]
b = [1, 0, 1]

a = Polynomial(a)
b = Polynomial(b)

print(a % 2)
