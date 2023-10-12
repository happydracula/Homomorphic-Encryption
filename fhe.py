import numpy as np
from math import floor , log
from random import choice

# Polynomial Genaration Part

def binary_poly(size):
  # Generates polynomial with coefficients randomly between [0 , 1]
  # (size - 1) ---> degree of the polynomial

  return np.poly1d(np.random.randint(0 , 2 , size).astype(int))

def integer_poly(size , modulus):

  #Generates a polynomial with integral coefficients between [0 , modulus]
  # (size - 1) ---> degree of the polynomial

  return np.poly1d(np.random.randint(0 , modulus , size , dtype = np.int64) % modulus)

def normal_poly(size , modulus):

  # Generates a polynomial with coefficent from a normal distribution of mean 0
  # and standard deviation of 2
  # (size - 1) ---> degree of the polynomial
  mean = 0
  std = 2
  return np.poly1d(np.random.normal(mean , std , size).astype(int) % modulus)

def base_decompose(polynomial , T , modulus):
  # To fetch the power of T used and create an array of 
  
  d = floor(log(modulus , T))

  result = []
  for i in range(d + 1):
    poly = np.poly1d(np.floor(polynomial / T ** i).astype(int) % T)
    result.append(poly)

  return np.array(result)


def mod(polynomial , modulus  , poly_mod):
  # To ensure coefficients of the polynomial between [0 , modulus]
  # Also (polynomial)mod(poly_mod) i.e. r in polynomial = a * poly_mod + r

  remainder = np.floor(np.polydiv(polynomial , poly_mod)[1])
  return np.poly1d(remainder % modulus)


def generate_secret_key(size):

  return binary_poly(size)

def generate_public_key(sk , size , modulus , poly_mod):
  #Generate the secret key and public key as a funtion of the secret key

  a = integer_poly(size , modulus)
  e = normal_poly(size , modulus)

  pk0 = mod(-(a*sk) + e , modulus , poly_mod)
  pk1 = a

  return pk0 , pk1


def generate_eval_key(sk , size , T , modulus , poly_mod):

  d = floor(log(modulus , T))
  rlks = []

  for i in range(d + 1):
    
    a = integer_poly(size , modulus)
    e = normal_poly(size , modulus)
    rlk0 = mod(-(a*sk) + e + ((T**i) * (sk**2)) , modulus , poly_mod)
    rlk1 = a
    rlks.append((rlk0 , rlk1))

  return rlks


def encrypt(pk , pt , size , t , modulus , poly_mod):

  delta = modulus // t
  u = binary_poly(size)
  e1 = normal_poly(size , modulus)
  e2 = normal_poly(size , modulus)

  c0 = mod((pk[0] * u) + e1 + (delta * pt) , modulus , poly_mod)
  c1 = mod((pk[1] * u) + e2 , modulus , poly_mod)

  return c0 , c1

def decrypt(sk , ct , t , modulus , poly_mod):

  scale = t / modulus
  temp = mod(ct[0] + ct[1] * sk , modulus , poly_mod)
  return np.poly1d((np.round(scale * temp) % t).astype(int))

## Methods to perform addtion and multiplication between two ciphertexts

def cipher_add(ct1 , ct2 , modulus , poly_mod):
  
  res0 = mod(ct1[0] + ct2[0] , modulus , poly_mod)
  res1 = mod(ct1[1] + ct2[1] , modulus , poly_mod)
  return res0 , res1

def cipher_multiply(rlks , ct1 , ct2 , t , T , modulus , poly_mod):

  d = floor(log(modulus , T))
  #Two phases :- Multiplication term wise and then relinearization

  scale = t / modulus
  temp = ct1[0] * ct2[0]
  res0 = mod(np.round(scale * temp) , modulus , poly_mod)

  temp = ct1[0] * ct2[1] + ct1[1] * ct2[0]
  res1 = mod(np.round(scale * temp) , modulus , poly_mod)

  temp = ct1[1] * ct2[1]
  res2 = mod(np.round(scale * temp) , modulus , poly_mod)

#  t_res = (res0 , res1 , res2)

  # Relinearization (Can make another fucntion for relinearization also)

  decomposed_res2 = base_decompose(res2 , T , modulus)
  res_0 = mod(res0 + sum(rlks[i][0] * decomposed_res2[i] for i in range(d + 1)) , modulus , poly_mod)
  res_1 = mod(res1 + sum(rlks[i][1] * decomposed_res2[i] for i in range(d + 1)) , modulus , poly_mod)

  return res_0 , res_1

# Methods to add and multiply plaint texts

def plain_add(ct , pt , t , modulus , poly_mod):

  delta = modulus // t
  m = delta * pt    # scaled_pt
  res0 = mod((ct[0] + m) , modulus , poly_mod)

  return (res0 , ct[1])

def plain_multiply(ct , pt , t , modulus , poly_mod):

  size = len(poly_mod) - 1

  res0 = mod((ct[0] * pt) , modulus , poly_mod)
  res1 = mod((ct[1] * pt) , modulus , poly_mod)

  return res0 , res1


#######################################################
# Implemenation

n = 2 ** 4
T = 2   # Base for relinearlization
t = 2 ** 15   # modulus for plain text
q = (2 ** 30) * t   # modulus for polynomial coefficients
poly_mod = np.poly1d([1] + ([0] * (n-1) ) + [1])

sk = generate_secret_key(n)
pk = generate_public_key(sk , n , q , poly_mod)
rlks = generate_eval_key(sk , n , T , q , poly_mod)

pt1 = 203
pt2 = 31
pt3 = 4

c1 = encrypt(pk , pt1 , n , t , q , poly_mod)
c2 = encrypt(pk , pt2 , n , t , q , poly_mod)
c3 = encrypt(pk , pt3 , n , t , q , poly_mod)

add_c1_pt2 = plain_add(c1 , pt2 , t , q , poly_mod)
mul_c1_pt3 = plain_multiply(c1 , pt3 , t , q , poly_mod)

add_c1_c2 = cipher_add(c1 , c2 , q , poly_mod)
mul_c1_c2 = cipher_multiply(rlks , c1 , c2 , t , T , q , poly_mod)

dct1 = decrypt(sk , add_c1_pt2 , t , q , poly_mod)
dct2 = decrypt(sk , mul_c1_pt3 , t , q , poly_mod)
dct3 = decrypt(sk , mul_c1_c2 , t , q , poly_mod)
dct4 = decrypt(sk , add_c1_c2 , t , q , poly_mod)

print(f"PlainText Addition :- {pt1} + {pt2} = {dct1[0]}")
print(f"PlainText Multiplication :- {pt1} * {pt3} = {dct2[0]}")
print(f"CipherText Multiplication :- {pt1} * {pt2} = {dct3[0]}")
print(f"CipherText Addition :- {pt1} + {pt2} = {dct4[0]}")
