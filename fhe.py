import numpy as np
from math import floor, log
from random import choice
import utils
import math
from polynomial import Polynomial
# Params Set 1
# N = 4096
# RT = 2
# T = 1024
# Q = 2**63
# POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])

# Params Set 2
N = 1024
RT = 2
T = 1024
Q = 2**63
POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])


class FV12:

    def generate_keys(self):
        sk = utils.binary_poly(N)
        a = utils.integer_poly(N, Q)
        e = utils.normal_poly(N)
        pk0 = utils.mod(-(a*sk) + e, Q, POLY_MOD)
        pk1 = a
        d = floor(log(Q, RT))
        rlks = []
        for i in range(d + 1):
            a = utils.integer_poly(N, Q)
            e = utils.normal_poly(N)
            rlk0 = utils.mod(-(a*sk) + e + ((RT**i) * (sk**2)), Q, POLY_MOD)
            rlk1 = a
            rlks.append((rlk0, rlk1))
        return PublicKey(pk0, pk1, rlks), PrivateKey(sk)


class PublicKey:
    def __init__(self, pk0, pk1, rlks):
        self.pk0 = pk0
        self.pk1 = pk1
        self.rlks = rlks

    def encrypt(self, pt):
        delta = Q // T
        u = utils.binary_poly(N)
        e1 = utils.normal_poly(N)
        e2 = utils.normal_poly(N)

        c0 = utils.mod((self.pk0 * u) + e1 + (delta * pt), Q, POLY_MOD)
        c1 = utils.mod((self.pk1 * u) + e2, Q, POLY_MOD)

        return CipherText(c0, c1, self.pk0, self.pk1, self.rlks)


class PrivateKey:
    def __init__(self, sk):
        self.sk = sk

    def decrypt(self, ciphertext):
        scale = T / Q
        temp = utils.mod(ciphertext.ct0 + ciphertext.ct1 *
                         self.sk, Q, POLY_MOD)[0]

        pt = int((round(scale * temp) % T))
        return pt


