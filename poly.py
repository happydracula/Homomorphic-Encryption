from polynomial import Polynomial
import math
import random


# class Polynomial():
#     def __init__(self, arr):
#         self.poly = {}
#         for i in range(len(arr)):
#             if (arr[i] != 0):
#                 self.poly[i] = arr[i]
#                 self.degree = i

#     def __add__(self, other):
#         if (isinstance(other, int)):
#             if (0 in self.poly):
#                 self.deg[0] += other
#             else:
#                 self.deg[0] = other
#             return self
#         elif (isinstance(other, Polynomial)):
#             for deg, coeff in other.poly.items():
#                 if (deg in self.poly):
#                     self.poly[deg] += coeff
#                 else:
#                     self.poly[deg] = coeff
#             return self
#         else:
#             raise Exception('Invalid Data Type')

#     def __sub__(self, other):
#         if (isinstance(other, int)):
#             if (0 in self.poly):
#                 self.deg[0] -= other
#             else:
#                 self.deg[0] = (-other)
#             return self
#         elif (isinstance(other, Polynomial)):
#             for deg, coeff in other.poly.items():
#                 if (deg in self.poly):
#                     self.poly[deg] -= coeff
#                 else:
#                     self.poly[deg] = (-coeff)
#             return self
#         else:
#             raise Exception('Invalid Data Type')

#     @staticmethod
#     def __normalize(poly):
#         while poly and poly[-1] == 0:
#             poly.pop()
#         if poly == []:
#             poly.append(0)

#     def polydiv(self, other):
#         num = num[:]
#         Polynomial.__normalize(num)
#         den = den[:]
#         Polynomial.__normalize(den)

#         if len(num) >= len(den):
#             # Shift den towards right so it's the same degree as num
#             shiftlen = len(num) - len(den)
#             den = [0] * shiftlen + den
#         else:
#             return [0], num

#         quot = []
#         divisor = float(den[-1])
#         for i in range(shiftlen + 1):
#             # Get the next coefficient of the quotient.
#             mult = num[-1] / divisor
#             quot = [mult] + quot

#             # Subtract mult * den from num, but don't bother if mult == 0
#             # Note that when i==0, mult!=0; so quot is automatically normalized.
#             if mult != 0:
#                 d = [mult * u for u in den]
#                 num = [u - v for u, v in zip(num, d)]

#             num.pop()
#             den.pop(0)

#         Polynomial.__normalize(num)
#         return quot, num

#     def __mul__(self, other):
#         if (not isinstance(other, Polynomial)):
#             for key in self.poly.keys():
#                 self.poly[key] *= other
#             return self
#         else:
#             res = Polynomial([])
#             for a in self.poly.items():
#                 for b in other.poly.items():
#                     coeff = a[1]*b[1]
#                     power = a[0]+b[0]
#                     if (power in res.poly):
#                         res.poly[power] += coeff
#                     else:
#                         res.poly[power] = coeff
#             return res

#     def __str__(self):
#         res = ''
#         for item in self.poly.items():
#             if (item[0]) == 0:
#                 res += str(item[1])+' + '
#             else:
#                 res += str(item[1])+' x^'+str(item[0])+' + '
#         return res[:-2]

a = Polynomial([2**100]*2)
b = Polynomial([2**1000]*3)
print(divmod(b, a)[1])
