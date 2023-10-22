import numpy as np
from math import floor , log
from random import choice
import utils
# Polynomial Genaration Part

N=2**4
RT=2
T=2**21
Q=2**63
POLY_MOD=np.poly1d([1] + ([0] * (N-1) ) + [1])


class FV12:
  
    def generate_keys(self):
      sk=utils.binary_poly(N)
      a = utils.integer_poly(N , Q)
      e = utils.normal_poly(N , Q)
      pk0 = utils.mod(-(a*sk) + e , Q , POLY_MOD)
      pk1 = a
      d = floor(log(Q , RT))
      rlks = []
      for i in range(d + 1):
        a = utils.integer_poly(N , Q)
        e = utils.normal_poly(N , Q)
        rlk0 = utils.mod(-(a*sk) + e + ((RT**i) * (sk**2)) , Q , POLY_MOD)
        rlk1 = a
        rlks.append((rlk0 , rlk1))
      return PublicKey(pk0,pk1,rlks),PrivateKey(sk)
  
class PublicKey:
  def __init__(self,pk0,pk1,rlks):
    self.pk0=pk0
    self.pk1=pk1
    self.rlks=rlks
    
  def encrypt(self,pt):
    delta = Q // T
    u = utils.binary_poly(N)
    e1 = utils.normal_poly(N , Q)
    e2 = utils.normal_poly(N , Q)

    c0 = utils.mod((self.pk0 * u) + e1 + (delta * pt) , Q , POLY_MOD)
    c1 = utils.mod((self.pk1 * u) + e2 , Q , POLY_MOD)

    return CipherText(c0 , c1,self.pk0,self.pk1,self.rlks)
    
class PrivateKey:
  def __init__(self,sk):
    self.sk=sk
  
  def decrypt(self,ciphertext):
    scale = T/ Q
    temp = utils.mod(ciphertext.ct0 + ciphertext.ct1 * self.sk , Q , POLY_MOD)
    pt=np.poly1d((np.round(scale * temp) % T).astype(int))[0]
    return ((pt+(T//2))%T)-(T//2)
    

class CipherText: 
  
  def __init__(self,ct0,ct1,pk0,pk1,rlks):
    self.ct0=ct0
    self.ct1=ct1
    self.pk0=pk0
    self.pk1=pk1
    self.rlks=rlks
  
  def __base_decompose(self,polynomial):
  # To fetch the power of T used and create an array of

    d = floor(log(Q , RT))

    result = []
    for i in range(d + 1):
      poly = np.poly1d(np.floor(polynomial / RT ** i).astype(int) % RT)
      result.append(poly)

    return np.array(result)

  def __plain_add(self , pt):

    delta = Q // T
    m = delta * pt    # scaled_pt
    res0 = utils.mod((self.ct0 + m) , Q , POLY_MOD)
    return CipherText(res0 , self.ct1,self.pk0,self.pk1,self.rlks)
  
  def __plain_multiply(self,pt):

    res0 = utils.mod((self.ct0 * pt) , Q , POLY_MOD)
    res1 = utils.mod((self.ct1 * pt) , Q , POLY_MOD)

    return CipherText(res0 , res1,self.pk0,self.pk1,self.rlks)
  def __cipher_add(self,ciphertext):

    res0 = utils.mod(self.ct0 + ciphertext.ct0 ,Q ,POLY_MOD)
    res1 = utils.mod(self.ct1 +ciphertext.ct1 ,Q ,POLY_MOD)
    return CipherText(res0 , res1,self.pk0,self.pk1,self.rlks)
  
  def __cipher_sub(self,ciphertext):

    res0 = utils.mod(self.ct0 - ciphertext.ct0 ,Q ,POLY_MOD)
    res1 = utils.mod(self.ct1 - ciphertext.ct1 ,Q ,POLY_MOD)
    return CipherText(res0 , res1,self.pk0,self.pk1,self.rlks)
  
  def __cipher_multiply(self , ciphertext):

    d = floor(log(Q , RT))
    scale = T / Q
    temp = self.ct0 * ciphertext.ct0
    res0 = utils.mod(np.round(scale * temp) , Q , POLY_MOD)

    temp = self.ct0 * ciphertext.ct1 + self.ct1 * ciphertext.ct0
    res1 = utils.mod(np.round(scale * temp) , Q , POLY_MOD)

    temp = self.ct1 * ciphertext.ct1
    res2 = utils.mod(np.round(scale * temp) , Q , POLY_MOD)
    decomposed_res2 = self.__base_decompose(res2)
    res_0 = utils.mod(res0 + sum(self.rlks[i][0] * decomposed_res2[i] for i in range(d + 1)) , Q , POLY_MOD)
    res_1 = utils.mod(res1 + sum(self.rlks[i][1] * decomposed_res2[i] for i in range(d + 1)) , Q , POLY_MOD)
    return CipherText(res_0 , res_1,self.pk0,self.pk1,self.rlks)

  def __add__ (self,other):
        if(isinstance(other,int)):
            return self.__plain_add(other)
        elif(isinstance(other,CipherText)):
            if(self.pk0!=other.pk0 or self.pk1!=other.pk1):
              raise Exception("You can only add ciphertexts encrypted by same key!!")
            else:
              return self.__cipher_add(other)
        else:
            raise Exception("Unkown Type!!")
  def __sub__(self,other):
       if(isinstance(other,int)):
            return self.__plain_add(0-other)
       elif(isinstance(other,CipherText)):
            if(self.pk0!=other.pk0 or self.pk1!=other.pk1):
              raise Exception("You can only subtract ciphertexts encrypted by same key!!")
            else:
              return self.__cipher_sub(other)
       else:
            raise Exception("Unkown Type!!")
  def __mul__(self,other):
       if(isinstance(other,int)):
            return self.__plain_multiply(other)
       elif(isinstance(other,CipherText)):
            if(self.pk0!=other.pk0 or self.pk1!=other.pk1):
              raise Exception("You can only multiply ciphertexts encrypted by same key!!")
            else:
              return self.__cipher_multiply(other)
       else:
            raise Exception("Unkown Type!!")
  def __str__(self):
    return str(self.ct0)+' '+str(self.ct1)
#######################################################
# Implemenation
if __name__=='__main__':
  fv12=FV12()
  public_key,private_key=fv12.generate_keys()
  print("Enter your equation:")
  while(True):
        print(">> ",end="")
        eq=input()
        eq=eq.replace(" ","")
        conversion=utils.Conversion(len(eq))
        postfix_eq=conversion.infixToPostfix(eq)
        print(postfix_eq)
        stack=[]
        i=0
        while i in range(len(postfix_eq)):
            if(postfix_eq[i].isdigit()):
                stack.append(postfix_eq[i])
            else:
                op=postfix_eq[i]
                b=int(stack.pop())
                a=int(stack.pop())
                if(op=='+'):
                    a_encrypted=public_key.encrypt(a)
                    b_encrypted=public_key.encrypt(b)
                    c_encrypted=a_encrypted+b_encrypted
                    stack.append(private_key.decrypt(c_encrypted))
                elif(op=='-'):
                    a_encrypted=public_key.encrypt(a)
                    b_encrypted=public_key.encrypt(b)
                    c_encrypted=a_encrypted-b_encrypted
                    stack.append(private_key.decrypt(c_encrypted))
                elif(op=='*'):
                    a_encrypted=public_key.encrypt(a)
                    b_encrypted=public_key.encrypt(b)
                    c_encrypted=a_encrypted*b_encrypted
                    stack.append(private_key.decrypt(c_encrypted))

                else:
                    print('Operation Not Supported')
                    break
            i+=1
        print(stack.pop())
  