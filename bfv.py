
from math import floor, log
from joblib import Parallel, delayed
from random import choice
import utils
import time
from poly import Polynomial
# Params Set 1
# N = 4096
# self.params.RT = 2
# T = 1024
# self.params.Q = 2**63
# self.params.POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])

# Params Set 2
# N = 1024
# RT = 4
# T = 2**21
# Q = 2**63
# POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])

# N = 1024
# RT = 16
# T = 65535
# Q = 2**312
# P = 2**90
# POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])


class Params:
    def __init__(self, N, RT, T, Q):
        self. N = N
        self.RT = RT
        self.T = T
        self.Q = Q
        self.POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])


class FV12:
    def __init__(self, params):
        self.params = params

    def generate_keys(self):
        sk = utils.binary_poly(self.params.N)
        a = utils.integer_poly(self.params.N, self.params.Q)
        e = utils.normal_poly(self.params.N)
        pk0 = utils.mod(-(a*sk) + e, self.params.Q, self.params.POLY_MOD)
        pk1 = a
        rlks = []
        d = floor(log(self.params.Q, self.params.RT))
        for i in range(d + 1):
            a = utils.integer_poly(self.params.N, self.params.Q)
            e = utils.normal_poly(self.params.N)
            rlk0 = utils.mod(-(a*sk) + e +
                             ((self.params.RT**i) * (sk*sk)), self.params.Q, self.params.POLY_MOD)
            rlk1 = a
            rlks.append((rlk0, rlk1))
        return PublicKey(pk0, pk1, rlks, self.params), PrivateKey(sk, self.params)


class PublicKey:
    def __init__(self, pk0, pk1, rlks, params):
        self.pk0 = pk0
        self.pk1 = pk1
        self.rlks = rlks
        self.params = params

    def encrypt(self, pt):
        delta = self.params.Q / self.params.T
        u = utils.binary_poly(self.params.N)
        e1 = utils.normal_poly(self.params.N)
        e2 = utils.normal_poly(self.params.N)

        c0 = utils.mod((self.pk0 * u) + e1 +
                       round(delta * pt), self.params.Q, self.params.POLY_MOD)
        c1 = utils.mod((self.pk1 * u) + e2,
                       self.params.Q, self.params.POLY_MOD)

        return CipherText(c0, c1, self.pk0, self.pk1, self.rlks, self.params)


class PrivateKey:
    def __init__(self, sk, params):
        self.sk = sk
        self.params = params

    def decrypt(self, ciphertext):
        scale = self.params.T / self.params.Q
        temp = utils.mod(ciphertext.ct0 + ciphertext.ct1 *
                         self.sk, self.params.Q, self.params.POLY_MOD)[0]

        pt = int((round(scale * temp) % self.params.T))
        return pt


