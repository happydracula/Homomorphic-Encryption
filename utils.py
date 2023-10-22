
import numpy as np
from math import floor , log
from random import choice

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