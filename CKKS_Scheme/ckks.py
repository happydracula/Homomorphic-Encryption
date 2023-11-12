import sys

sys.path.insert(0, '../utils')
from poly import Polynomial
from math import floor, log
from joblib import Parallel, delayed
import importlib
from plaintext import Plaintext
from random import choice
import utils as utils



class Params:
    def __init__(self, N, Q, big_mod):
        self. N = N
        self.Q = Q
        self.big_mod = big_mod
        self.POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])
        print('Initialised')


class CKKS:
    def __init__(self, params):
        self.params = params

    def generate_keys(self):
        sk = utils.sample_hamming_weight_vector(
            self.params.N, self.params.N//4)
        mod = self.params.big_mod
        a = utils.sample_uniform(0, mod, self.params.N)
        e = utils.sample_triangle(self.params.N)
        pk0 = utils.mod(-(a*sk) + e, mod, self.params.POLY_MOD)
        pk1 = a
        sk_squared = utils.mod(sk*sk, mod, self.params.POLY_MOD)
        mod_squared = mod**2
        swk_coeff = utils.sample_uniform(0, mod_squared, self.params.N)
        swk_error = utils.sample_triangle(self.params.N)
        sw0 = utils.mod(-(swk_coeff*sk)+swk_error,
                        mod_squared, self.params.POLY_MOD)
        temp = utils.mod(sk_squared*mod, mod_squared, self.params.POLY_MOD)
        sw0 = utils.mod(sw0+temp, mod_squared, self.params.POLY_MOD)
        sw1 = swk_coeff
        return PublicKey(pk0, pk1, sw0, sw1, self.params), PrivateKey(sk, self.params)


class PublicKey:
    def __init__(self, pk0, pk1, sw0, sw1, params):
        self.pk0 = pk0
        self.pk1 = pk1
        self.sw0 = sw0
        self.sw1 = sw1
        self.params = params

    def encrypt(self, pt):

        u = utils.sample_triangle(self.params.N)
        e1 = utils.sample_triangle(self.params.N)
        e2 = utils.sample_triangle(self.params.N)

        c0 = utils.mod((self.pk0 * u) + e1 +
                       pt.poly, self.params.Q, self.params.POLY_MOD)
        c1 = utils.mod((self.pk1 * u) + e2,
                       self.params.Q, self.params.POLY_MOD)
        c0 = utils.small_mod(c0, self.params.Q)
        c1 = utils.small_mod(c1, self.params.Q)
        return CipherText(c0, c1, self.sw0, self.sw1, pt.scale, self.params.Q, self.params)


class PrivateKey:
    def __init__(self, sk, params):
        self.sk = sk
        self.params = params

    def decrypt(self, ciphertext):
        pt = utils.mod(ciphertext.ct0 + ciphertext.ct1 *
                       self.sk, ciphertext.modulus, self.params.POLY_MOD)
        # print(pt)
        return Plaintext(utils.small_mod(pt, ciphertext.modulus), ciphertext.scale)


class CipherText:

    def __init__(self, ct0, ct1, sw0, sw1, scale, modulus, params):
        self.ct0 = ct0
        self.ct1 = ct1
        self.sw0 = sw0
        self.sw1 = sw1
        self.scale = scale
        self.modulus = modulus
        self.params = params

    def __plain_add(self, pt):
        if (self.scale != pt.scale):
            raise Exception("Differenct scaling factors!!")
        res0 = utils.mod(
            (self.ct0 + pt.poly), self.modulus, self.params.POLY_MOD)
        res0 = utils.small_mod(res0, self.modulus)
        return CipherText(res0, self.ct1, self.sw0, self.sw1, self.scale, self.modulus, self.params)

    def __cipher_add(self, ciphertext):
        if (self.scale != ciphertext.scale):
            raise Exception("Differenct scaling factors!!")
        if (self.modulus != ciphertext.modulus):
            raise Exception("Differenct moduli!!")
        res0 = utils.mod(self.ct0 + ciphertext.ct0,
                         self.modulus, self.params.POLY_MOD)
        res0 = utils.small_mod(res0, self.modulus)
        res1 = utils.mod(self.ct1 + ciphertext.ct1,
                         self.modulus, self.params.POLY_MOD)
        res1 = utils.small_mod(res1, self.modulus)
        return CipherText(res0, res1, self.sw0, self.sw1, self.scale, self.modulus, self.params)

    def __cipher_sub(self, ciphertext):
        if (self.scale != ciphertext.scale):
            raise Exception("Differenct scaling factors!!")
        if (self.modulus != ciphertext.modulus):
            raise Exception("Differenct moduli!!")
        res0 = utils.mod(self.ct0 - ciphertext.ct0,
                         self.modulus, self.params.POLY_MOD)
        res1 = utils.mod(self.ct1 - ciphertext.ct1,
                         self.modulus, self.params.POLY_MOD)
        res0 = utils.small_mod(res0, self.modulus)
        res1 = utils.small_mod(res1, self.modulus)
        return CipherText(res0, res1, self.sw0, self.sw1, self.scale, self.modulus, self.params)

    def __plain_multiply(self, pt):

        res0 = utils.mod(
            (self.ct0 * pt.poly), self.modulus, self.params.POLY_MOD)
        res0 = utils.small_mod(res0, self.modulus)
        res1 = utils.mod(
            (self.ct1 * pt.poly), self.modulus, self.params.POLY_MOD)
        res1 = utils.small_mod(res1, self.modulus)
        temp = CipherText(res0, res1, self.sw0, self.sw1, self.scale *
                          pt.scale, self.modulus, self.params)
        return self.rescale(temp, self.scale)

    def __cipher_multiply(self, ciphertext):
        if self.modulus != ciphertext.modulus:
            raise Exception("Unequal modulus while multiplication")

        res0 = utils.mod((self.ct0 * ciphertext.ct0),
                         self.modulus, self.params.POLY_MOD)
        res0 = utils.small_mod(res0, self.modulus)
        res1 = utils.mod((self.ct0 * ciphertext.ct1 + self.ct1 * ciphertext.ct0),
                         self.modulus, self.params.POLY_MOD)
        res1 = utils.small_mod(res1, self.modulus)
        res2 = utils.mod((self.ct1 * ciphertext.ct1),
                         self.modulus, self.params.POLY_MOD)
        res2 = utils.small_mod(res2, self.modulus)
        temp = self.relinearize(self.sw0, self.sw1, res0, res1,
                                res2, self.scale * ciphertext.scale, self.modulus)
        return self.rescale(temp, self.scale)

    def relinearize(self, sw0, sw1, res0, res1, res2, new_scale, modulus):
        new_res0 = utils.mod(sw0*res2, modulus *
                             self.params.big_mod, self.params.POLY_MOD)
        new_res0 = utils.small_mod(new_res0, modulus*self.params.big_mod)
        new_res0 = new_res0//self.params.big_mod
        new_res0 = utils.mod(new_res0+res0, modulus, self.params.POLY_MOD)
        new_res0 = utils.small_mod(new_res0, modulus)

        new_res1 = utils.mod(sw1*res2, modulus *
                             self.params.big_mod, self.params.POLY_MOD)
        new_res1 = utils.small_mod(new_res1, modulus*self.params.big_mod)
        new_res1 = new_res1//self.params.big_mod
        new_res1 = utils.mod(new_res1+res1, modulus, self.params.POLY_MOD)
        new_res1 = utils.small_mod(new_res1, modulus)
        return CipherText(new_res0, new_res1, sw0, sw1, new_scale, modulus, self.params)

    def rescale(self, ciphertext, scale):
        c0 = ciphertext.ct0//scale
        c1 = ciphertext.ct1//scale
        return CipherText(c0, c1, ciphertext.sw0, ciphertext.sw1, ciphertext.scale//scale, ciphertext.modulus//scale, ciphertext.params)

    def __plain_power(self, pt):
        if (pt == 0):
            raise Exception("Have not added support for x^0 = 1 yet")
        else:
            res = self
            for i in range(pt-1):
                res = res*self
            return res

    def __add__(self, other):
        if (isinstance(other, Plaintext)):
            return self.__plain_add(other)
        elif (isinstance(other, CipherText)):
            if (self.sw0 != other.sw0 or self.sw1 != other.sw1):
                raise Exception(
                    "You can only add ciphertexts encrypted by same key!!")
            else:
                return self.__cipher_add(other)
        else:
            raise Exception('Unkown Type!')

    def __sub__(self, other):
        if (isinstance(other, Plaintext)):
            return self.__plain_add(-other)
        elif (isinstance(other, CipherText)):
            if (self.sw0 != other.sw0 or self.sw1 != other.sw1):
                raise Exception(
                    "You can only subtract ciphertexts encrypted by same key!!")
            else:
                return self.__cipher_sub(other)
        else:
            raise Exception('Unkown Type!')

    def __mul__(self, other):
        if (isinstance(other, Plaintext)):
            return self.__plain_multiply(other)
        elif (isinstance(other, CipherText)):
            if (self.sw0 != other.sw0 or self.sw1 != other.sw1):
                raise Exception(
                    "You can only multiply ciphertexts encrypted by same key!!")
            else:
                return self.__cipher_multiply(other)
        else:
            raise Exception("Unkown Type!!"+str(type(other)))

    def __rmul__(self, other):
        return self*other

    def __radd__(self, other):
        return self+other

    def __rsub__(self, other):
        return self-other

    def __pow__(self, other):
        if (isinstance(other, int)):
            return self.__plain_power(other)
        else:
            raise Exception("You can only power ciphertext with plaintext")

    def __str__(self):
        return str(self.ct0)+' '+str(self.ct1)


# if __name__ == '__main__':
#     params = Params(128, 32, 4293918721, 2**218)
#     fv12 = FV12(params)
#     public_key, private_key = fv12.generate_keys()

#     print("Enter your equation:")
#     while (True):
#         print(">> ", end="")
#         eq = input()
#         eq = eq.replace(" ", "")
#         conversion = utils.Conversion(len(eq))
#         postfix_eq = conversion.infixToPostfix(eq)

#         stack = []
#         i = 0

#         for i in range(len(postfix_eq)):
#             if (postfix_eq[i].isdigit()):
#                 postfix_eq[i] = public_key.encrypt(int(postfix_eq[i]))
#         i = 0
#         first = 0
#         while i < len(postfix_eq):

#             if (isinstance(postfix_eq[i], CipherText)):
#                 stack.append(postfix_eq[i])

#             else:
#                 op = postfix_eq[i]
#                 b = stack.pop()
#                 a = stack.pop()
#                 if (op == '+'):
#                     stack.append(a+b)
#                 elif (op == '-'):
#                     stack.append(a-b)
#                 elif (op == '*'):
#                     stack.append(a*b)
#                 elif (op == '^'):
#                     b = private_key.decrypt(b)
#                     stack.append(a**b)
#                 elif (op == '/'):
#                     b = private_key.decrypt(b)
#                     stack.append(a//b)
#                 else:
#                     print('Operation Not Supported')
#                     break
#             i += 1
#         print(private_key.decrypt(stack.pop()))