class CipherText:

    def __init__(self, ct0, ct1, pk0, pk1, rlks, params):
        self.ct0 = ct0
        self.ct1 = ct1
        self.pk0 = pk0
        self.pk1 = pk1
        self.rlks = rlks
        self.params = params

    def __base_decompose(self, polynomial):
        # To fetch the power of T used and create an array of
        d = floor(log(self.params.Q, self.params.RT))

        result = []
        for i in range(d + 1):
            poly = utils.poly_floor(polynomial // (self.params.RT ** i))
            result.append(poly % self.params.RT)

        return result

    def __plain_add(self, pt):

        delta = self.params.Q // self.params.T
        m = delta * pt    # scaled_pt
        res0 = utils.mod(
            (self.ct0 + m), self.params.Q, self.params.POLY_MOD)
        return CipherText(res0, self.ct1, self.pk0, self.pk1, self.rlks, self.params)

    def __plain_multiply(self, pt):

        res0 = utils.mod(
            (self.ct0 * pt), self.params.Q, self.params.POLY_MOD)
        res1 = utils.mod(
            (self.ct1 * pt), self.params.Q, self.params.POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks, self.params)

    def __plain_divide(self, pt):
        res0 = utils.mod((self.ct0 * utils.modInverse(pt, self.params.T)),
                         self.params.Q, self.params.POLY_MOD)
        res1 = utils.mod((self.ct1 * utils.modInverse(pt, self.params.T)),
                         self.params.Q, self.params.POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks, self.params)

    def __cipher_add(self, ciphertext):

        res0 = utils.mod(self.ct0 + ciphertext.ct0,
                         self.params.Q, self.params.POLY_MOD)
        res1 = utils.mod(self.ct1 + ciphertext.ct1,
                         self.params.Q, self.params.POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks, self.params)

    def __cipher_sub(self, ciphertext):

        res0 = utils.mod(self.ct0 - ciphertext.ct0,
                         self.params.Q, self.params.POLY_MOD)
        res1 = utils.mod(self.ct1 - ciphertext.ct1,
                         self.params.Q, self.params.POLY_MOD)
        return CipherText(res0, res1, self.pk0, self.pk1, self.rlks, self.params)

    def mul_sum_polynomials(self, a, rlks_i, b, start, end):
        return sum(a[i][rlks_i]*b[i] for i in range(start, end))

    def __parallel_cipher_multiply(self, ciphertext):
        d = floor(log(self.params.Q, self.params.RT))
        scale = self.params.T / self.params.Q

        temp = self.ct0 * ciphertext.ct0
        res0 = utils.mod(utils.poly_round(scale * temp),
                         self.params.Q, self.params.POLY_MOD)
        temp = self.ct0 * ciphertext.ct1 + self.ct1 * ciphertext.ct0
        res1 = utils.mod(utils.poly_round(scale * temp),
                         self.params.Q, self.params.POLY_MOD)

        temp = self.ct1 * ciphertext.ct1
        res2 = utils.mod(utils.poly_round(scale * temp),
                         self.params.Q, self.params.POLY_MOD)
        decomposed_res2 = self.__base_decompose(res2)
        start = time.time()
        num_chunks = 8
        chunk_size = (d+1)//8
        temp = Parallel(n_jobs=num_chunks)(
            delayed(self.mul_sum_polynomials)(self.rlks, 0, decomposed_res2, start, min(d+1, start+chunk_size)) for start in range(0, d+1, chunk_size))
        temp = sum(temp)
        res_0 = utils.mod(
            res0 + temp, self.params.Q, self.params.POLY_MOD)
        temp = Parallel(n_jobs=num_chunks)(
            delayed(self.mul_sum_polynomials)(self.rlks, 1, decomposed_res2, start, min(d+1, start+chunk_size)) for start in range(0, d+1, chunk_size))
        temp = sum(temp)
        res_1 = utils.mod(
            res1 + temp, self.params.Q, self.params.POLY_MOD)
        end = time.time()
        print("The time of relinearisation is :",
              (end-start) * 10**3, "ms")

        return CipherText(res_0, res_1, self.pk0, self.pk1, self.rlks, self.params)

    def __cipher_multiply(self, ciphertext):
        d = floor(log(self.params.Q, self.params.RT))
        scale = self.params.T / self.params.Q
        temp = self.ct0 * ciphertext.ct0
        res0 = utils.mod(utils.poly_round(scale * temp),
                         self.params.Q, self.params.POLY_MOD)
        temp = self.ct0 * ciphertext.ct1 + self.ct1 * ciphertext.ct0
        res1 = utils.mod(utils.poly_round(scale * temp),
                         self.params.Q, self.params.POLY_MOD)

        temp = self.ct1 * ciphertext.ct1
        res2 = utils.mod(utils.poly_round(scale * temp),
                         self.params.Q, self.params.POLY_MOD)
        self.decomposed_res2 = self.__base_decompose(res2)
        start = time.time()
        res_0 = utils.mod(
            res0 + sum(self.rlks[i][0] * self.decomposed_res2[i] for i in range(d + 1)), self.params.Q, self.params.POLY_MOD)
        res_1 = utils.mod(
            res1 + sum(self.rlks[i][1] * self.decomposed_res2[i] for i in range(d + 1)), self.params.Q, self.params.POLY_MOD)
        end = time.time()
        print("The time of relinearisation is :",
              (end-start) * 10**3, "ms")

        return CipherText(res_0, res_1, self.pk0, self.pk1, self.rlks, self.params)

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
            raise Exception("Unknown Type!!")

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
                return self.__parallel_cipher_multiply(other)
        else:
            raise Exception("Unkown Type!!")

    def __rmul__(self, other):
        return self*other

    def __pow__(self, other):
        if (isinstance(other, int)):
            return self.__plain_power(other)
        else:
            raise Exception("You can only power ciphertext with plaintext")

    def __floordiv__(self, other):
        if (isinstance(other, int)):
            return self.__plain_divide(other)
        else:
            raise Exception(
                "You can only divide ciphertext with plaintext")

    def __str__(self):
        return str(self.ct0)+' '+str(self.ct1)


if __name__ == '__main__':
    params = Params(1024, 16, 1024, 2**63)
    fv12 = FV12(params)
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
