import numpy as np
from math import floor , log
from random import choice
import random 
def binary_poly(size):
  # Generates polynomial with coefficients randomly between [0 , 1]
  # (size - 1) ---> degree of the polynomial

  return np.poly1d(np.random.randint(-1 , 2 , size).astype(int))

def integer_poly(size , modulus):

  #Generates a polynomial with integral coefficients between [0 , modulus]
  # (size - 1) ---> degree of the polynomial

  return np.poly1d(np.random.randint(0 , modulus , size,dtype=np.int64) % modulus)
print(integer_poly(19,2))
def normal_poly(size , modulus):

  # Generates a polynomial with coefficent from a normal distribution of mean 0
  # and standard deviation of 2
  # (size - 1) ---> degree of the polynomial
  mean = 0
  std = 3.2
  return np.poly1d(np.random.normal(mean , std , size).astype(int) % modulus)

def mod(polynomial , modulus  , poly_mod):
  # To ensure coefficients of the polynomial between [0 , modulus]
  # Also (polynomial)mod(poly_mod) i.e. r in polynomial = a * poly_mod + r

  remainder = np.floor(np.polydiv(polynomial , poly_mod)[1])
  return np.poly1d(remainder % modulus)

class Conversion:

	# Constructor to initialize the class variables
	def __init__(self, capacity):
		self.top = -1
		self.capacity = capacity
		
		# This array is used a stack
		self.array = []
		
		# Precedence setting
		self.output = []
		self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

	# Check if the stack is empty
	def isEmpty(self):
		return True if self.top == -1 else False

	# Return the value of the top of the stack
	def peek(self):
		return self.array[-1]

	# Pop the element from the stack
	def pop(self):
		if not self.isEmpty():
			self.top -= 1
			return self.array.pop()
		else:
			return "$"

	# Push the element to the stack
	def push(self, op):
		self.top += 1
		self.array.append(op)

	# A utility function to check is the given character
	# is operand
	def isOperand(self, ch):
		return ch.isdigit()

	# Check if the precedence of operator is strictly
	# less than top of stack or not
	def notGreater(self, i):
		try:
			a = self.precedence[i]
			b = self.precedence[self.peek()]
			return True if a <= b else False
		except KeyError:
			return False

	# The main function that
	# converts given infix expression
	# to postfix expression
	def infixToPostfix(self, exp):

		# Iterate over the expression for conversion
		i=0
		while i < len(exp):
			num=''
			while(i<len(exp) and exp[i].isdigit()):
				num+=exp[i]
				i+=1
			self.output.append(num)
			# If the character is an '(', push it to stack
			if i<len(exp) and exp[i] == '(':
				self.push(exp[i])
			elif i<len(exp) and exp[i] == ')':
				while((not self.isEmpty()) and
					self.peek() != '('):
					a = self.pop()
					self.output.append(a)
				if (not self.isEmpty() and self.peek() != '('):
					return -1
				else:
					self.pop()
			elif i<len(exp):
				while(not self.isEmpty() and self.notGreater(exp[i])):
					self.output.append(self.pop())
				self.push(exp[i])
			i+=1
		while not self.isEmpty():
			self.output.append(self.pop())
		
		return self.output

first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
					31, 37, 41, 43, 47, 53, 59, 61, 67,
					71, 73, 79, 83, 89, 97, 101, 103,
					107, 109, 113, 127, 131, 137, 139,
					149, 151, 157, 163, 167, 173, 179,
					181, 191, 193, 197, 199, 211, 223,
					227, 229, 233, 239, 241, 251, 257,
					263, 269, 271, 277, 281, 283, 293,
					307, 311, 313, 317, 331, 337, 347, 349]

def nBitRandom(n_bits):
	return random.randrange(2**(n_bits-1)+1, 2**n_bits - 1)


def getLowLevelPrime(n_bits):
	'''Generate a prime candidate divisible 
	by first primes'''
	while True:
		# Obtain a random number
		pc = nBitRandom(n_bits)

		# Test divisibility by pre-generated
		# primes
		for divisor in first_primes_list:
			if pc % divisor == 0 and divisor**2 <= pc:
				break
		else:
			return pc


def isMillerRabinPassed(mrc):
	'''Run 20 iterations of Rabin Miller Primality test'''
	maxDivisionsByTwo = 0
	ec = mrc-1
	while ec % 2 == 0:
		ec >>= 1
		maxDivisionsByTwo += 1
	assert(2**maxDivisionsByTwo * ec == mrc-1)

	def trialComposite(round_tester):
		if pow(round_tester, ec, mrc) == 1:
			return False
		for i in range(maxDivisionsByTwo):
			if pow(round_tester, 2**i * ec, mrc) == mrc-1:
				return False
		return True

	# Set number of trials here
	numberOfRabinTrials = 20
	for i in range(numberOfRabinTrials):
		round_tester = random.randrange(2, mrc)
		if trialComposite(round_tester):
			return False
	return True


def large_prime(n_bits):
	while True:
		prime_candidate = getLowLevelPrime(n_bits)
		if not isMillerRabinPassed(prime_candidate):
			continue
		else:
			return prime_candidate
def get_coefficient_modulus(n_bits):
    temp=n_bits//3
    return large_prime(temp)*large_prime(temp)*large_prime(temp)
def modInverse(A, M):
    m0 = M
    y = 0
    x = 1
 
    if (M == 1):
        return 0
 
    while (A > 1):
 
        # q is quotient
        q = A // M
 
        t = M
 
        # m is remainder now, process
        # same as Euclid's algo
        M = A % M
        A = t
        t = y
 
        # Update x and y
        y = x - q * y
        x = t
 
    # Make x positive
    if (x < 0):
        x = x + m0
 
    return x