class CipherText:

    def __init__(self, ct0, ct1, pk0, pk1, rlks):
        self.ct0 = ct0
        self.ct1 = ct1
        self.pk0 = pk0
        self.pk1 = pk1
        self.rlks = rlks

    def __base_decompose(self, polynomial):
        # To fetch the power of T used and create an array of

        d = floor(log(Q, RT))

        result = []
        for i in range(d + 1):
            poly = utils.poly_floor(polynomial // (RT ** i))
            result.append(Polynomial(
                [(int(term[0] % RT), int(term[1])) for term in poly.terms], from_monomials=True))
        return result

    def __plain_add(self, pt):

        delta = Q // T
        m = delta * pt    # scaled_pt
        res0 = utils.mod((self.ct0 + m), Q, POLY_MOD)
        return CipherText(res0, self.ct1, self.pk0, self.pk1, self.rlks)

    def __plain_multiply(self, pt):

        res0 = utils.mod((self.ct0 * pt), Q, POLY_MOD)
        res1 = utils.mod((self.ct1 * pt), Q, POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks)

    def __plain_divide(self, pt):
        res0 = utils.mod((self.ct0 * utils.modInverse(pt, T)), Q, POLY_MOD)
        res1 = utils.mod((self.ct1 * utils.modInverse(pt, T)), Q, POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks)

    def __cipher_add(self, ciphertext):

        res0 = utils.mod(self.ct0 + ciphertext.ct0, Q, POLY_MOD)
        res1 = utils.mod(self.ct1 + ciphertext.ct1, Q, POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks)

    def __cipher_sub(self, ciphertext):

        res0 = utils.mod(self.ct0 - ciphertext.ct0, Q, POLY_MOD)
        res1 = utils.mod(self.ct1 - ciphertext.ct1, Q, POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks)

    def __cipher_multiply(self, ciphertext):

        d = floor(log(Q, RT))
        scale = T / Q
        temp = self.ct0 * ciphertext.ct0
        res0 = utils.mod(utils.poly_round(scale * temp), Q, POLY_MOD)

        temp = self.ct0 * ciphertext.ct1 + self.ct1 * ciphertext.ct0
        res1 = utils.mod(utils.poly_round(scale * temp), Q, POLY_MOD)

        temp = self.ct1 * ciphertext.ct1
        res2 = utils.mod(utils.poly_round(scale * temp), Q, POLY_MOD)
        decomposed_res2 = self.__base_decompose(res2)
        res_0 = utils.mod(
            res0 + sum(self.rlks[i][0] * decomposed_res2[i] for i in range(d + 1)), Q, POLY_MOD)
        res_1 = utils.mod(
            res1 + sum(self.rlks[i][1] * decomposed_res2[i] for i in range(d + 1)), Q, POLY_MOD)
        return CipherText(res_0, res_1, self.pk0, self.pk1, self.rlks)

    def __plain_power(self, pt):
        if (pt == 0):
            raise Exception("Have not added support for x^0 = 1 yet")
        else:
            res = self
            for i in range(pt-1):
                res = res*self
            return res

    def __add__(self, other):
        if (isinstance(other, int)):
            return self.__plain_add(other)
        elif (isinstance(other, CipherText)):
            if (self.pk0 != other.pk0 or self.pk1 != other.pk1):
                raise Exception(
                    "You can only add ciphertexts encrypted by same key!!")
            else:
                return self.__cipher_add(other)
        else:
            raise Exception("Unkown Type!!")

    def __sub__(self, other):
        if (isinstance(other, int)):
            return self.__plain_add(0-other)
        elif (isinstance(other, CipherText)):
            if (self.pk0 != other.pk0 or self.pk1 != other.pk1):
                raise Exception(
                    "You can only subtract ciphertexts encrypted by same key!!")
            else:
                return self.__cipher_sub(other)
        else:
            raise Exception("Unkown Type!!")

    def __mul__(self, other):
        if (isinstance(other, int)):
            return self.__plain_multiply(other)
        elif (isinstance(other, CipherText)):
            if (self.pk0 != other.pk0 or self.pk1 != other.pk1):
                raise Exception(
                    "You can only multiply ciphertexts encrypted by same key!!")
            else:
                return self.__cipher_multiply(other)
        else:
            raise Exception("Unkown Type!!")

    def __pow__(self, other):
        if (isinstance(other, int)):
            return self.__plain_power(other)
        else:
            raise Exception("You can only power ciphertext with plaintext")

    def __floordiv__(self, other):
        if (isinstance(other, int)):
            return self.__plain_divide(other)
        else:
            raise Exception("You can only divide ciphertext with plaintext")

    def __str__(self):
        return str(self.ct0)+' '+str(self.ct1)


# Implemenation
if __name__ == '__main__':
    fv12 = FV12()
    public_key, private_key = fv12.generate_keys()
    print("Enter your equation:")
    while (True):
        print(">> ", end="")
        eq = input()
        eq = eq.replace(" ", "")
        conversion = utils.Conversion(len(eq))
        postfix_eq = conversion.infixToPostfix(eq)

        stack = []
        i = 0

        for i in range(len(postfix_eq)):
            if (postfix_eq[i].isdigit()):
                postfix_eq[i] = public_key.encrypt(int(postfix_eq[i]))
        i = 0
        first = 0
        while i < len(postfix_eq):

            if (isinstance(postfix_eq[i], CipherText)):
                stack.append(postfix_eq[i])

            else:
                op = postfix_eq[i]
                b = stack.pop()
                a = stack.pop()
                if (op == '+'):
                    stack.append(a+b)
                elif (op == '-'):
                    stack.append(a-b)
                elif (op == '*'):
                    stack.append(a*b)
                elif (op == '^'):
                    b = private_key.decrypt(b)
                    stack.append(a**b)
                elif (op == '/'):
                    b = private_key.decrypt(b)
                    stack.append(a//b)
                else:
                    print('Operation Not Supported')
                    break
            i += 1
        print(private_key.decrypt(stack.pop()))
