from BFV_Scheme.bfv import Params,FV12,CipherText
import utils.utils as utils

if __name__ == '__main__':
    params = Params(2**4, 2, 2**21, 2**63)
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
