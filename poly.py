import math
import random
class Polynomial():
    def __init__(self,arr):
        self.poly={}
        for i in range(len(arr)):
            if(arr[i]!=0):
                self.poly[i]=arr[i]
                self.degree=i
    def __add__(self,other):
        if(isinstance(other,int)):
            if(0 in self.poly):
                self.deg[0]+=other
            else:
                self.deg[0]=other
            return self
        elif(isinstance(other,Polynomial)):
            for deg, coeff in other.poly.items():
                if(deg in self.poly):
                    self.poly[deg]+=coeff
                else:
                    self.poly[deg]=coeff
            return self
        else:
            raise Exception('Invalid Data Type')

    def __sub__(self,other):
         if(isinstance(other,int)):
            if(0 in self.poly):
                self.deg[0]-=other
            else:
                self.deg[0]=(-other)
            return self
         elif(isinstance(other,Polynomial)):
            for deg, coeff in other.poly.items():
                if(deg in self.poly):
                    self.poly[deg]-=coeff
                else:
                    self.poly[deg]=(-coeff)
            return self
         else:
            raise Exception('Invalid Data Type')
    def polydiv(self,other):
        pass
    def __mul__(self,other):
        if(not isinstance(other,Polynomial)):
            for key in self.poly.keys():
                self.poly[key]*=other
            return self
        else:  
            res=Polynomial([])
            for a in self.poly.items():
                for b in other.poly.items():
                    coeff=a[1]*b[1]
                    power=a[0]+b[0]
                    if(power in res.poly):
                        res.poly[power]+=coeff
                    else:
                         res.poly[power]=coeff
            return res
            
    def __str__(self):
        res=''
        for item in self.poly.items():
            if(item[0])==0:
                 res+=str(item[1])+' + '
            else:
                res+=str(item[1])+' x^'+str(item[0])+' + '
        return res[:-2]

a=[1,2]
b=[3,-4,7]

a=Polynomial(a)
b=Polynomial(b)
print(a)
print(b)
print(a+b)
            
            