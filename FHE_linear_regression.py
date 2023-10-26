import pandas as pd
from fhe import FV12
fv12 = FV12()
public_key, private_key = fv12.generate_keys()
weights = [106]
b = 131
x = [1]
encrypted_x = [public_key.encrypt(i) for i in x]
pred = public_key.encrypt(0)
for i in range(len(weights)):
    pred += encrypted_x[i]*weights[i]
pred += b
print(pred)
print(private_key.decrypt(pred))
