
from CKKS_Scheme.ckks import CKKS, Params, CipherText
import numpy as np
from random import choice
from utils.plaintext import Plaintext
import importlib
from joblib import Parallel, delayed
from CKKS_Scheme.ckks_encoder import CKKSEncoder
from math import floor, log
from utils.poly import Polynomial
import utils.utils as utils



def encode_value(a, scale):
    encoder = CKKSEncoder(16, scale)
    a_encoded = encoder.encode(np.array([a]*4))
    a_encoded = Polynomial(a_encoded.coef)
    a_encoded.poly_floor()
    a_pt = Plaintext(a_encoded, scale)
    return a_pt

    
if __name__ == '__main__':
    scale=1<<20
    params = Params(8,  1 << 600, 1 << 1200,do_rescale=True)
    ckks = CKKS(params)
    public_key, private_key = ckks.generate_keys()
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
                temp=encode_value(float(postfix_eq[i]),scale)
                postfix_eq[i] = public_key.encrypt(temp)
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
        res=stack.pop()
        pt_dash=private_key.decrypt(res)
        pt=np.polynomial.Polynomial(pt_dash.poly.convert_to_list())
        encoder=CKKSEncoder(16,pt_dash.scale)
        pt=encoder.decode(pt)
        print(pt[0].real)
